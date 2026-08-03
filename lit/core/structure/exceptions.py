from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc
from lit.core.utils.exceptions import TypeErrorWithDefaultMessage as TypeErrorBase

REPO_DOES_NOT_EXIST_ERROR = "Repository for this project has not yet been initialized!"
REPO_EXISTS_ERROR = "Repository for this project has already been initialized!"
STATIC_NAMESPACE_ERROR = "Static namespace {class_name} can not be instantiated!"


class RepoExistsError(BaseExc):
    message = REPO_EXISTS_ERROR


class RepoNotFoundError(BaseExc):
    message = REPO_DOES_NOT_EXIST_ERROR


class StaticNamespaceInstantiationError(TypeErrorBase):
    message = STATIC_NAMESPACE_ERROR
