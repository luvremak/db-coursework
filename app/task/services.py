from app.task.dal import TaskCrud, TaskRepo
from app.task.models import Task
from app.core.serializer import DataclassSerializer


class TaskService:
    def __init__(self, task_repo: TaskRepo):
        self.task_repo = task_repo


task_service = TaskService(TaskRepo(TaskCrud(), DataclassSerializer(Task)))
