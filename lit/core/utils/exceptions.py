class BaseExceptionWithDefaultMessage(Exception):  # noqa: N818
    """
    Base exception class that uses a class-level `message` as the default
    error message if no positional arguments are provided.
    """

    message: str = "Something went wrong!"

    def __init__(self, *args) -> None:
        if args:
            super().__init__(*args)
        else:
            super().__init__(self.message)
