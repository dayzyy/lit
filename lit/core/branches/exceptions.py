from lit.core.utils.exceptions import BaseExceptionWithDefaultMessage as BaseExc

BRANCH_EXISTS_ERROR = "Branch {branch} already exists!"
BRANCH_NOT_FOUND_ERROR = "Branch {branch} does not exist!"
REF_IS_EMPTY = "{ref} is empty, but at least 1 {valid_reference} exists!"


class BranchExistsError(BaseExc):
    message = BRANCH_EXISTS_ERROR


class BranchNotFoundError(BaseExc):
    message = BRANCH_NOT_FOUND_ERROR


class RefIsEmptyError(BaseExc):
    message = REF_IS_EMPTY.format(ref="Ref", valid_reference="valid reference")


class HeadIsEmptyError(RefIsEmptyError):
    message = REF_IS_EMPTY.format(ref="HEAD", valid_reference="branch")


class BranchIsEmptyError(RefIsEmptyError):
    message = REF_IS_EMPTY.format(ref="Branch '{branch}'", valid_reference="snapshot")
