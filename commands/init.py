from pathlib import Path

from config import SNAPSHOT_WRITER_CLS
from core.snapshots.repo import SnapshotRepository
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

    snapshot_file_path = SnapshotRepository._get_file_path(lit_path)
    SNAPSHOT_WRITER_CLS._initialize_file(snapshot_file_path)

    return lit_path


if __name__ == "__main__":
    create_repo()
