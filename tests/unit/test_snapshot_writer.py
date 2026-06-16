from pathlib import Path

import pytest

from core.snapshots.reader import JSONSnapshotReader
from core.snapshots.schemas import ProjectSnapshot
from core.snapshots.writer import JSONSnapshotWriter
from tests.unit.utils import make_valid_project_snapshot_dict


def test_add_raises_for_invalid_snapshot(snapshots_path: Path):
    writer = JSONSnapshotWriter(snapshots_path)
    snapshot = "not a ProjectSnapshot"
    with pytest.raises(TypeError):
        writer.add(snapshot)


def test_add_appends_snapshot_to_empty_storage(snapshots_path: Path):
    snapshot = ProjectSnapshot.from_dict(make_valid_project_snapshot_dict())
    writer = JSONSnapshotWriter(snapshots_path)
    writer.add(snapshot)

    reader = JSONSnapshotReader(snapshots_path)
    snapshots = reader.read_snapshots()

    assert snapshots == [snapshot]


def test_add_preserves_existing_snapshots(snapshots_path: Path):
    snapshot_1 = ProjectSnapshot.from_dict(make_valid_project_snapshot_dict())
    snapshot_2 = ProjectSnapshot.from_dict(make_valid_project_snapshot_dict())

    writer = JSONSnapshotWriter(snapshots_path)

    writer.add(snapshot_1)
    writer.add(snapshot_2)

    reader = JSONSnapshotReader(snapshots_path)
    snapshots = reader.read_snapshots()

    assert snapshots == [snapshot_1, snapshot_2]
