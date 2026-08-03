from lit.core.snapshots.builder import build_snapshot
from tests.commands.runners import CommandRunner
from tests.conftest import RepoContext


def case_added_files(repo_context: RepoContext, commands: CommandRunner):
    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    new_file = repo_context.root / "new_file.txt"
    new_file.write_text("hello")

    output = commands.status()

    assert "Added:" in output
    assert "new_file.txt" in output


def case_modified_files(repo_context: RepoContext, commands: CommandRunner):
    file_path = repo_context.root / "modified_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.write_text("hello world!")

    output = commands.status()

    assert "Modified:" in output
    assert "modified_file.txt" in output


def case_removed_files(repo_context: RepoContext, commands: CommandRunner):
    file_path = repo_context.root / "removed_file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    file_path.unlink()

    output = commands.status()

    assert "Removed:" in output
    assert "removed_file.txt" in output


def case_added_removed_and_modified_files(
    repo_context: RepoContext, commands: CommandRunner
):
    modified_file = repo_context.root / "modified_file.txt"
    modified_file.write_text("hello")

    removed_file = repo_context.root / "removed_file.txt"
    removed_file.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    modified_file.write_text("hello world!")
    removed_file.unlink()

    added_file = repo_context.root / "added_file.txt"
    added_file.write_text("new file")

    output = commands.status()

    assert "Modified:" in output
    assert "modified_file.txt" in output

    assert "Removed:" in output
    assert "removed_file.txt" in output

    assert "Added:" in output
    assert "added_file.txt" in output


def case_clean_working_tree(repo_context: RepoContext, commands: CommandRunner):
    file_path = repo_context.root / "file.txt"
    file_path.write_text("hello")

    snapshot = build_snapshot(repo_context.root, "commit 1")
    repo_context.snapshot_repo.add(snapshot)

    output = commands.status()

    assert output == "Working tree clean."


def case_all_files_added_without_initial_commit(
    repo_context: RepoContext, commands: CommandRunner
):
    file_path_1 = repo_context.root / "file_1.txt"
    file_path_1.write_text("hello")

    file_path_2 = repo_context.root / "file_2.txt"
    file_path_2.write_text("world")

    output = commands.status()

    assert "Added:" in output
    assert "file_1.txt" in output
    assert "file_2.txt" in output


CASES = [
    case_added_files,
    case_modified_files,
    case_removed_files,
    case_added_removed_and_modified_files,
    case_clean_working_tree,
    case_all_files_added_without_initial_commit,
]
