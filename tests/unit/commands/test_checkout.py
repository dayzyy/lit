import pytest

from lit.cli.commands import SnapshotCkeckoutCommand
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import SnapshotNotFoundError
from tests.conftest import RepoContext


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


def test_checkout_creates_nested_dir_files(repo_context: RepoContext):
    file_path_1 = repo_context.root / "nested" / "further" / "new_file_1.txt"
    file_path_1.parent.mkdir(parents=True, exist_ok=True)
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    file_path_1.unlink()
    (repo_context.root / "nested" / "further").rmdir()
    (repo_context.root / "nested").rmdir()

    assert not file_path_1.exists()
    assert not (repo_context.root / "nested").exists()
    assert not (repo_context.root / "nested" / "further").exists()

    command = SnapshotCkeckoutCommand(snapshot_1.id, repo_context.root)
    command.run()

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert (repo_context.root / "nested").exists()
    assert (repo_context.root / "nested" / "further").exists()


def test_checkout_restores_state_of_modified_files(repo_context: RepoContext):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_1.write_text("hello world!")

    assert file_path_1.read_text() == "hello world!"

    command = SnapshotCkeckoutCommand(snapshot_1.id, repo_context.root)
    command.run()

    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
