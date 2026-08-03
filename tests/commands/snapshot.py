import pytest

from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import NothingToCommitError
from tests.commands.runners import CommandRunner
from tests.conftest import RepoContext


def case_creates_new_snapshot_when_changes_exist(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file_1.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    file_path = repo_context.root / "new_file_2.txt"
    file_path.write_text("hello world!")

    commands.snapshot("test message")

    snapshots = repo_context.snapshot_repo.reader.read_snapshots()
    assert len(snapshots) == 2
    assert snapshots[-1] != snapshots[-2]


def case_raises_when_no_changes(repo_context: RepoContext, commands: CommandRunner):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    with pytest.raises(NothingToCommitError):
        commands.snapshot("test message")


CASES = [
    case_creates_new_snapshot_when_changes_exist,
    case_raises_when_no_changes,
]
