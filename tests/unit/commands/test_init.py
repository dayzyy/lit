from pathlib import Path

import pytest

from lit.cli.commands import InitCommand
from lit.core.constants import DEFAULT_BRANCH_NAME
from lit.core.snapshots.reader import JSONSnapshotReader
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.snapshots.writer import JSONSnapshotWriter
from lit.core.structure.exceptions import RepoExistsError
from lit.core.structure.structure import RepoStructure


def test_init_command_creates_expected_directories_and_files(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()
    lit_path = tmp_path / ".lit"

    for d in RepoStructure.Directories:
        if d != RepoStructure.Directories.BASE:
            assert d.get_path(lit_path).exists()

    for f in RepoStructure.Files:
        assert f.get_path(lit_path).exists()


def test_init_commands_creates_default_branch(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()
    lit_path = tmp_path / ".lit"

    default_branch_path = RepoStructure.branch_file_path(lit_path, DEFAULT_BRANCH_NAME)
    assert default_branch_path.exists()


def test_init_command_results_in_valid_lit_repo(tmp_path: Path):
    InitCommand(cwd=tmp_path).execute()

    lit_path = RepoStructure.find_valid_repo_root(tmp_path)

    assert RepoStructure.is_valid_lit_repo(lit_path)


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
