from typing import Any, Callable


class classproperty:
    def __init__(self, func: Callable[[Any], Any]):
        self.function = func

    def __get__(self, _, owner: Any):
        return self.function(owner)
