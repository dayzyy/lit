from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

REPO_DOES_NOT_EXIST = "Repository for this project has not yet been initialized!"
REPO_EXISTS = "Repository for this project has already been initialized!"

REPO_DOES_NOT_EXIST_ERROR = RuntimeError(REPO_DOES_NOT_EXIST)
REPO_EXISTS_ERROR = RuntimeError(REPO_EXISTS)


class RepoExistsError(BaseExc):
    message = REPO_EXISTS


class RepoNotFoundError(BaseExc):
    message = REPO_DOES_NOT_EXIST
