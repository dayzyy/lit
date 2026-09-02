from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Self, final

from lit.cli.exceptions import TooManySnapshotIDsError
from lit.config import SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
from lit.core.constants import DEFAULT_BRANCH_NAME
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.comparer import compare_snapshots
from lit.core.snapshots.differ import diff_snapshots
from lit.core.snapshots.exceptions import NothingToCommitError
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.snapshots.schemas import ProjectSnapshot
from lit.core.structure.exceptions import RepoExistsError
from lit.core.structure.structure import RepoStructure


class LitCommand(ABC):
    """
    Base class for all CLI commands.

    Commands are executed through the public `run()` method, which
    provides a stable entry point and allows common execution logic
    to be introduced in one place.

    Subclasses must implement `execute()` with the command-specific
    behavior.
    """

    def __init__(self, cwd: Path | None = None):
        self.cwd = cwd or Path.cwd()

    @staticmethod
    def configure_parser(parser: ArgumentParser) -> None:
        """
        Configure the command-specific CLI arguments.

        Implementations should register any arguments required by the command
        on the provided parser. This method is invoked during parser creation,
        allowing each command to define its own command-line interface while
        keeping parser setup centralized.
        """
        return None

    @classmethod
    def from_args(cls, args: Namespace, cwd: Path | None = None) -> Self:
        """
        Create a command instance from parsed CLI arguments.

        This method acts as an adapter between ``argparse`` and the command,
        extracting the relevant values from the parsed argument namespace and
        constructing a fully initialized command instance.
        """
        return cls(cwd=cwd)

    @final
    def run(self):
        """
        Execute the command and print its output.
        """
        message = self.execute()
        print(message)

    @abstractmethod
    def execute(self) -> str:
        raise NotImplementedError


class RepoCommand(LitCommand):
    """
    Base class for commands that operate on an existing repository.

    During initialization, the repository root is discovered and
    stored in `lit_path`. This guarantees that subclasses have
    access to a valid repository location before execution.

    Commands such as `status`, `diff`, and `snapshot` should inherit
    from this class. Commands that can be executed outside of a
    repository, such as `init`, should inherit directly from
    `LitCommand`.
    """

    lit_path: Path

    def __init__(self, cwd: Path | None = None):
        super().__init__(cwd)

        self.lit_path = RepoStructure.find_valid_repo_root(self.cwd)
        self.root = self.lit_path.parent

        self._init_snapshot_repo()

    @final
    def _init_snapshot_repo(self):
        self.repo = SnapshotRepository(
            self.lit_path, SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
        )


class InitCommand(LitCommand):
    """
    Initialize a new Lit repository in the current directory.

    Raise `RepoExistsError` if a repository already exists.
    """

    def execute(self) -> str:
        if RepoStructure.repo_exists(self.cwd):
            raise RepoExistsError

        lit_path = self.cwd / RepoStructure.Directories.BASE.value
        lit_path.mkdir()

        for dir in RepoStructure.Directories:
            if dir is not RepoStructure.Directories.BASE:
                dir.get_path(lit_path).mkdir(parents=True)

        for file in RepoStructure.Files:
            file.get_path(lit_path).touch()

        # Create default branch
        default_branch_path = (
            RepoStructure.Directories.BRANCHES.get_path(lit_path) / DEFAULT_BRANCH_NAME
        )
        default_branch_path.touch()

        # Initialize snapshot storage
        snapshot_file_path = SnapshotRepository._get_file_path(lit_path)
        SNAPSHOT_WRITER_CLS._initialize_file(snapshot_file_path)

        return "Created an empty lit repository!"


class SnapshotCreateCommand(RepoCommand):
    """
    Create a snapshot of the current working tree.
    """

    def __init__(self, message: str, cwd: Path | None = None):
        super().__init__(cwd)
        self.message = message

    @classmethod
    def from_args(cls, args: Namespace, cwd: Path | None = None) -> Self:
        message = args.message
        return cls(message=message, cwd=cwd)

    @staticmethod
    def configure_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "-m",
            "--message",
            required=True,
            help="Snapshot message describing the state",
        )

    def execute(self):
        latest_snapshot = self.repo.latest()
        new_snapshot = build_snapshot(self.lit_path.parent, self.message)

        if latest_snapshot is not None and latest_snapshot == new_snapshot:
            raise NothingToCommitError

        self.repo.add(new_snapshot)

        return f"Created a new snapshot with id: {new_snapshot.id}"


