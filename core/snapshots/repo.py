from abc import ABC
from pathlib import Path
from typing import final

from core.snapshots.reader import BaseSnapshotReader
from core.snapshots.writer import BaseSnapshotWriter
from core.structure.structure import RepoStructure


class SnapshotRepository(ABC):
    _FILE_NAME = "snapshots"

    def __init__(
        self,
        lit_path: Path,
        reader_cls: type[BaseSnapshotReader],
        writer_cls: type[BaseSnapshotWriter],
    ):
        snapshots_file_path = self._get_file_path(lit_path)

        self.reader = reader_cls(snapshots_file_path)
        self.writer = writer_cls(snapshots_file_path)

    @classmethod
    @final
    def _get_file_path(cls, lit_path: Path) -> Path:
        path = RepoStructure.Directories.SNAPSHOTS.get_path(lit_path) / cls._FILE_NAME
        return path
