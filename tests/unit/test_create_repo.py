from pathlib import Path

import pytest

from lit.commands.init import create_repo
from lit.core.snapshots.reader import JSONSnapshotReader
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.snapshots.writer import JSONSnapshotWriter
from lit.core.structure.exceptions import RepoExistsError
from lit.core.structure.structure import RepoStructure


def test_create_repo_creates_expected_directories(tmp_path: Path):
    create_repo(cwd=tmp_path)

    base = tmp_path / RepoStructure.Directories.BASE.value

    assert base.exists()

    for d in RepoStructure.Directories:
        if d != RepoStructure.Directories.BASE:
            assert (base / d.value).exists()


def test_create_repo_raises_when_repo_already_initialized(tmp_path: Path):
    create_repo(cwd=tmp_path)
    with pytest.raises(RepoExistsError):
        create_repo(cwd=tmp_path)


def test_create_repo_initializes_snapshot_file(tmp_path: Path):
    lit_path = create_repo(
        cwd=tmp_path, writer_cls=JSONSnapshotWriter, reader_cls=JSONSnapshotReader
    )
    snapshots_file_path = SnapshotRepository._get_file_path(lit_path)

    reader = JSONSnapshotReader(snapshots_file_path)
    snapshots = reader.read_snapshots()

    assert snapshots == JSONSnapshotWriter.INITIAL_STRUCTURE
