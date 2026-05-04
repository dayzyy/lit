from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import final

from core.structure.exceptions import RepoNotFoundError


@final
class RepoStructure:
    def __new__(cls) -> None:
        raise TypeError(f"Static namespace {cls.__name__} can not be instantiated!")

    class Directories(StrEnum):
        """
        Represents all required directories in a Lit repository.

        Each member corresponds to a directory that must exist in a valid repository.
        Provides a `get_path` method to get the full Path object
        relative to the repository root.
        """

        BASE = ".lit"

        SNAPSHOTS = "snapshots"

        def get_path(self, lit_path: Path) -> Path:
            """
            Return path to represented dir based on provided lit_path
            """
            if self is not self.BASE:
                lit_path = lit_path / self.value
            print(lit_path)
            return lit_path

    @classmethod
    def is_valid_lit_repo(cls, root_path: Path) -> bool:
        return all(
            (root_path / dir.value).is_dir()
            for dir in cls.Directories
            if dir != cls.Directories.BASE
        )

    @classmethod
    @lru_cache
    def find_repo_root(cls, start_path: Path) -> Path:
        """
        Find and return path to root of a Lit repository (.lit/).
        Raise RepoNotFoundError if fail to find.
        """
        lit_path = start_path / cls.Directories.BASE.value
        while start_path.parent != start_path:
            if lit_path.exists():
                return lit_path

            start_path = start_path.parent
        raise RepoNotFoundError

    @classmethod
    @lru_cache
    def find_valid_repo_root(cls, start_path: Path) -> Path:
        """
        Find and return path to root of a VALID Lit repository
        (see cls.is_valid_lit_repo).
        Raise RepoNotFoundError if fail to find.
        """
        while True:
            root = cls.find_repo_root(start_path)
            if cls.is_valid_lit_repo(root):
                return root
            if start_path.parent == start_path:
                break
            start_path = root.parent.parent
        raise RepoNotFoundError

    @classmethod
    def repo_exists(cls, start_path: Path) -> bool:
        try:
            cls.find_valid_repo_root(start_path)
            return True
        except RepoNotFoundError:
            return False
