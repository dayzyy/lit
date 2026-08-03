class BaseExceptionWithDefaultMessage(Exception):  # noqa: N818
    """
    Base exception class that uses a class-level `message` as the default
    error message when no arguments are provided.

    Positional arguments are used as the message directly, allowing for
    one-off messages. Keyword arguments are formatted into `message` using
    `str.format`, e.g. a `message` of `"missing '{key}'"` raised as
    `SomeError(key="id")`.
    """

    message: str = "Something went wrong!"

    def __init__(self, *args, **kwargs) -> None:
        if args:
            super().__init__(*args)
        elif kwargs:
            super().__init__(self.message.format(**kwargs))
        else:
            super().__init__(self.message)


class TypeErrorWithDefaultMessage(  # noqa: N818
    BaseExceptionWithDefaultMessage, TypeError
):
    """
    Like `BaseExceptionWithDefaultMessage`, but also a `TypeError`.
    """
