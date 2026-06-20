from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

INVALID_SNAPSHOT_SCHEMA = "Invalid snapshot schema!"
SNAPSHOT_FILE_NOT_FOUND = "Snapshot file not found!"
SNAPSHOT_FILE_ALREADY_EXISTS = "Snapshot file arleady exists!"
SNAPSHOT_NOT_FOUND = "Snapshot not found!"


class InvalidSnapshotSchemaError(BaseExc):
    message = INVALID_SNAPSHOT_SCHEMA


class SnapshotFileNotFoundError(BaseExc):
    message = SNAPSHOT_FILE_NOT_FOUND


class SnapshotFileAlreadyExistsError(BaseExc):
    message = SNAPSHOT_FILE_ALREADY_EXISTS


class SnapshotNotFoundError(BaseExc):
    message = SNAPSHOT_FILE_NOT_FOUND
