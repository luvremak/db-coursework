from app.core.exceptions import ApplicationError, UniqueViolationError


class TaskException(ApplicationError):
    pass

class TaskNotFoundError(TaskException):
    pass

class TaskAlreadyExistsError(UniqueViolationError, TaskException):
    pass
