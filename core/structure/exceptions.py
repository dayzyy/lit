from core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

REPO_DOES_NOT_EXIST_ERROR = "Repository for this project has not yet been initialized!"
REPO_EXISTS_ERROR = "Repository for this project has already been initialized!"


class RepoExistsError(BaseExc):
    message = REPO_EXISTS_ERROR


class RepoNotFoundError(BaseExc):
    message = REPO_DOES_NOT_EXIST_ERROR
