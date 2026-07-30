from lit.cli.commands import StatusCommand
from lit.core.snapshots.builder import build_snapshot
from tests.conftest import RepoContext


def test_status_reports_added_files(repo_context: RepoContext):
    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    new_file = repo_context.root / "new_file.txt"
    new_file.write_text("hello")

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert "Added:" in output
    assert "new_file.txt" in output


def test_status_reports_modified_files(repo_context: RepoContext):
    file_path = repo_context.root / "modified_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert "Modified:" in output
    assert "modified_file.txt" in output


def test_status_reports_removed_files(repo_context: RepoContext):
    file_path = repo_context.root / "removed_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.unlink()

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert "Removed:" in output
    assert "removed_file.txt" in output


def test_status_reports_added_removed_and_modified_files(repo_context: RepoContext):
    modified_file = repo_context.root / "modified_file.txt"
    modified_file.write_text("hello")

    removed_file = repo_context.root / "removed_file.txt"
    removed_file.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    modified_file.write_text("hello world!")
    removed_file.unlink()

    added_file = repo_context.root / "added_file.txt"
    added_file.write_text("new file")

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert "Modified:" in output
    assert "modified_file.txt" in output

    assert "Removed:" in output
    assert "removed_file.txt" in output

    assert "Added:" in output
    assert "added_file.txt" in output


def test_status_reports_clean_working_tree(repo_context: RepoContext):
    file_path = repo_context.root / "file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert output == "Working tree clean."


def test_status_reports_all_files_as_added_without_initial_commit(
    repo_context: RepoContext,
):
    file_path_1 = repo_context.root / "file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "file_2.txt"
    file_path_2.write_text("world")

    command = StatusCommand(cwd=repo_context.root)

    output = command.execute()

    assert "Added:" in output
    assert "file_1.txt" in output
    assert "file_2.txt" in output
