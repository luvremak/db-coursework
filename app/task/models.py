from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.core.models import Entity


class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELED = "canceled"


@dataclass(kw_only=True)
class Task(Entity):
    project_id: int
    name: str
    code: int
    description: str
    deadline: datetime
    created_at: datetime
    assignee_user_id: int
    status: TaskStatus = TaskStatus.NEW
