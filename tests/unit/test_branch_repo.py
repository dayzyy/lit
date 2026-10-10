import pytest

from lit.config import DEFAULT_BRANCH_NAME
from lit.core.branches.exceptions import (
    BranchExistsError,
    BranchIsEmptyError,
    BranchNotFoundError,
    HeadIsEmptyError,
)
from lit.core.branches.repo import BranchRepository
from lit.core.snapshots.exceptions import SnapshotNotFoundError
from lit.core.snapshots.schemas import ProjectSnapshot
from lit.core.structure.structure import RepoStructure
from tests.conftest import RepoContext
from tests.unit.utils import make_valid_project_snapshot_dict

OTHER_BRANCH = "feature"


@pytest.fixture
def branch_repo(repo_context: RepoContext) -> BranchRepository:
    return BranchRepository(repo_context.lit_path, repo_context.snapshot_repo)


def add_snapshot(repo_context: RepoContext) -> str:
    snapshot = ProjectSnapshot.from_dict(make_valid_project_snapshot_dict())
    repo_context.snapshot_repo.add(snapshot)
    return snapshot.id


class TestBranchExists:
    def test_true_for_existing_branch(self, branch_repo: BranchRepository):
        assert branch_repo.branch_exists(DEFAULT_BRANCH_NAME)

    def test_false_for_missing_branch(self, branch_repo: BranchRepository):
        assert not branch_repo.branch_exists(OTHER_BRANCH)


class TestBranchPath:
    def test_returns_path_in_branches_dir(
        self, branch_repo: BranchRepository, repo_context: RepoContext
    ):
        path = branch_repo.branch_path(DEFAULT_BRANCH_NAME)

        expected = (
            RepoStructure.Directories.BRANCHES.get_path(repo_context.lit_path)
            / DEFAULT_BRANCH_NAME
        )
        assert path == expected


class TestRequireBranch:
    def test_returns_path_for_existing_branch(self, branch_repo: BranchRepository):
        path = branch_repo.require_branch(DEFAULT_BRANCH_NAME)
        assert path == branch_repo.branch_path(DEFAULT_BRANCH_NAME)

    def test_raises_for_missing_branch(self, branch_repo: BranchRepository):
        with pytest.raises(BranchNotFoundError):
            branch_repo.require_branch(OTHER_BRANCH)

    def test_raises_with_branch_name_in_message(self, branch_repo: BranchRepository):
        with pytest.raises(BranchNotFoundError) as exc_info:
            branch_repo.require_branch(OTHER_BRANCH)
        assert OTHER_BRANCH in str(exc_info.value)


class TestReadRef:
    def test_reads_value(self, branch_repo: BranchRepository):
        ref = branch_repo.branch_path(DEFAULT_BRANCH_NAME)
        ref.write_text("123")
        assert branch_repo.read_ref(ref) == "123"

    def test_strips_surrounding_whitespace(self, branch_repo: BranchRepository):
        ref = branch_repo.branch_path(DEFAULT_BRANCH_NAME)
        ref.write_text("  123\n")
        assert branch_repo.read_ref(ref) == "123"

    def test_returns_none_when_empty(self, branch_repo: BranchRepository):
        ref = branch_repo.branch_path(DEFAULT_BRANCH_NAME)
        ref.write_text("")
        assert branch_repo.read_ref(ref) is None

    def test_returns_none_when_whitespace_only(self, branch_repo: BranchRepository):
        ref = branch_repo.branch_path(DEFAULT_BRANCH_NAME)
        ref.write_text("  \n")
        assert branch_repo.read_ref(ref) is None


