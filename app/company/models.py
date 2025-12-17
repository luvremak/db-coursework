from dataclasses import dataclass

from app.core.models import Entity


@dataclass(kw_only=True)
class Company(Entity):
    name: str
    code: str
    owner_tg_id: int
