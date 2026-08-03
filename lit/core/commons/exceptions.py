from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

FORBIDDEN_OVERRIDE = (
    "Forbidden override!\n{namespace}.{attr_name} must not be overridden!"
)


class ForbiddenOverrideError(BaseExc):
    message = FORBIDDEN_OVERRIDE
