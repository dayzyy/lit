import pytest

from lit.core.snapshots.exceptions import SnapshotNotFoundError
from lit.core.snapshots.schemas import ProjectSnapshot
from tests.conftest import RepoContext
from tests.unit.utils import make_valid_project_snapshot_dict


def make_snapshot(id: str) -> ProjectSnapshot:
    data = make_valid_project_snapshot_dict()
    data["id"] = id
    return ProjectSnapshot.from_dict(data)


class TestGet:
    def test_returns_snapshot_with_matching_id(self, repo_context: RepoContext):
        repo_context.snapshot_repo.add(make_snapshot("1"))
        repo_context.snapshot_repo.add(make_snapshot("2"))

        result = repo_context.snapshot_repo.get("2")

        assert result is not None
        assert result.id == "2"

    def test_returns_none_when_missing(self, repo_context: RepoContext):
        repo_context.snapshot_repo.add(make_snapshot("1"))

        assert repo_context.snapshot_repo.get("missing") is None


class TestRequireSnapshot:
    def test_returns_snapshot_when_found(self, repo_context: RepoContext):
        repo_context.snapshot_repo.add(make_snapshot("1"))

        result = repo_context.snapshot_repo.require_snapshot("1")

        assert result.id == "1"

    def test_raises_when_missing(self, repo_context: RepoContext):
        with pytest.raises(SnapshotNotFoundError):
            repo_context.snapshot_repo.require_snapshot("missing")

    def test_raises_with_id_in_message(self, repo_context: RepoContext):
        with pytest.raises(SnapshotNotFoundError) as exc_info:
            repo_context.snapshot_repo.require_snapshot("missing")

        assert "missing" in str(exc_info.value)
