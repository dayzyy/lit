from pathlib import Path

from lit.core.snapshots.schemas import FileSnapshot, ProjectSnapshot
from lit.core.structure.structure import RepoStructure


def is_ignored(path: Path) -> bool:
    """
    Determine whether a given file system path should be excluded
    from snapshot creation.

    Currently, only the repository metadata directory (e.g. `.lit`)
    is ignored.

    This logic is intentionally minimal and will likely be replaced
    or extended by a more sophisticated ignore system (similar to
    `.gitignore`) as the project evolves.
    """
    return RepoStructure.Directories.BASE.value in path.parts


def build_snapshot(root: Path, message: str) -> ProjectSnapshot:
    """
    Construct a `ProjectSnapshot` of the working directory at `root`.

    Walks the directory tree under `root` and captures the content of
    every non-ignored file, keyed by its path relative to `root`. Files
    are read as text; binary files are not supported.
    """
    files = {}
    for path in root.rglob("*"):
        if path.is_file() and not is_ignored(path):
            relative_path = path.relative_to(root)
            content = path.read_text()

            files[relative_path] = FileSnapshot(content=content)

    return ProjectSnapshot(files=files, message=message)
