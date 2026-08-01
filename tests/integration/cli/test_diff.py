from lit.cli.parser import create_parser
from lit.core.snapshots.builder import build_snapshot
from tests.conftest import RepoContext


def test_cli_diff_without_ids_compares_working_tree_to_latest_snapshot(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    parser = create_parser()
    args = parser.parse_args(["diff"])

    command = args.command_cls.from_args(
        args=args,
        cwd=repo_context.root,
    )
    command.run()

    captured = capsys.readouterr()

    assert "Modified: new_file.txt" in captured.out
    assert "-hello" in captured.out
    assert "+hello world!" in captured.out


def test_cli_diff_with_one_id_compares_working_tree_to_snapshot(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    parser = create_parser()
    args = parser.parse_args(["diff", snapshot.id])

    command = args.command_cls.from_args(
        args=args,
        cwd=repo_context.root,
    )
    command.run()

    captured = capsys.readouterr()

    assert "Modified: new_file.txt" in captured.out
    assert "-hello world!" in captured.out
    assert "+hello" in captured.out


def test_cli_diff_with_two_ids_compares_snapshots(
    repo_context: RepoContext,
    capsys,
):
    file_path = repo_context.root / "new_file.txt"
    file_path.write_text("hello")

    from_snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(from_snapshot)

    file_path.write_text("hello world!")

    to_snapshot = build_snapshot(repo_context.root, "commit 2")
    repo_context.snapshot_repo.add(to_snapshot)

    parser = create_parser()
    args = parser.parse_args(["diff", from_snapshot.id, to_snapshot.id])

    command = args.command_cls.from_args(
        args=args,
        cwd=repo_context.root,
    )
    command.run()

    captured = capsys.readouterr()

    assert "Modified: new_file.txt" in captured.out
    assert "-hello" in captured.out
    assert "+hello world!" in captured.out
