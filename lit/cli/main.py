import sys
from pathlib import Path

from lit.cli.commands import LitCommand
from lit.cli.parser import create_parser
from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage


def main():
    try:
        cwd = Path.cwd()
        parser = create_parser()
        args = parser.parse_args()
        command: LitCommand = args.command_cls.from_args(args=args, cwd=cwd)

        command.run()
        return 0

    except BaseExceptionWithDefaultMessage as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
