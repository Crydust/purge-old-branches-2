import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from purge_old_branches_2.csv_parser import CsvParser


@dataclass(frozen=True)
class Arguments:
    csv_file: str
    csv_ticket_col: str
    csv_status_col: str
    csv_done_status: str
    repo: list[str]
    prefix: str
    target: str
    days: int
    dry_run: bool


def parse_arguments(args: list[str] | None = None) -> Arguments:
    parser = argparse.ArgumentParser(
        prog="purge_old_branches_2",
        description="Purge stale Git branches based on Jira ticket status and branch age."
    )
    parser.add_argument("--csv-file", type=str, required=True, help="Path to the CSV file containing ticket statuses.")
    parser.add_argument("--csv-ticket-col", type=str, required=True,
                        help="Column name of the ticket ID in the CSV file.")
    parser.add_argument("--csv-status-col", type=str, required=True,
                        help="Column name of the ticket status in the CSV file.")
    parser.add_argument("--csv-done-status", type=str, required=True,
                        help="Column value for 'Done' status in the CSV file.")
    parser.add_argument("--repo", type=str, nargs="+", required=True,
                        help="Path(s) to the repositor(y/ies) to purge branches from.")
    parser.add_argument("--prefix", type=str, default="BUG-", help="Prefix to filter branches by.")
    parser.add_argument("--target", type=str, default="main", help="Target branch to compare against.")
    parser.add_argument("--days", type=int, default=90, help="Number of days to consider a branch stale.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without deleting any branches.")
    return Arguments(**vars(parser.parse_args(args)))


def main(args: list[str] | None = None) -> int:
    arguments = parse_arguments(args)
    print(arguments)
    done_tickets = CsvParser(
        Path(arguments.csv_file),
        arguments.csv_ticket_col,
        arguments.csv_status_col,
        arguments.csv_done_status,
    ).done_tickets()
    print(done_tickets)

    return 0


if __name__ == "__main__":
    sys.exit(main())
