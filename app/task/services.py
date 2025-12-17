from app.task.dal import TaskRepo, task_repo


class TaskService:
    def __init__(self, task_repo: TaskRepo):
        self.task_repo = task_repo


task_service = TaskService(task_repo)
