from lit.core.snapshots.schemas import ProjectSnapshot, SnapshotDiff


def compare_snapshots(
    snapshot_1: ProjectSnapshot, snapshot_2: ProjectSnapshot
) -> SnapshotDiff:
    """
    Compare two snapshots and return a `SnapshotDiff` of the changes
    between them.

    A path is `removed` if it exists only in `snapshot_1`, `added` if it
    exists only in `snapshot_2`, and `modified` if it exists in both but
    with different content.
    """
    files_1 = snapshot_1.files
    files_2 = snapshot_2.files

    paths_1 = set(files_1)
    paths_2 = set(files_2)
    common_paths = paths_1 & paths_2

    removed = paths_1 - paths_2
    added = paths_2 - paths_1
    modified = {path for path in common_paths if files_1[path] != files_2[path]}

    return SnapshotDiff(removed=removed, added=added, modified=modified)
