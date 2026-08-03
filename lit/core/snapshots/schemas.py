from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self
from uuid import uuid4

from lit.core.snapshots.exceptions import (
    FileSnapshotMissingKeyError,
    FileSnapshotTypeError,
    InvalidFilePathTypeError,
    InvalidFileSnapshotTypeError,
    InvalidFilesTypeError,
    InvalidISODatetimeError,
    InvalidSnapshotIDTypeError,
    ProjectSnapshotMissingKeyError,
    ProjectSnapshotTypeError,
)


def parse_iso_datetime(string: str) -> datetime:
    """
    Parse an ISO-formatted datetime string.

    Raise `InvalidISODatetimeError` if the value is not a string or cannot
    be parsed.
    """
    if not isinstance(string, str):
        raise InvalidISODatetimeError(value=string)
    try:
        return datetime.fromisoformat(string)
    except ValueError as err:
        raise InvalidISODatetimeError(value=string) from err


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"content": self.content}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            content = data["content"]
        except KeyError as err:
            raise FileSnapshotMissingKeyError(key=err.args[0]) from err

        return cls(str(content))

    def __eq__(self, other: object) -> bool:
        # Deliberately raise instead of returning NotImplemented, so comparing
        # against an unrelated type fails loudly.
        if not isinstance(other, FileSnapshot):
            raise FileSnapshotTypeError(other_type=type(other).__name__)

        return self.content == other.content


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    files: dict[Path, FileSnapshot]
    message: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now())

    def to_dict(self) -> dict[str, Any]:
        id = self.id
        message = self.message
        # JSON keys must be strings, so Path keys are serialized as str.
        files = {str(path): snapshot.to_dict() for path, snapshot in self.files.items()}
        created_at = self.created_at.isoformat()

        return {"id": id, "message": message, "files": files, "created_at": created_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            id: str = data["id"]
            message: str = data["message"]
            raw_files: dict[str, dict[str, Any]] = data["files"]
            created_at_raw: str = data["created_at"]
        except KeyError as err:
            raise ProjectSnapshotMissingKeyError(key=err.args[0]) from err

        if not isinstance(id, str):
            raise InvalidSnapshotIDTypeError()
        if not isinstance(raw_files, dict):
            raise InvalidFilesTypeError()

        created_at = parse_iso_datetime(created_at_raw)
        files: dict[Path, FileSnapshot] = {}

        for path, ss in raw_files.items():
            if not isinstance(path, str):
                raise InvalidFilePathTypeError()
            if not isinstance(ss, dict):
                raise InvalidFileSnapshotTypeError()

            files[Path(path)] = FileSnapshot.from_dict(ss)

        return cls(id=id, message=message, files=files, created_at=created_at)

    def __eq__(self, other: object) -> bool:
        # Deliberately raise instead of returning NotImplemented, so comparing
        # against an unrelated type fails loudly.
        if not isinstance(other, ProjectSnapshot):
            raise ProjectSnapshotTypeError(other_type=type(other).__name__)

        return self.files == other.files


@dataclass(frozen=True, slots=True)
class SnapshotDiff:
    removed: set[Path]
    added: set[Path]
    modified: set[Path]
