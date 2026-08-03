# Lit — a Git-inspired version control system

Lit is a small, Git-inspired version control system. Instead of tracking
changes between commits, it stores the entire working tree as a **snapshot**
and lets you restore, compare, and diff snapshots.

## Project structure

### Repository layout — `lit/core/structure/structure.py`

`RepoStructure` defines how a Lit repository looks on disk. A repository is
the `.lit` directory (created by `lit init`) containing one directory per
storage concern:

```
.lit/
└── snapshots/
    └── snapshots        # snapshot storage file
```

It also provides helpers to locate a repository from any path
(`find_repo_root`, `find_valid_repo_root`) and to validate one
(`is_valid_lit_repo`).

### Core data objects — `lit/core/snapshots/schemas.py`

Defines the objects that make up a repository, the equivalent of Git's
blobs, commits, and trees:

- `FileSnapshot` — the content of a single file. The equivalent of a
  Git **blob**.
- `ProjectSnapshot` — the entire working tree at a point in time: every
  file keyed by its path relative to the repository root, plus a message
  and metadata. Combines Git's **tree** and **commit**.
- `SnapshotDiff` — the set of added, removed, and modified paths between
  two snapshots.

All objects serialize to and from dictionaries (`to_dict` / `from_dict`),
which is how they are stored in and restored from the storage file.

### Reading, writing, and accessing snapshots

- `lit/core/snapshots/builder.py` — walks the working directory and
  captures it into a `ProjectSnapshot` (`build_snapshot`).
- `lit/core/snapshots/reader.py` — loads snapshots from the storage file.
  `BaseSnapshotReader` is the interface; `JSONSnapshotReader` is the
  default implementation. Reading is delegated to `_parse_raw_snapshots`,
  so other backends (e.g. SQLite) can be plugged in.
- `lit/core/snapshots/writer.py` — persists snapshots. `BaseSnapshotWriter`
  is the interface; `JSONSnapshotWriter` appends snapshots to a JSON file
  and initializes new storage files.
- `lit/core/snapshots/repo.py` — `SnapshotRepository` is the high-level
  facade combining a reader and a writer, exposing `add`, `all`, `latest`,
  and `get`.
- `lit/core/snapshots/comparer.py` — detects added, removed, and modified
  paths between two snapshots (`compare_snapshots`).
- `lit/core/snapshots/differ.py` — renders the changes between two
  snapshots as a unified diff (`diff_snapshots`).

## Usage

### Initialize a repository

```sh
lit init
```

Creates the `.lit` repository structure in the current directory.

### Create a snapshot

```sh
lit snapshot -m "initial commit"
```

Captures the current working tree as a snapshot and prints its ID. Errors
with "No new changes to commit!" if the tree is unchanged since the latest
snapshot.

### List snapshots

```sh
lit log
```

Prints a table of all snapshots (ID, creation date, message).

### Restore a snapshot

```sh
lit checkout <snapshot_id>
```

Restores the working tree to the state of the given snapshot.

### Show status

```sh
lit status
```

Lists added, removed, and modified files relative to the latest snapshot,
or prints "Working tree clean." if there are no changes.

### Show a diff

```sh
lit diff                 # working tree vs. latest snapshot
lit diff <snapshot_id>   # working tree vs. that snapshot
lit diff <id> <id>       # between two snapshots
```

Renders the changes as a unified diff.
