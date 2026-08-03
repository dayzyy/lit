from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import final

from lit.core.structure.exceptions import (
    RepoNotFoundError,
    StaticNamespaceInstantiationError,
)


@final
class RepoStructure:
    """
    Static namespace for repository structure utilities.

    Cannot be instantiated; access its members statically, e.g.
    `RepoStructure.find_repo_root` or `RepoStructure.Directories`.
    """

    def __new__(cls) -> None:
        raise StaticNamespaceInstantiationError(class_name=cls.__name__)

    class Directories(StrEnum):
        """
        Represents all required directories in a Lit repository.

        Each member corresponds to a directory that must exist in a valid
        repository. `get_path` returns the full `Path` of the represented
        directory relative to the repository root.
        """

        BASE = ".lit"

        SNAPSHOTS = "snapshots"

        def get_path(self, lit_path: Path) -> Path:
            """
            Return the path to the directory this member represents.

            The repository must already be initialized: `lit_path` must be
            the path to a repository root, i.e. a `.lit` directory such as
            the one returned by `RepoStructure.find_repo_root`. For `BASE`
            `lit_path` itself is returned; every other member appends its
            directory name to `lit_path`.
            """
            if self is not self.BASE:
                lit_path = lit_path / self.value
            return lit_path

    @classmethod
    def is_valid_lit_repo(cls, root_path: Path) -> bool:
        """
        Check whether `root_path` is the root of a valid Lit repository.

        `root_path` must be a `.lit` directory; the repository is valid
        when every directory in `Directories`, except `BASE`, exists
        directly inside it.
        """
        return all(
            (root_path / dir.value).is_dir()
            for dir in cls.Directories
            if dir != cls.Directories.BASE
        )

    @classmethod
    @lru_cache
    def find_repo_root(cls, start_path: Path) -> Path:
        """
        Find and return the `.lit` directory of the repository
        containing `start_path`.

        Walks up the directory tree from `start_path` until a `.lit`
        directory is found. Raise `RepoNotFoundError` if none is found.
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
        Find and return the root of a valid Lit repository.

        Unlike `find_repo_root`, the found root must also satisfy
        `is_valid_lit_repo`. Raise `RepoNotFoundError` if no valid
        repository is found.
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
        """
        Check whether `start_path` lies within a valid Lit repository.
        """
        try:
            cls.find_valid_repo_root(start_path)
            return True
        except RepoNotFoundError:
            return False
