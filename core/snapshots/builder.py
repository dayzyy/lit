from pathlib import Path

from core.snapshots.schemas import FileSnapshot, ProjectSnapshot
from core.structure.structure import RepoStructure


def is_ignored(path: Path) -> bool:
    """
    Determines whether a given file system path should be excluded
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
    Constructs a ProjectSnapshot representing the current state of
    the working directory.
    """
    files = {}
    for path in root.rglob("*"):
        if path.is_file() and not is_ignored(path):
            relative_path = path.relative_to(root)
            content = path.read_text()

            files[relative_path] = FileSnapshot(content=content)

    return ProjectSnapshot(files=files, message=message)
