from app.core.exceptions import ApplicationError, UniqueViolationError


class EmployeeException(ApplicationError):
    pass

class EmployeeNotFoundError(EmployeeException):
    pass

class EmployeeAlreadyExistsError(UniqueViolationError, EmployeeException):
    pass
