import json
from abc import ABC, abstractmethod
from pathlib import Path

from core.snapshots.reader import JSONSnapshotReader
from core.snapshots.schemas import ProjectSnapshot
from core.snapshots.utils import ensure_snapshot_file_exists


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
        ensure_snapshot_file_exists(file_path)
        self.file_path = file_path

    @abstractmethod
    def add(self, snapshot: ProjectSnapshot) -> None:
        """
        Persist a snapshot to the configured storage file.
        """
        raise NotImplementedError

    @abstractmethod
    def init(self) -> None:
        """
        Initialize the snapshot storage file with the format's
        default structure.
        """
        raise NotImplementedError


class JSONSnapshotWriter(BaseSnapshotWriter):
    def add(self, snapshot: ProjectSnapshot):
        json_reader = JSONSnapshotReader(self.file_path)
        snapshots = json_reader.read_snapshots()
        snapshots.append(snapshot)

        with open(self.file_path, "w") as f:
            json.dump(snapshots, f)
