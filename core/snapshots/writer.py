import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from core.snapshots.reader import JSONSnapshotReader
from core.snapshots.schemas import ProjectSnapshot


class BaseSnapshotWriter(ABC):
    """
    Initial content written to a newly created snapshot storage file.

    Each subclass should override this value with a structure appropriate
    for its storage format.

    Example:
    JSONSnapshotWriter.INITIAL_STRUCTURE = tuple()

    This allows the storage file to be parsed immediately and have
    snapshots appended to it.
    """

    INITIAL_STRUCTURE = None

    def __init__(self, file_path: Path):
        self.file_path = file_path

    @final
    def add(self, snapshot: ProjectSnapshot) -> None:
        if not isinstance(snapshot, ProjectSnapshot):
            raise TypeError(
                f"'snapshot' must be 'ProjectSnapshot', got {type(snapshot).__name__}"
            )

        self._add(snapshot)

    @abstractmethod
    def _add(self, snapshot: ProjectSnapshot) -> None:
        """
        Persist a snapshot to the configured storage file.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _initialize_file(cls, snapshos_file_path: Path):
        """
        Initialize the snapshot storage file with the format's
        default structure.
        """
        raise NotImplementedError


class JSONSnapshotWriter(BaseSnapshotWriter):
    INITIAL_STRUCTURE = []

    def _add(self, snapshot: ProjectSnapshot):
        json_reader = JSONSnapshotReader(self.file_path)
        snapshots = json_reader.read_snapshots()
        snapshots.append(snapshot)

        with open(self.file_path, "w") as f:
            json.dump([s.to_dict() for s in snapshots], f)

    @classmethod
    def _initialize_file(cls, snapshos_file_path) -> None:
        with open(snapshos_file_path, "w") as f:
            json.dump(cls.INITIAL_STRUCTURE, f)
