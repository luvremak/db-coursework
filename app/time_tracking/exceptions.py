from app.core.exceptions import ApplicationError, UniqueViolationError


class TimeTrackingEntryException(ApplicationError):
    pass

class TimeTrackingEntryNotFoundError(TimeTrackingEntryException):
    pass

class TimeTrackingEntryAlreadyExistsError(UniqueViolationError, TimeTrackingEntryException):
    pass
