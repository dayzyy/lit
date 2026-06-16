from core.snapshots.reader import BaseSnapshotReader, JSONSnapshotReader
from core.snapshots.writer import BaseSnapshotWriter, JSONSnapshotWriter

SNAPSHOT_READER_CLS: type[BaseSnapshotReader] = JSONSnapshotReader
SNAPSHOT_WRITER_CLS: type[BaseSnapshotWriter] = JSONSnapshotWriter
