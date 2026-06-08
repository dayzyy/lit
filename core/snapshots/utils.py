from pathlib import Path

from core.snapshots.exceptions import SnapshotFileNotFoundError


def ensure_snapshot_file_exists(file_path: Path):
    if not file_path.exists():
        raise SnapshotFileNotFoundError
