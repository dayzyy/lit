import pytest

from lit.cli.commands import DiffCommand
from lit.cli.exceptions import TooManySnapshotIDsError
from lit.core.snapshots.builder import build_snapshot
from tests.conftest import RepoContext


def test_diff_without_ids_compares_working_tree_to_latest_snapshot(
    repo_context: RepoContext,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    command = DiffCommand(snapshot_ids=[], cwd=repo_context.root)

    diff = command.execute()

    assert "Modified: new_file.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff


def test_diff_with_one_id_compares_working_tree_to_snapshot(
    repo_context: RepoContext,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    command = DiffCommand(
        snapshot_ids=[snapshot.id],
        cwd=repo_context.root,
    )

    diff = command.execute()

    assert "Modified: new_file.txt" in diff
    assert "-hello world!" in diff
    assert "+hello" in diff


def test_diff_with_two_ids_compares_snapshots(
    repo_context: RepoContext,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    from_snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(from_snapshot)

    file_path.write_text("hello world!")

    to_snapshot = build_snapshot(repo_context.root, "commit 2")
    repo_context.snapshot_repo.add(to_snapshot)

    command = DiffCommand(
        snapshot_ids=[from_snapshot.id, to_snapshot.id],
        cwd=repo_context.root,
    )

    diff = command.execute()

    assert "Modified: new_file.txt" in diff
    assert "-hello" in diff
    assert "+hello world!" in diff


def test_diff_raises_when_more_than_two_ids_are_provided(
    repo_context: RepoContext,
):
    with pytest.raises(TooManySnapshotIDsError):
        DiffCommand(
            snapshot_ids=["id1", "id2", "id3"],
            cwd=repo_context.root,
        )
