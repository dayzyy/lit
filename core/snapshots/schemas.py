from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self


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
            last_modified: datetime = datetime.fromisoformat(data["last_modified"])
        except KeyError as err:
            raise ValueError(f"ProjectSnapshot missing key: {err.args[0]}") from err

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
            files: dict[Path, FileSnapshot] = {
                Path(path): FileSnapshot.from_dict(f_ss)
                for path, f_ss in raw_files.items()
            }
            created_at: datetime = datetime.fromisoformat(data["created_at"])
        except KeyError as err:
            raise ValueError(f"ProjectSnapshot missing key: {err.args[0]}") from err

        return cls(id=id, files=files, created_at=created_at)
