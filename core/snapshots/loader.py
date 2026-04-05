import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, final

from core.commons.exeptions import ForbiddenOverrideError
from core.snapshots.schemas import ProjectSnapshot
from core.structure.structure import RepoStructure


class BaseSnapshotLoader(ABC):
    """
    A Base Abstract Class for SnapshotLoaders
    Child classes must implement the load method
    """

    _FILE_NAME = "snapshots"
    _FORBIDDEN_OVERRIDES = (
        "_get_file_path",
        "_load_raw_snapshots",
    )

    def __init_subclass__(cls) -> None:
        for attr_name in cls._FORBIDDEN_OVERRIDES:
            if cls.__dict__.get(attr_name) is not None:
                raise ForbiddenOverrideError(
                    namespace=cls.__name__, attr_name=attr_name
                )

        return super().__init_subclass__()

    @classmethod
    @final
    def _get_file_path(cls, root_path: Path) -> Path:
        return RepoStructure.Directories.SNAPSHOTS.get_path(root_path) / cls._FILE_NAME

    @classmethod
    @final
    def _load_raw_snapshots(cls, root_path: Path) -> str:
        with open(cls._get_file_path(root_path), "r") as snapshots:
            return snapshots.read()

    @classmethod
    @abstractmethod
    def _parse_raw_snapshots(cls, raw_snapshots: str) -> list[dict[str, Any]]:
        """
        This method must turn 'raw_snapshots' into a python dictionary
        """
        raise NotImplementedError

    @classmethod
    def load_snapshots(cls, root_path: Path) -> list[ProjectSnapshot]:
        raw_snapshots = cls._load_raw_snapshots(root_path)
        parsed_snapshots = cls._parse_raw_snapshots(raw_snapshots)
        return [ProjectSnapshot.from_dict(ss) for ss in parsed_snapshots]


class JSONSnapshotLoader(BaseSnapshotLoader):
    _FILE_NAME = "snapshots.json"

    @classmethod
    def _parse_raw_snapshots(cls, raw_snapshots: str) -> list[dict[str, Any]]:
        return json.loads(raw_snapshots)
