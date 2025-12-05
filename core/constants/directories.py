from enum import StrEnum
from pathlib import Path

from core.utils.decorators import classproperty


class Directories:
    class DirectoryNames(StrEnum):
        BASE = ".lit"

        OBJECTS = "objects" # File content storage
        SNAPSHOTS = "snapshots" # File name/object mapping

    @classproperty
    def repo_dir(cls) -> Path:
        cwd = Path.cwd()
        return cwd / cls.DirectoryNames.BASE.value

    @classproperty
    def repo_dirs(cls) -> list[Path]:
        dir_names: list[str] = [dir.value for dir in cls.DirectoryNames if dir != cls.DirectoryNames.BASE]

        return [cls.repo_dir / name for name in dir_names]
