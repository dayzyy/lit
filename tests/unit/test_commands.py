import pytest

from lit.cli.commands import SnapshotCkeckoutCommand, SnapshotCreateCommand
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import NothingToCommitError, SnapshotNotFoundError
from tests.conftest import RepoContext


def test_snapshot_creates_new_snapshot_when_changes_exist(repo_context: RepoContext):
    file_path = repo_context.root / "new_file_1.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    file_path = repo_context.root / "new_file_2.txt"
    file_path.write_text("hello world!")

    command = SnapshotCreateCommand(message="test message", cwd=repo_context.root)
    command.run()

    snapshots = repo_context.snapshot_repo.reader.read_snapshots()
    assert len(snapshots) == 2
    assert snapshots[-1] != snapshots[-2]


def test_snapshot_raises_when_no_changes(repo_context: RepoContext):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    command = SnapshotCreateCommand(message="test message", cwd=repo_context.root)

    with pytest.raises(NothingToCommitError):
        command.run()


def test_checkout_raises_when_snapshot_not_found(repo_context: RepoContext):
    command = SnapshotCkeckoutCommand("invalid_id", cwd=repo_context.root)

    with pytest.raises(SnapshotNotFoundError):
        command.run()


def test_checkout_removes_files_not_present_in_target_snapshot(
    repo_context: RepoContext,
):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    snapshot_2 = build_snapshot(root=repo_context.root, message="commit 2")
    repo_context.snapshot_repo.add(snapshot_2)

    assert file_path_2.exists()

    command = SnapshotCkeckoutCommand(snapshot_1.id, repo_context.root)
    command.run()

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert not file_path_2.exists()


def test_checkout_creates_files_present_in_target_snapshot(repo_context: RepoContext):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2.unlink()

    snapshot_2 = build_snapshot(root=repo_context.root, message="commit 2")
    repo_context.snapshot_repo.add(snapshot_2)

    command = SnapshotCkeckoutCommand(snapshot_1.id, repo_context.root)
    command.run()

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert file_path_2.exists()
    assert (
        file_path_2.read_text()
        == snapshot_1.files[file_path_2.relative_to(repo_context.root)].content
    )
