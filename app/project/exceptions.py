from app.core.exceptions import ApplicationError, UniqueViolationError


class ProjectException(ApplicationError):
    pass

class ProjectNotFoundError(ProjectException):
    pass

class ProjectAlreadyExistsError(UniqueViolationError, ProjectException):
    pass
