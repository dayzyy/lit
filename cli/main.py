from pathlib import Path

from cli.commands import LitCommand
from cli.parser import create_parser


def main():
    cwd = Path.cwd()
    parser = create_parser()
    args = parser.parse_args()
    command: LitCommand = args.command_cls(cwd)

    command.run()


if __name__ == "__main__":
    main()
