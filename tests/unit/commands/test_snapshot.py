import pytest

from tests.commands.runners import UnitCommands
from tests.commands.snapshot import CASES
from tests.conftest import RepoContext


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.__name__.removeprefix("case_"))
def test_snapshot(case, repo_context: RepoContext):
    case(repo_context, UnitCommands(repo_context.root))
