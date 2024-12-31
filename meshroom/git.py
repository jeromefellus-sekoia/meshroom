from subprocess import DEVNULL, PIPE, STDOUT, CalledProcessError, check_call, check_output
from meshroom.model import get_project_dir


def git_init(remote: str):
    """Initialize a new Git repository in the project directory"""
    try:
        check_call(["git", "init"], stderr=DEVNULL, stdout=DEVNULL, cwd=get_project_dir())

        if remote:
            old_remote = check_output(["git", "remote"], encoding="utf-8").strip()
            if old_remote:
                check_call(["git", "remote", "remove", old_remote], stderr=DEVNULL, cwd=get_project_dir())
            check_call(["git", "remote", "add", "origin", remote], stderr=DEVNULL, cwd=get_project_dir())
            git_pull()
    except Exception:
        ...


def git_branch(branch: str):
    """Switch to the given branch"""
    check_call(["git", "checkout", branch], cwd=get_project_dir())


def git_pull():
    """Pull the latest changes from the remote repository"""
    check_call(["git", "pull"], cwd=get_project_dir())


def git_push(autocommit: bool = True, path: str = ".", commit_msg: str | None = None):
    """
    Push the current branch to the remote repository, optionally committing all changes under :path
    returns True if any files were committed
    """
    files = []
    try:
        if autocommit and (files := get_updated_files()):
            updated = ", ".join(files[:3])
            if len(files) > 3:
                updated += f" and {len(files) - 3} more"
            check_call(["git", "add", path], cwd=get_project_dir())
            check_call(["git", "commit", "-m", commit_msg or f"Update {updated}"], cwd=get_project_dir())
    except Exception:
        ...
    try:
        check_output(["git", "push"], cwd=get_project_dir(), stderr=STDOUT)
    except CalledProcessError as e:
        raise RuntimeError(e.stdout.decode())
    return bool(files)


def get_updated_files(depth: int = 1):
    """Get the list of updated paths in the current branch, up to the given depth"""
    files = set()
    for line in check_output(["git", "diff", "--name-only"], cwd=get_project_dir(), encoding="utf-8").split():
        files.add("/".join(line.strip().split("/")[:depth]))
    return list(files)


def git_get_remote():
    """Get the remote URL of the current repository"""
    try:
        return check_output(["git", "remote", "get-url", "origin"], cwd=get_project_dir(), encoding="utf-8").strip()
    except Exception:
        raise RuntimeError("\nThis git repository has no remote URL, please set one up using\ngit remote add origin <url>")


def git_get_branch():
    """Get the current branch"""
    return check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=get_project_dir(), encoding="utf-8").strip()
