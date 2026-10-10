from pathlib import Path
from typing import final

from lit.core.snapshots.exceptions import (
    SnapshotFileNotFoundError,
    SnapshotNotFoundError,
)
from lit.core.snapshots.reader import BaseSnapshotReader
from lit.core.snapshots.schemas import ProjectSnapshot
from lit.core.snapshots.writer import BaseSnapshotWriter
from lit.core.structure.structure import RepoStructure


class SnapshotRepository:
    """
    High-level access to the snapshots of a repository.

    Wraps a `BaseSnapshotReader` and `BaseSnapshotWriter` configured for
    the repository's snapshot storage file, exposing common operations
    such as appending, listing, and querying snapshots.
    """

    def __init__(
        self,
        lit_path: Path,
        reader_cls: type[BaseSnapshotReader],
        writer_cls: type[BaseSnapshotWriter],
    ):
        """
        Create a handle for the snapshot storage of a repository.

        The repository must already be initialized: `lit_path` must be a
        `.lit` directory containing a snapshots file. Raise
        `SnapshotFileNotFoundError` if the storage file does not exist.
        """
        snapshots_file_path = self._get_file_path(lit_path)
        if not snapshots_file_path.exists():
            raise SnapshotFileNotFoundError

        self.reader = reader_cls(snapshots_file_path)
        self.writer = writer_cls(snapshots_file_path)

    @classmethod
    @final
    def _get_file_path(cls, lit_path: Path) -> Path:
        """
        Return the path to the snapshot storage file of `lit_path`.
        """
        path = RepoStructure.Files.SNAPSHOTS.get_path(lit_path)
        return path

    @final
    def add(self, snapshot: ProjectSnapshot) -> None:
        self.writer.append(snapshot)

    @final
    def latest(self) -> ProjectSnapshot | None:
        snapshots = self.all()

        if not snapshots:
            return None

        return snapshots[-1]

    @final
    def all(self) -> list[ProjectSnapshot]:
        snapshots = self.reader.read_snapshots()
        return snapshots

    @final
    def get(self, id: str) -> ProjectSnapshot | None:
        """
        Returns the snapshot with the given `id`, or None if it doesnt exist.
        """
        snapshots = self.all()

        for ss in snapshots:
            if ss.id == id:
                return ss
        return None

    @final
    def require_snapshot(self, id: str) -> ProjectSnapshot:
        snapshot = self.get(id)
        if snapshot is None:
            raise SnapshotNotFoundError(id=id)

        return snapshot
