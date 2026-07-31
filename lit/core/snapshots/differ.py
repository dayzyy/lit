import difflib

from lit.core.snapshots.comparer import compare_snapshots
from lit.core.snapshots.schemas import ProjectSnapshot


def diff_snapshots(
    snapshot_1: ProjectSnapshot,
    snapshot_2: ProjectSnapshot,
) -> str:
    changes = compare_snapshots(snapshot_1, snapshot_2)

    output = []

    for path in changes.added:
        output.append(f"Added: {path}")

        new_content = snapshot_2.files[path].content.splitlines(
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

        old_content = snapshot_1.files[path].content.splitlines(
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

        old_content = snapshot_1.files[path].content.splitlines(
            keepends=True,
        )
        new_content = snapshot_2.files[path].content.splitlines(
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
