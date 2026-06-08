from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

INVALID_SNAPSHOT_SCHEMA_ERROR = "Invalid snapshot schema!"
SNAPSHOT_FILE_NOT_FOUND_ERROR = "Snapshot file not found!"
SNAPSHOT_FILE_ALREADY_EXISTS = "Snapshot file arleady exists!"


class InvalidSnapshotSchemaError(BaseExc):
    message = INVALID_SNAPSHOT_SCHEMA_ERROR


class SnapshotFileNotFoundError(BaseExc):
    message = SNAPSHOT_FILE_NOT_FOUND_ERROR


class SnapshotFileAlreadyExistsError(BaseExc):
    message = SNAPSHOT_FILE_ALREADY_EXISTS
