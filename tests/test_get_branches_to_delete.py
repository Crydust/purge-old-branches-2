import subprocess
import os
from pathlib import Path
from purge_old_branches_2.git_repo import GitRepo

def _run_git(cwd: Path, *args: str, env: dict | None = None):
    # Merge current environment with custom env if provided
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=full_env)

def test_get_branches_to_delete_integration(tmp_path: Path):
    # Setup repo
    repo_path = tmp_path / "stale_repo"
    repo_path.mkdir()
    _run_git(repo_path, "init", "-b", "main")
    _run_git(repo_path, "config", "user.email", "test@example.com")
    _run_git(repo_path, "config", "user.name", "Tester")

    # Initial commit (acts as the merge target)
    (repo_path / "base.txt").write_text("base")
    _run_git(repo_path, "add", ".")
    _run_git(repo_path, "commit", "-m", "initial")

    # 1. Create a STALE branch (merged)
    # 200 days ago
    stale_date = "2023-01-01T12:00:00Z"
    env = {"GIT_AUTHOR_DATE": stale_date, "GIT_COMMITTER_DATE": stale_date}

    _run_git(repo_path, "checkout", "-b", "BUG-1")
    (repo_path / "bug1.txt").write_text("fix")
    _run_git(repo_path, "add", ".")
    _run_git(repo_path, "commit", "-m", "old fix", env=env)
    _run_git(repo_path, "checkout", "main")
    _run_git(repo_path, "merge", "BUG-1")

    # 2. Create a RECENT branch (merged)
    # Today (default)
    _run_git(repo_path, "checkout", "-b", "BUG-2")
    (repo_path / "bug2.txt").write_text("new fix")
    _run_git(repo_path, "add", ".")
    _run_git(repo_path, "commit", "-m", "recent fix")
    _run_git(repo_path, "checkout", "main")
    _run_git(repo_path, "merge", "BUG-2")

    # 3. Create a STALE branch (NOT merged)
    _run_git(repo_path, "checkout", "-b", "BUG-3")
    (repo_path / "bug3.txt").write_text("unmerged")
    _run_git(repo_path, "add", ".")
    _run_git(repo_path, "commit", "-m", "stale unmerged", env=env)
    _run_git(repo_path, "checkout", "main")

    # Run the logic: look for BUG- branches older than 30 days
    repo = GitRepo(path=repo_path, prefix="BUG-", target="main", days=30, remote=False)
    branches = repo.get_branches_to_delete()

    # Assertions:
    # BUG-1: Merged and Stale -> Should be in set
    # BUG-2: Merged but Recent -> Should NOT be in set
    # BUG-3: Stale but Not Merged -> Should NOT be in set (git branch --merged filters it)
    assert "BUG-1" in branches
    assert "BUG-2" not in branches
    assert "BUG-3" not in branches
    assert len(branches) == 1