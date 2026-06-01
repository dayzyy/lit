import json
from pathlib import Path

import pytest

from core.snapshots.loader import BaseSnapshotLoader, JSONSnapshotLoader
from core.snapshots.schemas import ProjectSnapshot
from tests.unit.utils import make_valid_project_snapshot_dict


def test_snpashot_loader_raises_if_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        BaseSnapshotLoader.load_snapshots(tmp_path)


def test_json_loader_loads_successfuly(lit_path: Path):
    ss_dict_1 = make_valid_project_snapshot_dict()
    ss_dict_2 = make_valid_project_snapshot_dict()
    ss_1 = ProjectSnapshot.from_dict(ss_dict_1)
    ss_2 = ProjectSnapshot.from_dict(ss_dict_2)
    snapshots = [ss_1, ss_2]

    with open(JSONSnapshotLoader._get_file_path(lit_path), "w") as f:
        json.dump([s.to_dict() for s in snapshots], f)

    assert JSONSnapshotLoader.load_snapshots(lit_path) == snapshots


def test_snapshot_loader_raises_if_content_is_not_a_list(lit_path: Path):
    with open(JSONSnapshotLoader._get_file_path(lit_path), "w") as f:
        json.dump({"not": "a list"}, f)
