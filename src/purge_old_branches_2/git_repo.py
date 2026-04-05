import subprocess
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CompletedProcess


def _datetime_at_utc(dt: datetime) -> datetime:
    return (
        dt.astimezone(timezone.utc)
        if dt.tzinfo is not None
        else dt.replace(tzinfo=timezone.utc)
    )


class GitRepo:
    def __init__(self, path: Path, prefix: str, target: str, days: int, remote: bool):
        self.path = path
        self.prefix = prefix
        self.target = target
        self.days = days
        self.remote = remote

    def get_branches_to_delete(self) -> set[str]:
        result = self._run_git_branch()
        now: datetime = datetime.now(timezone.utc)
        return self._parse_git_branch_output(now, result.stdout)

    def _run_git_branch(self) -> CompletedProcess[str]:
        args = [
            "git",
            "-C", self.path,
            "branch",
            "--list",
            "--no-color",
            "--format=%(authordate:iso8601-strict), %(committerdate:iso8601-strict), %(refname)",
        ]
        if self.remote:
            args.extend(["--remotes", "--merged", f"origin/{self.target}"])
        else:
            args.extend(["--merged", self.target])
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
        )
        return result

    def _parse_git_branch_output(self, now: datetime, stdout: str) -> set[str]:
        prefix = "refs/remotes/origin/" if self.remote else "refs/heads/"
        branches = set()
        for line in stdout.splitlines():
            raw_a, raw_c, raw_r = line.split(", ", maxsplit=2)
            authordate = _datetime_at_utc(datetime.fromisoformat(raw_a))
            committerdate = _datetime_at_utc(datetime.fromisoformat(raw_c))
            refname = raw_r.removeprefix(prefix)
            if ((now - authordate).days >= self.days
                    and (now - committerdate).days >= self.days
                    and refname.startswith(self.prefix)):
                branches.add(refname)
        return branches

    def delete_branches(self, branches: list[str]) -> None:
        batch_size = 10
        for i in range(0, len(branches), batch_size):
            batch = branches[i: i + batch_size]
            if self.remote:
                args = ["git", "-C", self.path, "push", "origin", "--delete"] + batch
            else:
                args = ["git", "-C", self.path, "branch", "--delete"] + batch
            subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=True,
            )
