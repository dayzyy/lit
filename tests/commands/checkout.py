import pytest

from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import SnapshotNotFoundError
from tests.commands.runners import CommandRunner
from tests.conftest import RepoContext


def case_raises_when_snapshot_not_found(
    repo_context: RepoContext, commands: CommandRunner
):
    with pytest.raises(SnapshotNotFoundError):
        commands.checkout("invalid_id")


def case_removes_files_not_present_in_target_snapshot(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    commands.checkout(snapshot_1.id)

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert not file_path_2.exists()


def case_creates_files_present_in_target_snapshot(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2.unlink()

    commands.checkout(snapshot_1.id)

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


def case_creates_nested_dir_files(repo_context: RepoContext, commands: CommandRunner):
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

    commands.checkout(snapshot_1.id)

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert (repo_context.root / "nested").exists()
    assert (repo_context.root / "nested" / "further").exists()


def case_restores_state_of_modified_files(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_1.write_text("hello world!")

    assert file_path_1.read_text() == "hello world!"

    commands.checkout(snapshot_1.id)

    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )


CASES = [
    case_raises_when_snapshot_not_found,
    case_removes_files_not_present_in_target_snapshot,
    case_creates_files_present_in_target_snapshot,
    case_creates_nested_dir_files,
    case_restores_state_of_modified_files,
]
