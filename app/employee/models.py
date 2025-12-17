from dataclasses import dataclass
from datetime import datetime

from app.core.models import Entity


@dataclass(kw_only=True)
class Employee(Entity):
    telegram_id: int
    company_id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    salary_per_hour: float
    display_name: str
