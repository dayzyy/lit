import datetime
import json
from pathlib import Path

from core.snapshots.loader import JSONSnapshotLoader
from core.snapshots.schemas import FileSnapshot, ProjectSnapshot


def test_json_loader_loads_correctly(lit_path: Path):
    # Create dummy snapshots
    file_1_ss = FileSnapshot(
        ["empty", "changed", "changed again"], datetime.datetime.now()
    )
    file_2_ss = FileSnapshot(
        ["hallow", "modified", "modified again"], datetime.datetime.now()
    )

    snapshot = ProjectSnapshot(
        "0",
        {Path("./file_1"): file_1_ss, Path("./file_2"): file_2_ss},
        datetime.datetime.now(),
    )

    with open(JSONSnapshotLoader._get_file_path(lit_path), "w") as f:
        json.dump([snapshot.to_dict()], f)

    assert JSONSnapshotLoader.load_snapshots(lit_path) == [snapshot]
