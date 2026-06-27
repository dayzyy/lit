from pathlib import Path
from typing import final

from core.snapshots.exceptions import SnapshotFileNotFoundError
from core.snapshots.reader import BaseSnapshotReader
from core.snapshots.schemas import ProjectSnapshot
from core.snapshots.writer import BaseSnapshotWriter
from core.structure.structure import RepoStructure


class SnapshotRepository:
    _FILE_NAME = "snapshots"

    def __init__(
        self,
        lit_path: Path,
        reader_cls: type[BaseSnapshotReader],
        writer_cls: type[BaseSnapshotWriter],
    ):
        snapshots_file_path = self._get_file_path(lit_path)
        if not snapshots_file_path.exists():
            raise SnapshotFileNotFoundError

        self.reader = reader_cls(snapshots_file_path)
        self.writer = writer_cls(snapshots_file_path)

    @classmethod
    @final
    def _get_file_path(cls, lit_path: Path) -> Path:
        path = RepoStructure.Directories.SNAPSHOTS.get_path(lit_path) / cls._FILE_NAME
        return path

    @final
    def add(self, snapshot: ProjectSnapshot) -> None:
        self.writer.add(snapshot)

    @final
    def latest(self) -> ProjectSnapshot:
        snapshots = self.all()

        if not snapshots:
            raise SnapshotFileNotFoundError

        return snapshots[-1]

    @final
    def all(self) -> list[ProjectSnapshot]:
        snapshots = self.reader.read_snapshots()
        return snapshots
