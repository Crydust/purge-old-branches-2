This review describes how the `GitRepo` class interacts with the Git CLI to identify and remove stale branches.

### Git Command Execution via `subprocess.run`

The class uses `subprocess.run` to execute Git commands. The following arguments are passed to configure the execution environment:

*   **`args`**: A list of strings where the first element is the executable (`git`) followed by its arguments. This prevents shell injection vulnerabilities.
*   **`-C <path>`**: This global Git option tells Git to run as if it were started in the specified directory instead of the current working directory.
*   **`capture_output=True`**: Redirects `stdout` and `stderr` so they can be processed by the Python script (e.g., parsing the branch list).
*   **`text=True`**: Returns the output as a `str` instead of `bytes`, using the default system encoding.
*   **`check=True`**: Ensures that if Git returns a non-zero exit code, a `CalledProcessError` is raised, preventing the script from proceeding with invalid data.

### Efficient Data Retrieval with `--format`

To determine if a branch is stale, the script needs the author date, committer date, and the branch name. Instead of running a separate command for every branch (which would be slow), it uses the `--format` flag in `git branch`:

```shell script
--format=%(authordate:iso8601-strict) ?sep? %(committerdate:iso8601-strict) ?sep? %(refname)
```


*   **One-Pass Retrieval**: This allows Git's internal engine to extract multiple pieces of metadata for every branch and print them in a single line.
*   **Custom Delimiter**: The use of `?sep?` creates a predictable structure that the script can reliably split using `line.split(" ?sep? ")`.
*   **Merged Filter**: By adding `--merged <target>`, Git only returns branches that have already been integrated into the main tracking branch, ensuring no unmerged work is lost.

### Local vs. Remote Deletion

The command for deleting a branch depends on whether it exists locally or on a remote server:

1.  **Local Branches**: Uses `git branch --delete <names>`. This targets the local `refs/heads/` namespace.
2.  **Remote Branches**: Uses `git push origin --delete <names>`. In Git, deleting a remote branch is technically a "push" operation where you instruct the remote server to remove a specific reference from its `refs/remotes/` namespace.

### Batching for Performance

The `delete_branches` method groups branch names into batches of 10.

*   **Reduced Overhead**: Every call to `subprocess.run` starts a new operating system process, which is "expensive" in terms of CPU and memory.
*   **Command Line Efficiency**: Git accepts multiple branch names as trailing arguments. By passing 10 branches at once (e.g., `git branch -d b1 b2 ... b10`), the script performs the same amount of work with 90% fewer subprocess starts compared to deleting them one by one.

### Relevant Documentation
*   [git-branch](https://git-scm.com/docs/git-branch): Documentation for listing and deleting local branches.
*   [git-push](https://git-scm.com/docs/git-push): Documentation for the `--delete` flag used for remote branches.
*   [Git Field Names (for --format)](https://git-scm.com/docs/git-for-each-ref#_field_names): Details on the available atoms like `authordate` and `committerdate`.
*   [Python subprocess.run](https://docs.python.org/3/library/subprocess.html#subprocess.run): Official Python documentation for the subprocess module.