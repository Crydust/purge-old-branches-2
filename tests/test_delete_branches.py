import subprocess
from pathlib import Path
from purge_old_branches_2.git_repo import GitRepo

def _run_git(cwd: Path, *args: str):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

def test_delete_local_branches_integration(tmp_path: Path):
    # Initialize a real git repo
    repo_path = tmp_path / "local_repo"
    repo_path.mkdir()
    _run_git(repo_path, "init", "-b", "main")
    _run_git(repo_path, "config", "user.email", "test@example.com")
    _run_git(repo_path, "config", "user.name", "Tester")

    # Create a commit so main exists
    (repo_path / "file.txt").write_text("content")
    _run_git(repo_path, "add", ".")
    _run_git(repo_path, "commit", "-m", "initial")

    # Create branches to delete
    branches = ["BUG-1", "BUG-2"]
    for b in branches:
        _run_git(repo_path, "branch", b)

    # Verify branches exist
    result = subprocess.run(["git", "branch"], cwd=repo_path, capture_output=True, text=True)
    for b in branches:
        assert b in result.stdout

    # Execute deletion
    repo = GitRepo(path=repo_path, prefix="BUG-", target="main", days=0, remote=False)
    repo.delete_branches(branches)

    # Verify branches are gone
    result = subprocess.run(["git", "branch"], cwd=repo_path, capture_output=True, text=True)
    for b in branches:
        assert b not in result.stdout

def test_delete_remote_branches_integration(tmp_path: Path):
    # 1. Create a bare "remote" repo
    remote_path = tmp_path / "remote_repo.git"
    remote_path.mkdir()
    _run_git(remote_path, "init", "--bare", "-b", "main")

    # 2. Create a "local" repo to push branches from
    local_path = tmp_path / "local_clone"
    _run_git(tmp_path, "clone", str(remote_path), "local_clone")
    _run_git(local_path, "config", "user.email", "test@example.com")
    _run_git(local_path, "config", "user.name", "Tester")

    # Push main
    (local_path / "file.txt").write_text("content")
    _run_git(local_path, "add", ".")
    _run_git(local_path, "commit", "-m", "initial")
    _run_git(local_path, "push", "origin", "main")

    # 3. Create and push branches to the remote
    branches = ["BUG-remote-1", "BUG-remote-2"]
    for b in branches:
        _run_git(local_path, "branch", b)
        _run_git(local_path, "push", "origin", b)

    # 4. Verify remote branches exist
    result = subprocess.run(["git", "ls-remote", "--heads", "origin"], cwd=local_path, capture_output=True, text=True)
    for b in branches:
        assert b in result.stdout

    # 5. Execute remote deletion
    repo = GitRepo(path=local_path, prefix="BUG-", target="main", days=0, remote=True)
    repo.delete_branches(branches)

    # 6. Verify remote branches are gone
    result = subprocess.run(["git", "ls-remote", "--heads", "origin"], cwd=local_path, capture_output=True, text=True)
    for b in branches:
        assert b not in result.stdout