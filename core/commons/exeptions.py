from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

FORBIDDEN_OVERRIDE = (
    "Forbidden override!: \n{namespace}.{attr_name} must not be overriden!"
)


class ForbiddenOverrideError(BaseExc):
    def __init__(
        self, namespace: str | None = None, attr_name: str | None = None, *args
    ) -> None:
        if namespace is not None and attr_name is not None:
            self.message = FORBIDDEN_OVERRIDE.format(
                namespace=namespace, attr_name=attr_name
            )
            super().__init__(self.message)
        super().__init__(*args)
