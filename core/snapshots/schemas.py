from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self

from core.snapshots.exceptions import InvalidSnapshotSchemaError


def parse_iso_datetime(string: str) -> datetime:
    if not isinstance(string, str):
        raise InvalidSnapshotSchemaError(
            "'last_modified' must be an ISO formated string!"
        )
    try:
        time = datetime.fromisoformat(string)
        return time
    except Exception as err:
        raise InvalidSnapshotSchemaError(
            "'last_modified' must be ISO formated!"
        ) from err


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    history: list[str]
    last_modified: datetime

    def to_dict(self) -> dict[str, Any]:
        history = self.history
        last_modified = self.last_modified.isoformat()

        return {"history": history, "last_modified": last_modified}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            history: list[str] = data["history"]
            last_modified_raw: str = data["last_modified"]
        except KeyError as err:
            raise InvalidSnapshotSchemaError(
                f"FileSnapshot missing key: {err.args[0]}"
            ) from err

        if not isinstance(history, list):
            raise InvalidSnapshotSchemaError("'history' must be a list!")

        last_modified = parse_iso_datetime(last_modified_raw)

        return cls(history=history, last_modified=last_modified)


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    id: str
    files: dict[Path, FileSnapshot]
    created_at: datetime = field(default_factory=datetime.now)

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
