from lit.core.constants import DEFAULT_BRANCH_NAME
from lit.core.snapshots.reader import BaseSnapshotReader, JSONSnapshotReader
from lit.core.snapshots.writer import BaseSnapshotWriter, JSONSnapshotWriter

SNAPSHOT_READER_CLS: type[BaseSnapshotReader] = JSONSnapshotReader
SNAPSHOT_WRITER_CLS: type[BaseSnapshotWriter] = JSONSnapshotWriter

DEFAULT_BRANCH_NAME = DEFAULT_BRANCH_NAME
