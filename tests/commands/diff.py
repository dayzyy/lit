import pytest

from lit.cli.exceptions import TooManySnapshotIDsError
from lit.core.snapshots.builder import build_snapshot
from tests.commands.runners import CommandRunner
from tests.conftest import RepoContext


def case_without_ids_compares_working_tree_to_latest_snapshot(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    diff = commands.diff()

    assert "Modified: new_file.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff


def case_with_one_id_compares_working_tree_to_snapshot(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    diff = commands.diff(snapshot.id)

    assert "Modified: new_file.txt" in diff
    assert "-hello world!" in diff
    assert "+hello" in diff


def case_with_two_ids_compares_snapshots(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    from_snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(from_snapshot)

    file_path.write_text("hello world!")

    to_snapshot = build_snapshot(repo_context.root, "commit 2")
    repo_context.snapshot_repo.add(to_snapshot)

    diff = commands.diff(from_snapshot.id, to_snapshot.id)

    assert "Modified: new_file.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff


def case_raises_when_more_than_two_ids_are_provided(
    repo_context: RepoContext, commands: CommandRunner
):
    with pytest.raises(TooManySnapshotIDsError):
        commands.diff("id1", "id2", "id3")


CASES = [
    case_without_ids_compares_working_tree_to_latest_snapshot,
    case_with_one_id_compares_working_tree_to_snapshot,
    case_with_two_ids_compares_snapshots,
    case_raises_when_more_than_two_ids_are_provided,
]
