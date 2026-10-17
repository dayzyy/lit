import pytest

from lit.core.constants import DEFAULT_BRANCH_NAME
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
    repo_context.branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot.id)

    file_path = repo_context.root / "new_file_2.txt"
    file_path.write_text("hello world!")

    created_snapshot = commands.snapshot("test message")

    snapshots = repo_context.snapshot_repo.reader.read_snapshots()
    assert len(snapshots) == 2
    assert snapshots[-1].id == created_snapshot.id
    assert snapshots[-1].id != snapshots[-2].id


def case_raises_when_no_changes(repo_context: RepoContext, commands: CommandRunner):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)
    repo_context.branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot.id)

    with pytest.raises(NothingToCommitError):
        commands.snapshot("test message")


def case_sets_none_for_parent_id_when_first_snapshot(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = commands.snapshot("test message")

    assert snapshot.message == "test message"
    assert snapshot.parent_id is None


def case_sets_branch_snapshot_for_parent_id_when_head_is_attached(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot_1 = commands.snapshot("test message 1")

    file_path.write_text("modified")
    snapshot_2 = commands.snapshot("test message 2")

    assert snapshot_2.message == "test message 2"
    assert snapshot_2.parent_id == snapshot_1.id


def case_sets_snapshot_id_for_parent_id_when_head_is_detached(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot_1 = commands.snapshot("test message 1")

    file_path.write_text("modified")
    commands.snapshot("test message 2")

    repo_context.branch_repo.detach(snapshot_1.id)

    file_path.write_text("modified again")
    snapshot_3 = commands.snapshot("test message 3")

    assert snapshot_3.parent_id == snapshot_1.id


CASES = [
    case_creates_new_snapshot_when_changes_exist,
    case_raises_when_no_changes,
    case_sets_none_for_parent_id_when_first_snapshot,
    case_sets_branch_snapshot_for_parent_id_when_head_is_attached,
    case_sets_snapshot_id_for_parent_id_when_head_is_detached,
]
