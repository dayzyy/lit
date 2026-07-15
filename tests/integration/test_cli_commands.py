import pytest

from lit.cli.parser import create_parser
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import NothingToCommitError, SnapshotNotFoundError
from tests.conftest import RepoContext


def test_cli_snapshot_creates_new_snapshot_when_changes_exist(
    repo_context: RepoContext,
):
    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    (repo_context.root / "new_file.txt").write_text("hello")

    parser = create_parser()
    args = parser.parse_args(["snapshot", "-m", "test message"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    snapshots = repo_context.snapshot_repo.reader.read_snapshots()

    assert len(snapshots) == 2


def test_cli_snapshot_raises_when_no_changes(
    repo_context: RepoContext,
):
    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    parser = create_parser()
    args = parser.parse_args(["snapshot", "-m", "test message"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)

    with pytest.raises(NothingToCommitError):
        command.run()


def test_cli_checkout_raises_when_snapshot_not_found(repo_context: RepoContext):
    parser = create_parser()
    args = parser.parse_args(["checkout", "invalid_id"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)

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

    parser = create_parser()
    args = parser.parse_args(["checkout", snapshot_1.id])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert not file_path_2.exists()


def test_cli_checkout_creates_files_present_in_target_snapshot(
    repo_context: RepoContext,
):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "new_file_2.txt"
    file_path_2.write_text("hello world!")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_2.unlink()

    parser = create_parser()
    args = parser.parse_args(["checkout", snapshot_1.id])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
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


def test_cli_checkout_creates_nested_dir_files(repo_context: RepoContext):
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

    parser = create_parser()
    args = parser.parse_args(["checkout", snapshot_1.id])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    assert file_path_1.exists()
    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
    assert (repo_context.root / "nested").exists()
    assert (repo_context.root / "nested" / "further").exists()


def test_cli_checkout_restores_state_of_modified_files(repo_context: RepoContext):
    file_path_1 = repo_context.root / "new_file_1.txt"
    file_path_1.write_text("hello")

    snapshot_1 = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot_1)

    file_path_1.write_text("hello world!")

    assert file_path_1.read_text() == "hello world!"

    parser = create_parser()
    args = parser.parse_args(["checkout", snapshot_1.id])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    assert (
        file_path_1.read_text()
        == snapshot_1.files[file_path_1.relative_to(repo_context.root)].content
    )
