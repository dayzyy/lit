import pytest

from cli.commands import SnapshotCommand
from core.snapshots.builder import build_snapshot
from core.snapshots.exceptions import NothingToCommitError
from tests.conftest import RepoContext


def test_snapshot_creates_new_snapshot_when_changes_exist(repo_context: RepoContext):
    snapshot = build_snapshot(repo_context.root)
    repo_context.snapshot_repo.add(snapshot)

    # modify project
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    # act
    command = SnapshotCommand(cwd=repo_context.root)
    command.run()

    # assert
    snapshots = repo_context.snapshot_repo.reader.read_snapshots()
    assert len(snapshots) == 2
    assert snapshots[-1] != snapshots[-2]


def test_snapshot_raises_when_no_changes(repo_context: RepoContext):
    snapshot = build_snapshot(repo_context.root)
    repo_context.snapshot_repo.add(snapshot)

    # act + assert
    command = SnapshotCommand(cwd=repo_context.root)

    with pytest.raises(NothingToCommitError):
        command.run()
