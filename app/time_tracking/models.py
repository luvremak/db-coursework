from dataclasses import dataclass
from datetime import datetime

from app.core.models import Entity


@dataclass(kw_only=True)
class TimeTrackingEntry(Entity):
    task_id: int
    employee_id: int
    duration_minutes: int
    created_at: datetime
