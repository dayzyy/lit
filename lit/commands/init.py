from pathlib import Path

from lit.config import SNAPSHOT_READER_CLS, SNAPSHOT_WRITER_CLS
from lit.core.snapshots.reader import BaseSnapshotReader
from lit.core.snapshots.repo import SnapshotRepository
from lit.core.snapshots.writer import BaseSnapshotWriter
from lit.core.structure.exceptions import RepoExistsError
from lit.core.structure.structure import RepoStructure


def create_repo(
    cwd: Path | None = None,
    reader_cls: type[BaseSnapshotReader] | None = None,
    writer_cls: type[BaseSnapshotWriter] | None = None,
) -> Path:
    writer_cls = writer_cls or SNAPSHOT_WRITER_CLS
    reader_cls = reader_cls or SNAPSHOT_READER_CLS

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
    writer_cls._initialize_file(snapshot_file_path)

    return lit_path


if __name__ == "__main__":
    create_repo()
