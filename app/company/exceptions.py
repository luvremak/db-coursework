from app.core.exceptions import ApplicationError, UniqueViolationError


class CompanyException(ApplicationError):
    pass

class CompanyNotFoundError(CompanyException):
    pass

class CompanyAlreadyExistsError(UniqueViolationError, CompanyException):
    pass
