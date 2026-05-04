from pathlib import Path

import pytest

from commands.init import create_repo


@pytest.fixture
def lit_path(tmp_path: Path) -> Path:
    lit_path = create_repo(tmp_path)
    return lit_path
