from lit.cli.parser import create_parser
from lit.core.snapshots.builder import build_snapshot
from tests.conftest import RepoContext


def test_cli_status_reports_added_files(
    repo_context: RepoContext,
    capsys,
):
    snapshot = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot)

    new_file = repo_context.root / "new_file.txt"
    new_file.write_text("hello")

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert "Added:" in captured.out
    assert "new_file.txt" in captured.out


def test_cli_status_reports_modified_files(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "modified_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert "Modified:" in captured.out
    assert "modified_file.txt" in captured.out


def test_cli_status_reports_removed_files(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "removed_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.unlink()

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert "Removed:" in captured.out
    assert "removed_file.txt" in captured.out


def test_cli_status_reports_added_removed_and_modified_files(
    repo_context: RepoContext,
    capsys,
):
    modified_file = repo_context.root / "modified_file.txt"
    modified_file.write_text("hello")

    removed_file = repo_context.root / "removed_file.txt"
    removed_file.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot)

    modified_file.write_text("hello world!")
    removed_file.unlink()

    added_file = repo_context.root / "added_file.txt"
    added_file.write_text("new file")

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert "Added:" in captured.out
    assert "added_file.txt" in captured.out

    assert "Removed:" in captured.out
    assert "removed_file.txt" in captured.out

    assert "Modified:" in captured.out
    assert "modified_file.txt" in captured.out


def test_cli_status_reports_clean_working_tree(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(root=repo_context.root, message="commit 1")
    repo_context.snapshot_repo.add(snapshot)

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert captured.out.strip() == "Working tree clean."


def test_cli_status_reports_all_files_as_added_without_initial_commit(
    repo_context: RepoContext,
    capsys,
):
    file_path_1 = repo_context.root / "file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "file_2.txt"
    file_path_2.write_text("world")

    parser = create_parser()
    args = parser.parse_args(["status"])

    command = args.command_cls.from_args(args=args, cwd=repo_context.root)
    command.run()

    captured = capsys.readouterr()

    assert "Added:" in captured.out
    assert "file_1.txt" in captured.out
    assert "file_2.txt" in captured.out
