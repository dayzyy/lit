import datetime
from typing import Any

now = datetime.datetime.now().isoformat()


def make_valid_file_snapshot_dict() -> dict[str, str]:
    snapshot = {
        "content": "contents of a file",
    }
    return snapshot


def make_valid_project_snapshot_dict() -> dict[str, Any]:
    snapshot = {
        "id": "0",
        "files": {
            "./path/to/file_1": make_valid_file_snapshot_dict(),
            "./path/to/file_2": make_valid_file_snapshot_dict(),
        },
        "created_at": now,
    }
    return snapshot
