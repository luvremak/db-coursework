from dataclasses import dataclass


@dataclass(kw_only=True)
class Entity:
    id: int = None
