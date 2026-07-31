from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.differ import diff_snapshots
from tests.conftest import RepoContext


def test_diff_reports_modified_file(repo_context: RepoContext):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot_1 = build_snapshot(repo_context.root, "commit 1")

    file_path.write_text("hello world!")

    snapshot_2 = build_snapshot(repo_context.root, "commit 2")

    diff = diff_snapshots(snapshot_1, snapshot_2)

    assert "Modified: new_file.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff


def test_diff_reports_added_file(repo_context: RepoContext):
    snapshot_1 = build_snapshot(repo_context.root, "commit 1")

    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot_2 = build_snapshot(repo_context.root, "commit 2")

    diff = diff_snapshots(snapshot_1, snapshot_2)

    assert "Added: new_file.txt" in diff
    assert "+hello" in diff


def test_diff_reports_removed_file(repo_context: RepoContext):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot_1 = build_snapshot(repo_context.root, "commit 1")

    file_path.unlink()

    snapshot_2 = build_snapshot(repo_context.root, "commit 2")

    diff = diff_snapshots(snapshot_1, snapshot_2)

    assert "Removed: new_file.txt" in diff
    assert "-hello" in diff


def test_diff_reports_added_removed_and_modified_files(
    repo_context: RepoContext,
):
    modified_file = repo_context.root / "modified.txt"
    modified_file.write_text("hello")

    removed_file = repo_context.root / "removed.txt"
    removed_file.write_text("goodbye")

    snapshot_1 = build_snapshot(repo_context.root, "commit 1")

    # Modify one file
    modified_file.write_text("hello world!")

    # Remove one file
    removed_file.unlink()

    # Add one file
    added_file = repo_context.root / "added.txt"
    added_file.write_text("new file")

    snapshot_2 = build_snapshot(repo_context.root, "commit 2")

    diff = diff_snapshots(snapshot_1, snapshot_2)

    # Modified file
    assert "Modified: modified.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff

    # Removed file
    assert "Removed: removed.txt" in diff
    assert "-goodbye" in diff

    # Added file
    assert "Added: added.txt" in diff
    assert "+new file" in diff
