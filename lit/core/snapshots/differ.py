import difflib

from lit.core.snapshots.comparer import compare_snapshots
from lit.core.snapshots.schemas import ProjectSnapshot


def diff_snapshots(
    from_snapshot: ProjectSnapshot,
    to_snapshot: ProjectSnapshot,
) -> str:
    """
    Generate a unified diff describing how to transform `from_snapshot`
    into `to_snapshot`.

    Change detection is delegated to `compare_snapshots`. The output is
    a concatenation of unified diffs, one per changed file, grouped in
    the order: added, removed, then modified.
    """
    changes = compare_snapshots(from_snapshot, to_snapshot)

    output = []

    for path in changes.added:
        output.append(f"Added: {path}")

        new_content = to_snapshot.files[path].content.splitlines(
            keepends=True,
        )

        diff = difflib.unified_diff(
            [],
            new_content,
            fromfile="/dev/null",
            tofile=str(path),
        )

        output.extend(diff)
        output.append("")

    for path in changes.removed:
        output.append(f"Removed: {path}")

        old_content = from_snapshot.files[path].content.splitlines(
            keepends=True,
        )

        diff = difflib.unified_diff(
            old_content,
            [],
            fromfile=str(path),
            tofile="/dev/null",
        )

        output.extend(diff)
        output.append("")

    for path in changes.modified:
        output.append(f"Modified: {path}")

        old_content = from_snapshot.files[path].content.splitlines(
            keepends=True,
        )
        new_content = to_snapshot.files[path].content.splitlines(
            keepends=True,
        )

        diff = difflib.unified_diff(
            old_content,
            new_content,
            fromfile=str(path),
            tofile=str(path),
        )

        output.extend(diff)
        output.append("")

    return "".join(output)
