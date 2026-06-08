import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, final

from core.commons.exeptions import ForbiddenOverrideError
from core.snapshots.exceptions import InvalidSnapshotSchemaError
from core.snapshots.schemas import ProjectSnapshot
from core.snapshots.utils import ensure_snapshot_file_exists


class BaseSnapshotReader(ABC):
    """
    A Base Abstract Class for SnapshotLoaders
    Child classes must implement the load method
    """

    _FORBIDDEN_OVERRIDES = (
        "_read_raw_snapshots",
        "_read_snapshots",
    )

    def __init_subclass__(cls) -> None:
        for attr_name in cls._FORBIDDEN_OVERRIDES:
            if cls.__dict__.get(attr_name) is not None:
                raise ForbiddenOverrideError(
                    namespace=cls.__name__, attr_name=attr_name
                )

        return super().__init_subclass__()

    def __init__(self, file_path: Path):
        ensure_snapshot_file_exists(file_path)
        self.file_path = file_path

    @final
    def _read_raw_snapshots(self) -> str:
        with open(self.file_path, "r") as snapshots:
            return snapshots.read()

    @abstractmethod
    def _parse_raw_snapshots(self, raw_snapshots: str) -> list[dict[str, Any]]:
        """
        This method must turn 'raw_snapshots' into a python dictionary
        """
        raise NotImplementedError

    @final
    def read_snapshots(self) -> list[ProjectSnapshot]:
        raw_snapshots = self._read_raw_snapshots()
        parsed_snapshots = self._parse_raw_snapshots(raw_snapshots)

        if not isinstance(parsed_snapshots, list):
            raise InvalidSnapshotSchemaError(
                f"{self.__class__.__name__}._parse_raw_snapshots must return a list!"
            )

        return [ProjectSnapshot.from_dict(ss) for ss in parsed_snapshots]


class JSONSnapshotReader(BaseSnapshotReader):
    def _parse_raw_snapshots(self, raw_snapshots: str) -> list[dict[str, Any]]:
        return json.loads(raw_snapshots)
