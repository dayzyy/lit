from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from commands.init import create_repo
from core.structure.structure import RepoStructure


class LitCommand(ABC):
    """
    Base class for all CLI commands.

    Commands are executed through the public `run()` method, which
    provides a stable entry point and allows common execution logic
    to be introduced in one place.

    Subclasses must implement `execute()` with the command-specific
    behavior.
    """

    def __init__(self, cwd: Path | None = None):
        self.cwd = cwd or Path.cwd()

    @final
    def run(self):
        self.execute()

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class RepoCommand(LitCommand):
    """
    Base class for commands that operate on an existing repository.

    During initialization, the repository root is discovered and
    stored in `lit_path`. This guarantees that subclasses have
    access to a valid repository location before execution.

    Commands such as `status`, `diff`, and `snapshot` should inherit
    from this class. Commands that can be executed outside of a
    repository, such as `init`, should inherit directly from
    `LitCommand`.
    """

    lit_path: Path

    def __init__(self, cwd: Path | None = None):
        super().__init__(cwd)
        self.lit_path = RepoStructure.find_valid_repo_root(self.cwd)


class InitCommand(LitCommand):
    def execute():
        create_repo()
