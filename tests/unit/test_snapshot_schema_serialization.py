import copy
from typing import Any

import pytest

from core.snapshots.exceptions import InvalidSnapshotSchemaError
from core.snapshots.schemas import ProjectSnapshot
from tests.unit.utils import make_valid_project_snapshot_dict

# ---------- Project-level mutations ----------


def missing_id(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot.pop("id", None)
    return project_snapshot


def invalid_id_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["id"] = 123
    return project_snapshot


def missing_files(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot.pop("files", None)
    return project_snapshot


def invalid_files_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"] = []
    return project_snapshot


def missing_created_at(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot.pop("created_at", None)
    return project_snapshot


def invalid_created_at_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["created_at"] = 123
    return project_snapshot


def invalid_created_at_format(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["created_at"] = "not-a-date"
    return project_snapshot


# ---------- File-level mutations ----------


def invalid_file_key_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    files = project_snapshot["files"]
    value = files.pop("./path/to/file_1")
    files[123] = value  # non-string key
    return project_snapshot


def invalid_file_value_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"] = "not-a-dict"
    return project_snapshot


# ---------- FileSnapshot-level mutations ----------


def missing_history(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"].pop("history", None)
    return project_snapshot


def invalid_history_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"]["history"] = "not-a-list"
    return project_snapshot


def missing_last_modified(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"].pop("last_modified", None)
    return project_snapshot


def invalid_last_modified_type(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"]["last_modified"] = 123
    return project_snapshot


def invalid_last_modified_format(project_snapshot: dict[str, Any]) -> dict[str, Any]:
    project_snapshot = copy.deepcopy(project_snapshot)
    project_snapshot["files"]["./path/to/file_1"]["last_modified"] = "not-a-date"
    return project_snapshot


@pytest.mark.parametrize(
    "mutate",
    [
        missing_id,
        invalid_id_type,
        missing_files,
        invalid_files_type,
        missing_created_at,
        invalid_created_at_type,
        invalid_created_at_format,
        invalid_file_key_type,
        invalid_file_value_type,
        missing_history,
        invalid_history_type,
        missing_last_modified,
        invalid_last_modified_type,
        invalid_last_modified_format,
    ],
)
def test_snapshot_schemas_init_raise_for_invalid_data(mutate):
    snapshot = mutate(make_valid_project_snapshot_dict())

    with pytest.raises(InvalidSnapshotSchemaError):
        ProjectSnapshot.from_dict(snapshot)
