from pathlib import Path

import pytest

from core.snapshots.schemas import FileSnapshot, ProjectSnapshot

# ---------- File-level equality ----------


def test_file_snapshot_equality_same_content():
    f1 = FileSnapshot(content="hello")
    f2 = FileSnapshot(content="hello")

    assert f1 == f2


def test_file_snapshot_inequality_different_content():
    f1 = FileSnapshot(content="hello")
    f2 = FileSnapshot(content="world")

    assert f1 != f2


# ---------- Project-level equality ----------


@pytest.mark.parametrize(
    "snap1, snap2, expected",
    [
        (
            ProjectSnapshot(
                id="1",
                files={
                    Path("a.txt"): FileSnapshot(content="a"),
                    Path("b.txt"): FileSnapshot(content="b"),
                },
            ),
            ProjectSnapshot(
                id="2",
                files={
                    Path("a.txt"): FileSnapshot(content="a"),
                    Path("b.txt"): FileSnapshot(content="b"),
                },
            ),
            True,
        ),
        (
            ProjectSnapshot(
                id="1",
                files={Path("a.txt"): FileSnapshot(content="a")},
            ),
            ProjectSnapshot(
                id="2",
                files={Path("a.txt"): FileSnapshot(content="different")},
            ),
            False,
        ),
    ],
)
def test_project_snapshot_equality(snap1, snap2, expected):
    assert (snap1 == snap2) is expected


def test_project_snapshot_inequality_missing_file():
    snap1 = ProjectSnapshot(
        id="1",
        files={
            Path("a.txt"): FileSnapshot(content="a"),
            Path("b.txt"): FileSnapshot(content="b"),
        },
    )

    snap2 = ProjectSnapshot(
        id="1",
        files={
            Path("a.txt"): FileSnapshot(content="a"),
        },
    )

    assert snap1 != snap2


def test_project_snapshot_inequality_extra_file():
    snap1 = ProjectSnapshot(
        id="1",
        files={Path("a.txt"): FileSnapshot(content="a")},
    )

    snap2 = ProjectSnapshot(
        id="1",
        files={
            Path("a.txt"): FileSnapshot(content="a"),
            Path("b.txt"): FileSnapshot(content="b"),
        },
    )

    assert snap1 != snap2
