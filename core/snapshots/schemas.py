from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self
from uuid import uuid4

from core.snapshots.exceptions import InvalidSnapshotSchemaError


def parse_iso_datetime(string: str) -> datetime:
    if not isinstance(string, str):
        raise InvalidSnapshotSchemaError(f"'{string}' is not an ISO formated string!")
    try:
        time = datetime.fromisoformat(string)
        return time
    except Exception as err:
        raise InvalidSnapshotSchemaError(
            f"'{string}' is not an ISO formated string!"
        ) from err


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
            raise InvalidSnapshotSchemaError(
                f"FileSnapshot missing key: {err.args[0]}"
            ) from err

        return cls(str(content))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileSnapshot):
            raise TypeError(
                f"'other' must be 'FileSnapshot', got {type(other).__name__}"
            )

        return self.content == other.content


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    files: dict[Path, FileSnapshot]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now())

    def to_dict(self) -> dict[str, Any]:
        id = self.id
        files = {str(path): snapshot.to_dict() for path, snapshot in self.files.items()}
        created_at = self.created_at.isoformat()

        return {"id": id, "files": files, "created_at": created_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            id: str = data["id"]
            raw_files: dict[str, dict[str, Any]] = data["files"]
            created_at_raw: str = data["created_at"]
        except KeyError as err:
            raise InvalidSnapshotSchemaError(
                f"ProjectSnapshot missing key: {err.args[0]}"
            ) from err

        if not isinstance(id, str):
            raise InvalidSnapshotSchemaError("'id' must be a string!")
        if not isinstance(raw_files, dict):
            raise InvalidSnapshotSchemaError("'files' must be a dictionary!")

        created_at = parse_iso_datetime(created_at_raw)
        files: dict[Path, FileSnapshot] = {}

        for path, ss in raw_files.items():
            if not isinstance(path, str):
                raise InvalidSnapshotSchemaError("file path must be a string!")
            if not isinstance(ss, dict):
                raise InvalidSnapshotSchemaError("file snapshot must be a dictionary!")

            files[Path(path)] = FileSnapshot.from_dict(ss)

        return cls(id=id, files=files, created_at=created_at)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectSnapshot):
            raise TypeError(
                f"'other' must be 'ProjectSnapshot', got {type(other).__name__}"
            )

        return self.files == other.files