class TestCreate:
    def test_creates_branch(self, branch_repo: BranchRepository):
        branch_repo.create(OTHER_BRANCH)
        assert branch_repo.branch_exists(OTHER_BRANCH)

    def test_raises_if_branch_exists(self, branch_repo: BranchRepository):
        with pytest.raises(BranchExistsError):
            branch_repo.create(DEFAULT_BRANCH_NAME)

    def test_raises_with_branch_name_in_message(self, branch_repo: BranchRepository):
        with pytest.raises(BranchExistsError) as exc_info:
            branch_repo.create(DEFAULT_BRANCH_NAME)
        assert DEFAULT_BRANCH_NAME in str(exc_info.value)

    def test_new_branch_is_empty_on_fresh_repo(self, branch_repo: BranchRepository):
        branch_repo.create(OTHER_BRANCH)
        assert branch_repo.tip(OTHER_BRANCH) is None

    def test_new_branch_points_to_attached_head_snapshot(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot_id)

        branch_repo.create(OTHER_BRANCH)

        assert branch_repo.tip(OTHER_BRANCH) == snapshot_id

    def test_new_branch_points_to_detached_head_snapshot(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.detach(snapshot_id)

        branch_repo.create(OTHER_BRANCH)

        assert branch_repo.tip(OTHER_BRANCH) == snapshot_id
        assert branch_repo.current_branch() is None
        assert branch_repo.is_detached()


class TestTip:
    def test_returns_snapshot_id(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot_id)

        assert branch_repo.tip(DEFAULT_BRANCH_NAME) == snapshot_id

    def test_returns_none_when_empty_and_no_snapshots(
        self, branch_repo: BranchRepository
    ):
        assert branch_repo.tip(DEFAULT_BRANCH_NAME) is None

    def test_raises_for_missing_branch(self, branch_repo: BranchRepository):
        with pytest.raises(BranchNotFoundError):
            branch_repo.tip(OTHER_BRANCH)

    def test_raises_with_branch_name_in_message(self, branch_repo: BranchRepository):
        with pytest.raises(BranchNotFoundError) as exc_info:
            branch_repo.tip(OTHER_BRANCH)
        assert OTHER_BRANCH in str(exc_info.value)

    def test_raises_if_branch_empty_and_snapshots_exist(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        add_snapshot(repo_context)

        with pytest.raises(BranchIsEmptyError):
            branch_repo.tip(DEFAULT_BRANCH_NAME)


class TestAdvance:
    def test_points_branch_at_snapshot(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)

        branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot_id)

        assert branch_repo.tip(DEFAULT_BRANCH_NAME) == snapshot_id

    def test_raises_for_missing_branch(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)

        with pytest.raises(BranchNotFoundError):
            branch_repo.advance(OTHER_BRANCH, snapshot_id)

    def test_raises_for_missing_snapshot(self, branch_repo: BranchRepository):
        with pytest.raises(SnapshotNotFoundError):
            branch_repo.advance(DEFAULT_BRANCH_NAME, "missing")


class TestAttach:
    def test_points_head_at_branch(self, branch_repo: BranchRepository):
        branch_repo.create(OTHER_BRANCH)

        branch_repo.attach(OTHER_BRANCH)

        assert branch_repo.current_branch() == OTHER_BRANCH
        assert not branch_repo.is_detached()

    def test_raises_for_missing_branch(self, branch_repo: BranchRepository):
        with pytest.raises(BranchNotFoundError):
            branch_repo.attach(OTHER_BRANCH)


class TestDetach:
    def test_points_head_at_snapshot(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)

        branch_repo.detach(snapshot_id)

        assert branch_repo.read_head_raw() == snapshot_id
        assert branch_repo.current_branch() is None
        assert branch_repo.is_detached()

    def test_raises_for_missing_snapshot(self, branch_repo: BranchRepository):
        with pytest.raises(SnapshotNotFoundError):
            branch_repo.detach("missing")


class TestReadHeadRaw:
    def test_returns_branch_name_after_init(self, branch_repo: BranchRepository):
        assert branch_repo.read_head_raw() == DEFAULT_BRANCH_NAME

    def test_returns_none_when_head_is_empty(self, branch_repo: BranchRepository):
        branch_repo.head_path.write_text("")
        assert branch_repo.read_head_raw() is None

    def test_returns_none_when_head_is_whitespace(self, branch_repo: BranchRepository):
        branch_repo.head_path.write_text("  \n")
        assert branch_repo.read_head_raw() is None


class TestCurrentBranch:
    def test_returns_branch_when_attached(self, branch_repo: BranchRepository):
        assert branch_repo.current_branch() == DEFAULT_BRANCH_NAME

    def test_returns_none_when_detached(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.detach(snapshot_id)

        assert branch_repo.current_branch() is None

    def test_returns_none_when_head_is_empty(self, branch_repo: BranchRepository):
        branch_repo.head_path.write_text("")
        assert branch_repo.current_branch() is None


class TestIsDetached:
    def test_false_when_attached(self, branch_repo: BranchRepository):
        assert not branch_repo.is_detached()

    def test_true_when_detached(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.detach(snapshot_id)

        assert branch_repo.is_detached()

    def test_true_when_head_points_at_unknown_ref(self, branch_repo: BranchRepository):
        branch_repo.head_path.write_text("unknown")

        assert branch_repo.is_detached()

    def test_false_when_head_is_empty(self, branch_repo: BranchRepository):
        branch_repo.head_path.write_text("")
        assert not branch_repo.is_detached()


class TestResolveHead:
    def test_follows_attached_branch(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.advance(DEFAULT_BRANCH_NAME, snapshot_id)

        assert branch_repo.resolve_head() == snapshot_id

    def test_returns_snapshot_id_when_detached(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        snapshot_id = add_snapshot(repo_context)
        branch_repo.detach(snapshot_id)

        assert branch_repo.resolve_head() == snapshot_id

    def test_returns_none_on_fresh_repo(self, branch_repo: BranchRepository):
        assert branch_repo.resolve_head() is None

    def test_raises_if_attached_branch_is_empty_and_snapshots_exist(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        add_snapshot(repo_context)

        with pytest.raises(BranchIsEmptyError):
            branch_repo.resolve_head()

    def test_raises_if_head_is_empty_and_snapshots_exist(
        self, repo_context: RepoContext, branch_repo: BranchRepository
    ):
        add_snapshot(repo_context)
        branch_repo.head_path.write_text("")

        with pytest.raises(HeadIsEmptyError):
            branch_repo.resolve_head()
