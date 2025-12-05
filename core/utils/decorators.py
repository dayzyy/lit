from typing import Any, Callable


class classproperty: # noqa: N801
    def __init__(self, func: Callable[[Any], Any]):
        self.function = func

    def __get__(self, _, owner: Any):
        return self.function(owner)
