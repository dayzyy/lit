import json
from abc import ABC, abstractmethod
from pathlib import Path

from core.snapshots.reader import JSONSnapshotReader
from core.snapshots.schemas import ProjectSnapshot


class BaseSnapshotWriter(ABC):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    @abstractmethod
    def add(self, snapshot: ProjectSnapshot):
        """
        This method must save the snapshot in the configured file ('self.file_path')
        """
        raise NotImplementedError


class JSONSnapshotWriter(BaseSnapshotWriter):
    def add(self, snapshot: ProjectSnapshot):
        json_reader = JSONSnapshotReader(self.file_path)
        snapshots = json_reader.read_snapshots()
        snapshots.append(snapshot)

        with open(self.file_path, "w") as f:
            json.dump(snapshots, f)
