import pytest

from tests.commands.diff import CASES
from tests.commands.runners import UnitCommands
from tests.conftest import RepoContext


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.__name__.removeprefix("case_"))
def test_diff(case, repo_context: RepoContext):
    case(repo_context, UnitCommands(repo_context.root))
