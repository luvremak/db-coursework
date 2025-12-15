class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class UniqueViolationError(ApplicationError):
    def __init__(self, constraint_name: str):
        super().__init__()
        self.constraint_name = constraint_name
