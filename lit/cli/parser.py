from argparse import ArgumentParser, _SubParsersAction

from lit.cli.commands import (
    InitCommand,
    LitCommand,
    SnapshotCreateCommand,
    SnapshotListCommand,
)


def register_command(
    subparsers: _SubParsersAction,
    name: str,
    command_cls: type[LitCommand],
) -> None:
    """
    Register a CLI command and associate it with its command class.

    The provided command class is attached to the parser using
    `set_defaults()`, allowing the dispatching logic to instantiate
    and execute the appropriate command after argument parsing.

    This helper centralizes command registration and keeps parser
    configuration concise as new commands are added.
    """
    command_parser = subparsers.add_parser(name)
    command_cls.configure_parser(command_parser)
    command_parser.set_defaults(command_cls=command_cls)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="lit")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    register_command(subparsers, "init", InitCommand)
    register_command(subparsers, "snapshot", SnapshotCreateCommand)
    register_command(subparsers, "log", SnapshotListCommand)

    return parser
