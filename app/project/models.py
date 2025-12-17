from dataclasses import dataclass
from datetime import datetime

from app.core.models import Entity


@dataclass(kw_only=True)
class Project(Entity):
    company_id: int
    name: str
    code: str
    created_at: datetime
