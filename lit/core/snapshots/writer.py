import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from lit.core.snapshots.exceptions import InvalidSnapshotTypeError
from lit.core.snapshots.reader import JSONSnapshotReader
from lit.core.snapshots.schemas import ProjectSnapshot


class BaseSnapshotWriter(ABC):
    """
    Base class for writers that persist snapshots to a single storage file.

    The storage file must be initialized via `_initialize_file` before the
    first snapshot is appended. Subclasses set `INITIAL_STRUCTURE` to the
    content written to a newly created file and implement `_append` to
    persist a snapshot. `append` is final.
    """

    INITIAL_STRUCTURE = None

    def __init__(self, file_path: Path):
        """
        Store the path to the snapshot storage file.
        """
        self.file_path = file_path

    @final
    def append(self, snapshot: ProjectSnapshot) -> None:
        """
        Append a snapshot to the configured storage file.

        Raise `InvalidSnapshotTypeError` if `snapshot` is not a
        `ProjectSnapshot`.
        """
        if not isinstance(snapshot, ProjectSnapshot):
            raise InvalidSnapshotTypeError(snapshot_type=type(snapshot).__name__)

        self._append(snapshot)

    @abstractmethod
    def _append(self, snapshot: ProjectSnapshot) -> None:
        """
        Persist a snapshot to the configured storage file.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _initialize_file(cls, snapshots_file_path: Path) -> None:
        """
        Initialize the snapshot storage file with the format's default
        structure.
        """
        raise NotImplementedError


class JSONSnapshotWriter(BaseSnapshotWriter):
    """
    Appends snapshots to a JSON storage file.
    """

    INITIAL_STRUCTURE = []

    def _append(self, snapshot: ProjectSnapshot) -> None:
        json_reader = JSONSnapshotReader(self.file_path)
        snapshots = json_reader.read_snapshots()
        snapshots.append(snapshot)

        with open(self.file_path, "w") as f:
            json.dump([s.to_dict() for s in snapshots], f)

    @classmethod
    def _initialize_file(cls, snapshots_file_path: Path) -> None:
        with open(snapshots_file_path, "w") as f:
            json.dump(cls.INITIAL_STRUCTURE, f)
