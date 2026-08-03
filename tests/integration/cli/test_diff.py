import pytest

from tests.commands.diff import CASES
from tests.commands.runners import CliCommands
from tests.conftest import RepoContext


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.__name__.removeprefix("case_"))
def test_cli_diff(case, repo_context: RepoContext, capsys):
    case(repo_context, CliCommands(repo_context.root, capsys))
