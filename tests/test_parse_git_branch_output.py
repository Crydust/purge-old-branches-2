from datetime import datetime
from pathlib import Path

from purge_old_branches_2.git_repo import GitRepo


def test_parse_git_branch_output(tmp_path: Path):
    git_repo = GitRepo(
        tmp_path,
        "foo-",
        "bar",
        5,
        False,
    )
    now = datetime.fromisoformat("1970-01-10T00:00:00Z")
    branches = git_repo._parse_git_branch_output(now, "\n".join([
        "1970-01-01T00:00:00Z ?sep? 1970-01-01T00:00:00Z ?sep? refs/heads/foo-1",
        "1970-01-10T00:00:00Z ?sep? 1970-01-01T00:00:00Z ?sep? refs/heads/foo-2",
        "1970-01-01T00:00:00Z ?sep? 1970-01-10T00:00:00Z ?sep? refs/heads/foo-3",
        "1970-01-10T00:00:00Z ?sep? 1970-01-10T00:00:00Z ?sep? refs/heads/foo-4",
        "1970-01-05T00:00:00Z ?sep? 1970-01-05T00:00:00Z ?sep? refs/heads/foo-5",
    ]))
    assert branches == {"foo-1", "foo-5"}