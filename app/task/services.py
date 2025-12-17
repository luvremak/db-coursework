from app.task.dal import TaskRepo


class TaskService:
    def __init__(self, task_repo: TaskRepo):
        self.task_repo = task_repo