class SnapshotListCommand(RepoCommand):
    """
    List all snapshots stored in the repository.
    """

    def execute(self):
        snapshots = self.repo.all()

        lines = [
            f"{'ID':36} {'CREATED':20} MESSAGE",
            "─" * 80,
        ]

        for snapshot in snapshots:
            created = snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"{snapshot.id:36} " f"{created:20} " f"{snapshot.message}")

        return "\n".join(lines)


class SnapshotCheckoutCommand(RepoCommand):
    """
    Restore the working tree to the state of a snapshot.
    """

    def __init__(self, snapshot_id: str, cwd: Path | None = None):
        super().__init__(cwd)
        self.target_id = snapshot_id

    @classmethod
    def from_args(cls, args: Namespace, cwd: Path | None = None) -> Self:
        snapshot_id = args.snapshot_id
        return cls(snapshot_id=snapshot_id, cwd=cwd)

    @staticmethod
    def configure_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "snapshot_id",
            help="ID of the snapshot to check out",
        )

    def execute(self):
        snapshot_to_checkout = self.repo.get(self.target_id)
        target_files = snapshot_to_checkout.files

        cwd_snapshot = build_snapshot(root=self.root, message="")
        diff = compare_snapshots(cwd_snapshot, snapshot_to_checkout)

        for relative_path in diff.removed:
            abs_path = self.root / relative_path
            abs_path.unlink()
        for relative_path in diff.added | diff.modified:
            abs_path = self.root / relative_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(target_files[relative_path].content)

        return f"Checked out to snapshot {snapshot_to_checkout.id}"


class StatusCommand(RepoCommand):
    """
    Show the status of the working tree relative to the latest snapshot.
    """

    def execute(self):
        latest_snapshot = self.repo.latest()
        cwd_snapshot = build_snapshot(root=self.root, message="")

        # If no snapshots have been taken before, all files are new
        if latest_snapshot is None:
            added = set(cwd_snapshot.files)
            removed = set()
            modified = set()

        else:
            diff = compare_snapshots(latest_snapshot, cwd_snapshot)
            added = diff.added
            removed = diff.removed
            modified = diff.modified

        if not (added or removed or modified):
            return "Working tree clean."

        lines = []

        if added:
            lines.append("Added:")
            lines.extend(f"  {path}" for path in sorted(added))
            lines.append("")

        if removed:
            lines.append("Removed:")
            lines.extend(f"  {path}" for path in sorted(removed))
            lines.append("")

        if modified:
            lines.append("Modified:")
            lines.extend(f"  {path}" for path in sorted(modified))

        return "\n".join(lines)


class DiffCommand(RepoCommand):
    """
    Show a unified diff between snapshots and/or the working tree.
    """

    def __init__(self, snapshot_ids: list[str], cwd: Path | None = None):
        if len(snapshot_ids) > 2:
            raise TooManySnapshotIDsError

        super().__init__(cwd)
        self.snapshot_ids = snapshot_ids

    @classmethod
    def from_args(cls, args: Namespace, cwd: Path | None = None) -> Self:
        snapshot_ids = args.snapshot_ids

        return cls(
            snapshot_ids=snapshot_ids,
            cwd=cwd,
        )

    @staticmethod
    def configure_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "snapshot_ids",
            nargs="*",
            help=(
                "Zero, one, or two snapshot IDs.\n"
                "No IDs: compare working tree to latest snapshot.\n"
                "One ID: compare working tree to that snapshot.\n"
                "Two IDs: compare the two snapshots."
            ),
        )

    def execute(self):
        cwd_snapshot = build_snapshot(root=self.root, message="")

        if not self.snapshot_ids:
            latest_snapshot = self.repo.latest() or ProjectSnapshot(
                files={}, message=""
            )
            diff = diff_snapshots(latest_snapshot, cwd_snapshot)

        elif len(self.snapshot_ids) == 1:
            to_snapshot = self.repo.get(self.snapshot_ids[0])
            diff = diff_snapshots(cwd_snapshot, to_snapshot)

        else:
            from_snapshot = self.repo.get(self.snapshot_ids[0])
            to_snapshot = self.repo.get(self.snapshot_ids[1])
            diff = diff_snapshots(from_snapshot, to_snapshot)

        return diff
