from dataclasses import dataclass
from datetime import datetime

from app.core.models import Entity


@dataclass(kw_only=True)
class Task(Entity):
    project_id: int
    name: str
    code: str
    description: str
    deadline: datetime
    created_at: datetime
    assignee_user_id: int
