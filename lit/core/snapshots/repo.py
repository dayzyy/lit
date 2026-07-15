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
    def get(self, id: str) -> ProjectSnapshot:
        snapshots = self.all()

        for ss in snapshots:
            if ss.id == id:
                return ss
        raise SnapshotNotFoundError
