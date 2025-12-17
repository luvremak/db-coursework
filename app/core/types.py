from dataclasses import dataclass
from typing import Any, Mapping

DTO = Mapping[str, Any]


@dataclass
class PageData[T]:
    data: list[T]
    total: int


@dataclass
class PaginationParameters:
    page: int = 1
    page_size: int = 10
    order_by: str = "id"
    ascending: bool = True

    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 10
