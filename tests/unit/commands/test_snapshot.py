import pytest

from lit.cli.commands import SnapshotCreateCommand
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import NothingToCommitError
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
