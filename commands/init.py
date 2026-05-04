from pathlib import Path

from core.structure.exceptions import RepoExistsError
from core.structure.structure import RepoStructure


def create_repo(cwd: Path | None = None) -> Path:
    cwd = cwd or Path.cwd()

    if RepoStructure.repo_exists(cwd):
        raise RepoExistsError

    lit_path = cwd / RepoStructure.Directories.BASE.value
    lit_path.mkdir()

    for dir in RepoStructure.Directories:
        if dir is not RepoStructure.Directories.BASE:
            path = dir.get_path(lit_path)
            path.mkdir(parents=True)

    return lit_path


if __name__ == "__main__":
    create_repo()
