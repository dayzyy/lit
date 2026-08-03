import json
from abc import ABC, abstractmethod
from functools import wraps
from pathlib import Path
from typing import Any, final

from lit.core.commons.exceptions import ForbiddenOverrideError
from lit.core.snapshots.exceptions import (
    InvalidParseResultError,
    SnapshotFileNotFoundError,
)
from lit.core.snapshots.schemas import ProjectSnapshot


def _handle_file_not_found(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError as err:
            raise SnapshotFileNotFoundError from err

    return wrapper


class BaseSnapshotReader(ABC):
    """
    Base class for readers that load snapshots from a single storage file.

    Reading the storage is delegated to `_parse_raw_snapshots`, which
    subclasses must implement and may do however the storage format allows
    (e.g. plain file reading for JSON, a database driver for SQLite).
    `read_snapshots` turns the returned snapshot dictionaries into
    `ProjectSnapshot` objects and raises `SnapshotFileNotFoundError` if the
    storage file does not exist.
    """

    _FORBIDDEN_OVERRIDES = ("read_snapshots",)

    def __init_subclass__(cls) -> None:
        """
        Prevent subclasses from overriding `read_snapshots`.
        """
        for attr_name in cls._FORBIDDEN_OVERRIDES:
            if cls.__dict__.get(attr_name) is not None:
                raise ForbiddenOverrideError(
                    namespace=cls.__name__, attr_name=attr_name
                )

        return super().__init_subclass__()

    def __init__(self, file_path: Path):
        """
        Store the path to the snapshot storage file.
        """
        self.file_path = file_path

    @abstractmethod
    def _parse_raw_snapshots(self) -> list[dict[str, Any]]:
        """
        Read and parse the snapshot storage into a list of snapshot
        dictionaries. Must be implemented by subclasses.
        """
        raise NotImplementedError

    @final
    @_handle_file_not_found
    def read_snapshots(self) -> list[ProjectSnapshot]:
        """
        Read all snapshots from the storage file as `ProjectSnapshot`
        objects. Raise `SnapshotFileNotFoundError` if the storage file
        does not exist.
        """
        parsed_snapshots = self._parse_raw_snapshots()

        if not isinstance(parsed_snapshots, list):
            raise InvalidParseResultError(reader_class=self.__class__.__name__)

        return [ProjectSnapshot.from_dict(ss) for ss in parsed_snapshots]


class JSONSnapshotReader(BaseSnapshotReader):
    """
    Reads snapshots from a JSON file.
    """

    def _parse_raw_snapshots(self) -> list[dict[str, Any]]:
        with open(self.file_path, "r") as f:
            return json.load(f)
