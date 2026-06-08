from pathlib import Path

import pytest

from commands.init import create_repo
from core.snapshots.repo import SnapshotRepository
from core.structure.structure import RepoStructure


@pytest.fixture
def lit_path(tmp_path: Path) -> Path:
    lit_path = create_repo(tmp_path)
    return lit_path


@pytest.fixture
def snapshots_path(lit_path: Path) -> Path:
    path = (
        RepoStructure.Directories.SNAPSHOTS.get_path(lit_path)
        / SnapshotRepository._FILE_NAME
    )
    path.touch()
    return path
