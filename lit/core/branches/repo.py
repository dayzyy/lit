from pathlib import Path

from lit.config import DEFAULT_BRANCH_NAME
from lit.core.branches.exceptions import BranchExistsError, BranchNotFoundError
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.structure.structure import RepoStructure


class BranchRepository:
    def __init__(self, lit_path: Path, snapshot_repo: SnapshotRepository) -> None:
        self.lit_path = lit_path
        self.head_path = RepoStructure.Files.HEAD.get_path(lit_path)
        self.branches_dir = RepoStructure.Directories.BRANCHES.get_path(lit_path)
        self.snapshot_repo = snapshot_repo

    def _initialize_default_branch(self):
        self.create(DEFAULT_BRANCH_NAME)

    def _branch_exists(self, branch: str) -> bool:
        branch_file_path = RepoStructure.branch_file_path(self.lit_path, branch)
        return branch_file_path.exists()

    def create(self, branch):
        if self._branch_exists(branch):
            raise BranchExistsError(branch=branch)

        branch_path = RepoStructure.branch_file_path(self.lit_path, branch)
        branch_path.touch()

        # Point the branch to the current snapshot
        current_snapshot_id = self.tip(self.current())
        self.advance(branch, current_snapshot_id)

    def current(self):
        # Returns branch that is currently checked out
        current_branch = self.read_head()
        return current_branch

    def tip(self, branch: str):
        # Returns ID of the snapshot the branch points to
        if not self._branch_exists(branch):
            raise BranchNotFoundError(branch=branch)

        branch_file_path = RepoStructure.branch_file_path(self.lit_path, branch)
        return branch_file_path.read_text().strip()

    def advance(self, branch, snapshot_id):
        # Make the `branch` point to the snapshot with `snapshot_id` id
        if not self._branch_exists(branch):
            raise BranchNotFoundError(branch=branch)

        branch_file_path = RepoStructure.branch_file_path(self.lit_path, branch)
        branch_file_path.write_text(snapshot_id)

    def write_head(self, branch: str):
        if not self._branch_exists(branch):
            raise BranchNotFoundError(branch=branch)

        self.head_path.write_text(branch)

    def read_head(self):
        return self.head_path.read_text().strip()
