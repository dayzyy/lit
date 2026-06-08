import json
from pathlib import Path

import pytest

from core.snapshots.exceptions import (
    InvalidSnapshotSchemaError,
    SnapshotFileNotFoundError,
)
from core.snapshots.reader import JSONSnapshotReader
from core.snapshots.schemas import ProjectSnapshot
from tests.unit.utils import make_valid_project_snapshot_dict


def test_snpashot_reader_raises_if_file_not_found(tmp_path: Path):
    with pytest.raises(SnapshotFileNotFoundError):
        reader = JSONSnapshotReader(tmp_path / "invalid")
        reader.read_snapshots()


def test_json_reader_loads_successfuly(snapshots_path: Path):
    ss_dict_1 = make_valid_project_snapshot_dict()
    ss_dict_2 = make_valid_project_snapshot_dict()
    ss_1 = ProjectSnapshot.from_dict(ss_dict_1)
    ss_2 = ProjectSnapshot.from_dict(ss_dict_2)
    snapshots = [ss_1, ss_2]

    json_reader = JSONSnapshotReader(snapshots_path)
    with open(snapshots_path, "w") as f:
        json.dump([s.to_dict() for s in snapshots], f)

    assert json_reader.read_snapshots() == snapshots


def test_snapshot_reader_raises_if_content_is_not_a_list(snapshots_path: Path):
    with open(snapshots_path, "w") as f:
        json.dump({"not": "a list"}, f)

    json_reader = JSONSnapshotReader(snapshots_path)
    with pytest.raises(InvalidSnapshotSchemaError):
        json_reader.read_snapshots()
