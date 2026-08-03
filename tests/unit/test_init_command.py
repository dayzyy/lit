from pathlib import Path

import pytest

from lit.cli.commands import InitCommand
from lit.core.snapshots.reader import JSONSnapshotReader
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.snapshots.writer import JSONSnapshotWriter
from lit.core.structure.exceptions import RepoExistsError
from lit.core.structure.structure import RepoStructure


def test_init_command_creates_expected_directories(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()

    base = tmp_path / RepoStructure.Directories.BASE.value

    assert base.exists()

    for d in RepoStructure.Directories:
        if d != RepoStructure.Directories.BASE:
            assert (base / d.value).exists()


def test_init_command_raises_when_repo_already_initialized(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()
    with pytest.raises(RepoExistsError):
        InitCommand(cwd=tmp_path).execute()


def test_init_command_initializes_snapshot_file(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()
    lit_path = RepoStructure.find_valid_repo_root(tmp_path)
    snapshots_file_path = SnapshotRepository._get_file_path(lit_path)

    reader = JSONSnapshotReader(snapshots_file_path)
    snapshots = reader.read_snapshots()

    assert snapshots == JSONSnapshotWriter.INITIAL_STRUCTURE
