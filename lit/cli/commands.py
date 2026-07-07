from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Self, final

from lit.commands.init import create_repo
from lit.config import SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
from lit.core.snapshots.builder import build_snapshot
from lit.core.snapshots.exceptions import NothingToCommitError
from lit.core.snapshots.repo import SnapshotRepository
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
        self.execute()

    @abstractmethod
    def execute(self):
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
    def execute(self):
        create_repo()


class SnapshotCreateCommand(RepoCommand):
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


class SnapshotListCommand(RepoCommand):
    def execute(self):
        snapshots = self.repo.all()

        print(f"{'ID':36} {'CREATED':20} MESSAGE")
        print("─" * 80)

        for snapshot in snapshots:
            created = snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{snapshot.id:36} " f"{created:20} " f"{snapshot.message}")


class SnapshotCkeckoutCommand(RepoCommand):
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
        target_snapshot = self.repo.get(self.target_id)
        assert target_snapshot is not None

        cwd_files = build_snapshot(root=self.root, message="").files
        cwd_paths = set(cwd_files)
        snapshot_files = target_snapshot.files
        snapshot_paths = set(snapshot_files)

        to_remove = cwd_paths - snapshot_paths
        to_create = snapshot_paths - cwd_paths

        for relative_path in to_remove:
            abs_path = self.root / relative_path
            abs_path.unlink()
        for relative_path in to_create:
            abs_path = self.root / relative_path
            abs_path.touch()
            abs_path.write_text(snapshot_files[relative_path].content)
