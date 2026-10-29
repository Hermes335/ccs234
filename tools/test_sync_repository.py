"""Offline integration tests for the updater using disposable local Git remotes."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "tools" / "sync-repository.ps1"


def command(args, cwd=None, check=True):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def git(repo, *args):
    return command(["git", "-C", str(repo), *args]).stdout.strip()


def setup(tmp_path):
    remote, author, local = [tmp_path / name for name in ["remote.git", "author", "local"]]
    command(["git", "init", "--bare", "-b", "main", str(remote)])
    command(["git", "clone", str(remote), str(author)])
    git(author, "config", "user.name", "Updater test")
    git(author, "config", "user.email", "updater-test@example.invalid")
    (author / ".gitignore").write_text(".sync/\n")
    (author / "project.txt").write_text("version 1\n")
    git(author, "add", ".")
    git(author, "commit", "-m", "Initial fixture")
    git(author, "push", "-u", "origin", "main")
    command(["git", "clone", str(remote), str(local)])
    return remote, author, local


def update_remote(author):
    (author / "project.txt").write_text("version 2\n")
    git(author, "add", "project.txt")
    git(author, "commit", "-m", "Remote update")
    git(author, "push")


def sync(remote, local):
    return command(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                    "-File", str(SYNC), "-Repository", str(local), "-ExpectedRemote", str(remote)], check=False)


def test_clean_tree_fast_forwards(tmp_path):
    remote, author, local = setup(tmp_path)
    update_remote(author)
    result = sync(remote, local)
    assert result.returncode == 0, result.stderr
    assert (local / "project.txt").read_text() == "version 2\n"
    assert git(local, "rev-parse", "HEAD") == git(author, "rev-parse", "HEAD")


def test_dirty_tree_preserves_local_changes(tmp_path):
    remote, author, local = setup(tmp_path)
    (local / "project.txt").write_text("unsaved local work\n")
    before = git(local, "rev-parse", "HEAD")
    update_remote(author)
    result = sync(remote, local)
    assert result.returncode == 0, result.stderr
    assert (local / "project.txt").read_text() == "unsaved local work\n"
    assert git(local, "rev-parse", "HEAD") == before


def test_untracked_files_pause_updates(tmp_path):
    remote, author, local = setup(tmp_path)
    (local / "notes.txt").write_text("Local notes")
    update_remote(author)
    assert sync(remote, local).returncode == 0
    assert (local / "project.txt").read_text() == "version 1\n"


def test_divergent_history_preserves_local_commit(tmp_path):
    remote, author, local = setup(tmp_path)
    git(local, "config", "user.name", "Updater test")
    git(local, "config", "user.email", "updater-test@example.invalid")
    (local / "local.txt").write_text("Committed local work")
    git(local, "add", "local.txt")
    git(local, "commit", "-m", "Local commit")
    before = git(local, "rev-parse", "HEAD")
    update_remote(author)
    result = sync(remote, local)
    assert result.returncode == 1
    assert git(local, "rev-parse", "HEAD") == before
    assert (local / "local.txt").read_text() == "Committed local work"


def test_changed_remote_is_not_contacted(tmp_path):
    remote, author, local = setup(tmp_path)
    git(local, "remote", "set-url", "origin", str(tmp_path / "unapproved.git"))
    result = sync(remote, local)
    assert result.returncode == 0
    assert "origin differs" in (local / ".sync" / "auto-update.log").read_text(encoding="utf-8-sig")
