import pytest

from cli.parser import create_parser
from core.snapshots.builder import build_snapshot
from core.snapshots.exceptions import NothingToCommitError
from tests.conftest import RepoContext


def test_cli_snapshot_creates_new_snapshot_when_changes_exist(
    repo_context: RepoContext,
):
    snapshot = build_snapshot(root=repo_context.root, message="test message")
    repo_context.snapshot_repo.add(snapshot)

    (repo_context.root / "new_file.txt").write_text("hello")

    parser = create_parser()
    args = parser.parse_args(["snapshot", "-m", "test message"])

    command = args.command_cls(message=args.message, cwd=repo_context.root)
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

    command = args.command_cls(message=args.message, cwd=repo_context.root)

    with pytest.raises(NothingToCommitError):
        command.run()
