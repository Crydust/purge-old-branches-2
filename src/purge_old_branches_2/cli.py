import argparse
import re
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from operator import methodcaller
from pathlib import Path

from purge_old_branches_2.csv_parser import CsvParser
from purge_old_branches_2.git_repo import GitRepo


@dataclass(frozen=True)
class Arguments:
    csv_file: Path
    csv_ticket_col: str
    csv_status_col: str
    csv_done_status: str
    repo: list[Path]
    prefix: str
    target: str
    days: int
    remote: bool
    dry_run: bool


def _parse_arguments(args: list[str] | None = None) -> Arguments:
    parser = argparse.ArgumentParser(
        prog="purge_old_branches_2",
        description="Purge stale Git branches based on Jira ticket status and branch age."
    )
    parser.add_argument("--csv-file", type=Path, required=True, help="Path to the CSV file containing ticket statuses.")
    parser.add_argument("--csv-ticket-col", type=str, required=True,
                        help="Column name of the ticket ID in the CSV file.")
    parser.add_argument("--csv-status-col", type=str, required=True,
                        help="Column name of the ticket status in the CSV file.")
    parser.add_argument("--csv-done-status", type=str, required=True,
                        help="Column value for 'Done' status in the CSV file.")
    parser.add_argument("--repo", type=Path, nargs="+", required=True,
                        help="Path(s) to the repositor(y/ies) to purge branches from.")
    parser.add_argument("--prefix", type=str, default="BUG-", help="Prefix to filter branches by.")
    parser.add_argument("--target", type=str, default="main", help="Target branch to compare against.")
    parser.add_argument("--days", type=int, default=90, help="Number of days to consider a branch stale.")
    parser.add_argument("--remote", action="store_true", help="Delete remote instead of local branches.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without deleting any branches.")
    return Arguments(**vars(parser.parse_args(args)))


def _common_done_branches(
        prefix: str,
        branch_sets: list[set[str]],
        done_tickets: list[str]) -> list[str]:
    branches_to_delete = set.intersection(*branch_sets)
    pattern = re.compile(rf"^({re.escape(prefix)}[0-9]+).*$")
    branches_to_delete = [
        b for b in branches_to_delete
        if (m := pattern.fullmatch(b)) and m.group(1) in done_tickets
    ]

    def sort_key(branch: str) -> int:
        match = pattern.fullmatch(branch)
        if not match:
            raise ValueError(f"Branch '{branch}' does not match the expected format.")
        return int(match.group(1).removeprefix(prefix))

    branches_to_delete.sort(key=sort_key)
    return branches_to_delete


def main(args: list[str] | None = None) -> int:
    arguments = _parse_arguments(args)
    print(arguments)
    done_tickets = CsvParser(
        arguments.csv_file,
        arguments.csv_ticket_col,
        arguments.csv_status_col,
        arguments.csv_done_status,
        arguments.prefix,
    ).done_tickets()
    print(done_tickets)
    git_repos: list[GitRepo] = [GitRepo(
        repo_path,
        arguments.prefix,
        arguments.target,
        arguments.days,
        arguments.remote,
    ) for repo_path in arguments.repo]
    with ThreadPoolExecutor(max_workers=len(git_repos)) as executor:
        branch_sets = list(executor.map(methodcaller("get_branches_to_delete"), git_repos))
    branches_to_delete = _common_done_branches(
        arguments.prefix, branch_sets, done_tickets)
    print(branches_to_delete)
    if arguments.dry_run:
        print("Dry run: No branches will be deleted.")
        return 0
    with ThreadPoolExecutor(max_workers=len(git_repos)) as executor:
        list(executor.map(methodcaller("delete_branches", branches_to_delete), git_repos))
    return 0
