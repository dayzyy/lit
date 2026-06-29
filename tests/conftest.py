from dataclasses import dataclass
from pathlib import Path

import pytest

from lit.commands.init import create_repo
from lit.config import SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.structure.structure import RepoStructure


@dataclass(frozen=True, slots=True)
class RepoContext:
    lit_path: Path
    snapshot_repo: SnapshotRepository

    @property
    def root(self) -> Path:
        return self.lit_path.parent


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
    return path


@pytest.fixture
def repo_context(lit_path: Path) -> RepoContext:
    snapshot_repo = SnapshotRepository(
        lit_path, SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
    )

    return RepoContext(lit_path=lit_path, snapshot_repo=snapshot_repo)
