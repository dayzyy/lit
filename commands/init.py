from pathlib import Path

from core.structure.exceptions import RepoExistsError
from core.structure.structure import RepoStructure


def create_repo(cwd: Path | None = None):
    cwd = cwd or Path.cwd()

    if (RepoStructure.repo_exists(cwd)):
        raise RepoExistsError

    root_path = cwd / RepoStructure.Directories.BASE.value

    for dir in RepoStructure.Directories:
        dir.get_path(root_path).mkdir(parents=True)


if __name__ == "__main__":
    create_repo()
