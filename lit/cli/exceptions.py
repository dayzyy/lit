from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

DIFF_MORE_THAN_TWO_SNAPSHOTS = "diff accepts at most two snapshot IDs!"


class InvalidCLIUsageError(BaseExc):
    message = "Invalid way to use the CLI!"


class TooManySnapshotIDsError(InvalidCLIUsageError):
    message = DIFF_MORE_THAN_TWO_SNAPSHOTS
