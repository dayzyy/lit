from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from commands.init import create_repo
from core.constants.directories import Directories


@pytest.fixture(autouse=True)
def patch_cwd(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)
    return tmp_path


def test_create_repo_creates_expected_directories(patch_cwd: Path):
    create_repo()

    base = patch_cwd / Directories.DirectoryNames.BASE.value

    assert base.exists()

    for d in Directories.DirectoryNames:
        if d == Directories.DirectoryNames.BASE:
            continue
        assert (base / d.value).exists()


def test_create_repo_notifies_when_repo_already_initialized(capsys: CaptureFixture[str]): # noqa: E501
    create_repo()
    create_repo()

    captured = capsys.readouterr()
    assert "Repository has already been initialized for this project!" in captured.out
