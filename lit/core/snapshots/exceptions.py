from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc
from lit.core.utils.exceptions import TypeErrorWithDefaultMessage as TypeErrorBase

INVALID_SNAPSHOT_SCHEMA = "Invalid snapshot schema!"
SNAPSHOT_FILE_NOT_FOUND = "Snapshot file not found!"
SNAPSHOT_FILE_ALREADY_EXISTS = "Snapshot file already exists!"
SNAPSHOT_NOT_FOUND = "Snapshot {id} not found!"
NOTHING_TO_COMMIT = "No new changes to commit!"

INVALID_ISO_DATETIME = "'{value}' is not an ISO formatted string!"
FILE_SNAPSHOT_MISSING_KEY = "FileSnapshot missing key: {key}!"
PROJECT_SNAPSHOT_MISSING_KEY = "ProjectSnapshot missing key: {key}!"
INVALID_SNAPSHOT_ID_TYPE = "'id' must be a string!"
INVALID_FILES_TYPE = "'files' must be a dictionary!"
INVALID_FILE_PATH_TYPE = "file path must be a string!"
INVALID_FILE_SNAPSHOT_TYPE = "file snapshot must be a dictionary!"
INVALID_PARSE_RESULT = "{reader_class}._parse_raw_snapshots must return a list!"
INVALID_SNAPSHOT_TYPE = "'snapshot' must be 'ProjectSnapshot', got {snapshot_type}!"
FILE_SNAPSHOT_TYPE = "'other' must be 'FileSnapshot', got {other_type}!"
PROJECT_SNAPSHOT_TYPE = "'other' must be 'ProjectSnapshot', got {other_type}!"


class InvalidSnapshotSchemaError(BaseExc):
    message = INVALID_SNAPSHOT_SCHEMA


class InvalidISODatetimeError(InvalidSnapshotSchemaError):
    message = INVALID_ISO_DATETIME


class FileSnapshotMissingKeyError(InvalidSnapshotSchemaError):
    message = FILE_SNAPSHOT_MISSING_KEY


class ProjectSnapshotMissingKeyError(InvalidSnapshotSchemaError):
    message = PROJECT_SNAPSHOT_MISSING_KEY


class InvalidSnapshotIDTypeError(InvalidSnapshotSchemaError):
    message = INVALID_SNAPSHOT_ID_TYPE


class InvalidFilesTypeError(InvalidSnapshotSchemaError):
    message = INVALID_FILES_TYPE


class InvalidFilePathTypeError(InvalidSnapshotSchemaError):
    message = INVALID_FILE_PATH_TYPE


class InvalidFileSnapshotTypeError(InvalidSnapshotSchemaError):
    message = INVALID_FILE_SNAPSHOT_TYPE


class InvalidParseResultError(InvalidSnapshotSchemaError):
    message = INVALID_PARSE_RESULT


class InvalidSnapshotTypeError(TypeErrorBase):
    message = INVALID_SNAPSHOT_TYPE


class FileSnapshotTypeError(TypeErrorBase):
    message = FILE_SNAPSHOT_TYPE


class ProjectSnapshotTypeError(TypeErrorBase):
    message = PROJECT_SNAPSHOT_TYPE


class SnapshotFileNotFoundError(BaseExc):
    message = SNAPSHOT_FILE_NOT_FOUND


class SnapshotFileAlreadyExistsError(BaseExc):
    message = SNAPSHOT_FILE_ALREADY_EXISTS


class SnapshotNotFoundError(BaseExc):
    message = SNAPSHOT_NOT_FOUND


class NothingToCommitError(BaseExc):
    message = NOTHING_TO_COMMIT
