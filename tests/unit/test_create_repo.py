from pathlib import Path

import pytest

from commands.init import create_repo
from core.structure.exceptions import RepoExistsError
from core.structure.structure import RepoStructure


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
