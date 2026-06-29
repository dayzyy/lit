from pathlib import Path

from lit.cli.commands import LitCommand
from lit.cli.parser import create_parser


def main():
    cwd = Path.cwd()
    parser = create_parser()
    args = parser.parse_args()
    command: LitCommand = args.command_cls.from_args(args=args, cwd=cwd)

    command.run()


if __name__ == "__main__":
    main()
