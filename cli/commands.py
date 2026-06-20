from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from commands.init import create_repo
from config import SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
from core.snapshots.builder import build_snapshot
from core.snapshots.exceptions import NothingToCommitError
from core.snapshots.repo import SnapshotRepository
from core.structure.structure import RepoStructure


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

        self._init_snapshot_repo()

    def _init_snapshot_repo(self):
        self.repo = SnapshotRepository(
            self.lit_path, SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
        )


class InitCommand(LitCommand):
    def execute(self):
        create_repo()


class SnapshotCommand(RepoCommand):
    def execute(self):
        latest_snapshot = self.repo.latest()
        new_snapshot = build_snapshot(self.lit_path.parent)

        if latest_snapshot == new_snapshot:
            raise NothingToCommitError

        self.repo.add(new_snapshot)
