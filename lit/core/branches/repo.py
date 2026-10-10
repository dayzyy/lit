from pathlib import Path

from lit.config import DEFAULT_BRANCH_NAME
from lit.core.branches.exceptions import (
    BranchExistsError,
    BranchIsEmptyError,
    BranchNotFoundError,
    HeadIsEmptyError,
)
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.structure.structure import RepoStructure


class BranchRepository:
    def __init__(self, lit_path: Path, snapshot_repo: SnapshotRepository) -> None:
        self.lit_path = lit_path
        self.head_path = RepoStructure.Files.HEAD.get_path(lit_path)
        self.branches_dir = RepoStructure.Directories.BRANCHES.get_path(lit_path)
        self.snapshot_repo = snapshot_repo

    def _initialize_default_branch(self) -> None:
        self.create(DEFAULT_BRANCH_NAME)

    def branch_path(self, branch: str) -> Path:
        path = RepoStructure.branch_file_path(self.lit_path, branch)
        return path

    def branch_exists(self, branch: str) -> bool:
        path = self.branch_path(branch)
        exists = path.exists()
        return exists

    def require_branch(self, branch: str) -> Path:
        """
        Returns branch path

        Raises BranchNotFoundError if branch doesnt exist
        """
        if not self.branch_exists(branch):
            raise BranchNotFoundError(branch=branch)

        path = self.branch_path(branch)
        return path

    def read_ref(self, ref: Path) -> str | None:
        """
        Reads a snapshot reference - a file containing a snapshot_id
        """
        snapshot_id = ref.read_text().strip() or None
        return snapshot_id

    def create(self, branch: str) -> None:
        """
        Creates a new branch and points it to the snapshot currently
        resolved by HEAD, if one exists

        Raises BranchExistsError if branch already exists
        """
        if self.branch_exists(branch):
            raise BranchExistsError(branch=branch)

        branch_path = self.branch_path(branch)
        branch_path.touch()

        snapshot_id = self.resolve_head()
        if snapshot_id is not None:
            branch_path.write_text(snapshot_id)

    def tip(self, branch: str) -> str | None:
        """
        Returns ID of the snapshot the branch points to
        """
        branch_file_path = self.require_branch(branch)
        snapshot_id = self.read_ref(branch_file_path)

        if snapshot_id is None and self.empty_ref_is_invalid():
            raise BranchIsEmptyError(branch=branch)

        return snapshot_id

    def advance(self, branch: str, snapshot_id: str) -> None:
        """
        Points the branch to snapshot with given id

        Raises SnapshotNotFoundError if its not found
        """
        # Make sure that snapshot with the id exists
        self.snapshot_repo.require_snapshot(snapshot_id)

        path = self.require_branch(branch)
        path.write_text(snapshot_id.strip())

    def attach(self, branch: str) -> None:
        """
        Points HEAD at the given branch (attached HEAD)

        Raises BranchNotFoundError if the branch does not exist
        """
        self.require_branch(branch)
        self.head_path.write_text(branch.strip())

    def detach(self, snapshot_id: str) -> None:
        """
        Points HEAD directly at the given snapshot (detached HEAD)

        Raises SnapshotNotFoundError if the snapshot does not exist
        """
        self.snapshot_repo.require_snapshot(snapshot_id)
        self.head_path.write_text(snapshot_id.strip())

    def read_head_raw(self) -> str | None:
        """
        Returns the raw content of HEAD: a branch name (attached HEAD)
        or a snapshot id (detached HEAD)

        Returns None if HEAD is empty
        """
        return self.head_path.read_text().strip() or None

    def is_detached(self) -> bool:
        """
        Returns True if HEAD points directly at a snapshot instead of
        at a branch.
        An empty HEAD is not detached.
        """
        head_content = self.read_head_raw()
        if head_content is None:
            return False

        return not self.branch_exists(head_content)

    def current_branch(self) -> str | None:
        """
        Returns the name of the checked-out branch

        Returns None if HEAD is detached or empty
        """
        head_content = self.read_head_raw()
        if head_content is None:
            return None

        return head_content if self.branch_exists(head_content) else None

    def resolve_head(self) -> str | None:
        """
        Returns ID of the snapshot HEAD points to

        When HEAD is attached to a branch, the branch is followed;
        when detached, HEAD's content is the snapshot id itself.
        Returns None on an empty HEAD, unless at least 1 snapshot exists.

        Raises BranchIsEmptyError if HEAD is attached to an empty branch
        while at least 1 snapshot exists

        Raises HeadIsEmptyError if HEAD itself is empty while at least
        1 snapshot exists
        """
        head_content = self.read_head_raw()

        if head_content is None:
            if self.empty_ref_is_invalid():
                raise HeadIsEmptyError
            return None

        if not self.branch_exists(head_content):
            return head_content

        branch_path = self.branch_path(head_content)
        snapshot_id = self.read_ref(branch_path)
        if snapshot_id is None and self.empty_ref_is_invalid():
            raise BranchIsEmptyError(branch=head_content)

        return snapshot_id

    def empty_ref_is_invalid(self) -> bool:
        snapshot_id = self.snapshot_repo.latest()
        return snapshot_id is not None
