from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

BRANCH_EXISTS_ERROR = "Branch {branch} already exists!"
BRANCH_NOT_FOUND_ERROR = "Branch {branch} does not exist!"


class BranchExistsError(BaseExc):
    message = BRANCH_EXISTS_ERROR


class BranchNotFoundError(BaseExc):
    message = BRANCH_NOT_FOUND_ERROR
