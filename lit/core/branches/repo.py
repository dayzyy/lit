from pathlib import Path

from lit.config import DEFAULT_BRANCH_NAME
from lit.core.branches.exceptions import (
    BranchExistsError,
    BranchIsEmptyError,
    BranchNotFoundError,
    HeadIsEmptyError,
    RefIsEmptyError,
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

    def get_branch_path(self, branch: str) -> Path:
        path = RepoStructure.branch_file_path(self.lit_path, branch)
        return path

    def branch_exists(self, branch: str) -> bool:
        branch_file_path = self.get_branch_path(branch)
        return branch_file_path.exists()

    def require_branch(self, branch: str) -> Path:
        """
        Returns the path to the branch file

        Raises BranchNotFoundError if the branch does not exist
        """
        branch_file_path = self.get_branch_path(branch)
        if not branch_file_path.exists():
            raise BranchNotFoundError(branch=branch)
        return branch_file_path

    def read_ref(self, ref: Path) -> str | None:
        """
        Reads a snapshot reference - a file containing a snapshot_id
        """
        snapshot_id = ref.read_text().strip() or None
        return snapshot_id

    def read_and_validate_ref(self, ref: Path) -> str | None:
        """
        Validates a snapshot reference

        Returns the snapshot_id

        Raises RefIsEmptyError if at least 1 snapshot exists,
        but the ref file is empty
        """
        snapshot_id = self.read_ref(ref)
        if snapshot_id is None and self.snapshot_repo.latest() is not None:
            raise RefIsEmptyError

        return snapshot_id

    def create(self, branch: str) -> None:
        """
        Creates a new branch and points it to the snapshot currently
        resolved by HEAD, if one exists
        """
        if self.branch_exists(branch):
            raise BranchExistsError(branch=branch)

        branch_path = self.get_branch_path(branch)
        branch_path.touch()

        snapshot_id = self.resolve_head()
        if snapshot_id is not None:
            branch_path.write_text(snapshot_id)

    def tip(self, branch: str) -> str | None:
        """
        Returns ID of the snapshot the branch points to
        """
        branch_file_path = self.require_branch(branch)

        try:
            snapshot_id = self.read_and_validate_ref(branch_file_path)
        except RefIsEmptyError:
            raise BranchIsEmptyError(branch=branch)

        return snapshot_id

    def advance(self, branch: str, snapshot_id: str) -> None:
        """
        Points the branch to snapshot with given id

        Raises SnapshotNotFoundError if its not found
        """
        # Make sure that snapshot with the id exists
        self.snapshot_repo.get(snapshot_id, raise_if_not_found=True)

        self.require_branch(branch).write_text(snapshot_id)

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
        self.snapshot_repo.get(snapshot_id, raise_if_not_found=True)
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
        if head_content is None or not self.branch_exists(head_content):
            return None
        return head_content

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
            if self.snapshot_repo.latest() is not None:
                raise HeadIsEmptyError
            return None

        if not self.branch_exists(head_content):
            return head_content

        try:
            return self.read_and_validate_ref(self.get_branch_path(head_content))
        except RefIsEmptyError:
            raise BranchIsEmptyError(branch=head_content)
