from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.task.models import Task
from app.task.tables import task_table


class TaskCrud(CrudBase[int, DTO]):
    table = task_table


class TaskRepo(RepoBase[int, Task]):
    crud: TaskCrud

    def __init__(self, crud: TaskCrud, serializer: Serializer[Task, DTO]):
        super().__init__(crud, serializer, Task)


task_repo = TaskRepo(TaskCrud(), DataclassSerializer(Task))
