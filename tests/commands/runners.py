from pathlib import Path
from typing import Any, Protocol

from lit.cli.commands import (
    DiffCommand,
    SnapshotCheckoutCommand,
    SnapshotCreateCommand,
    StatusCommand,
)
from lit.cli.parser import create_parser
from lit.core.snapshots.schemas import ProjectSnapshot


class CommandRunner(Protocol):
    """Common interface shared by the unit and CLI execution layers."""

    def status(self) -> str: ...

    def diff(self, *snapshot_ids: str) -> str: ...

    def checkout(self, snapshot_id: str) -> None: ...

    def snapshot(self, message: str) -> ProjectSnapshot: ...


class UnitCommands:
    """Execute commands through their constructors and public API."""

    def __init__(self, cwd: Path):
        self.cwd = cwd

    def status(self) -> str:
        return StatusCommand(cwd=self.cwd).execute()

    def diff(self, *snapshot_ids: str) -> str:
        return DiffCommand(snapshot_ids=list(snapshot_ids), cwd=self.cwd).execute()

    def checkout(self, snapshot_id: str) -> None:
        SnapshotCheckoutCommand(snapshot_id, cwd=self.cwd).run()

    def snapshot(self, message: str) -> ProjectSnapshot:
        return SnapshotCreateCommand(message=message, cwd=self.cwd).run()


class CliCommands:
    """Execute commands by parsing CLI args, then running them."""

    def __init__(self, cwd: Path, capsys):
        self.cwd = cwd
        self.capsys = capsys

    def _run(self, argv: list[str]) -> tuple[str, Any]:
        parser = create_parser()
        args = parser.parse_args(argv)

        command = args.command_cls.from_args(args=args, cwd=self.cwd)
        result = command.run()

        return self.capsys.readouterr().out.strip(), result

    def status(self) -> str:
        output, _ = self._run(["status"])
        return output

    def diff(self, *snapshot_ids: str) -> str:
        output, _ = self._run(["diff", *snapshot_ids])
        return output

    def checkout(self, snapshot_id: str) -> None:
        self._run(["checkout", snapshot_id])

    def snapshot(self, message: str) -> ProjectSnapshot:
        _, result = self._run(["snapshot", "-m", message])
        return result
