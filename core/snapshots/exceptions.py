from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

INVALID_SNAPSHOT_SCHEMA_ERROR = "Invalid snapshot schema!"


class InvalidSnapshotSchemaError(BaseExc):
    message = INVALID_SNAPSHOT_SCHEMA_ERROR
