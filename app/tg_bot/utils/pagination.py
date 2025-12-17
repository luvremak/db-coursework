from app.core.types import PaginationParameters


def get_pagination_params(page: int, page_size: int = 5) -> PaginationParameters:
    return PaginationParameters(
        page=page,
        page_size=page_size,
        order_by="id",
        ascending=False
    )


def calculate_total_pages(total_items: int, page_size: int = 5) -> int:
    if total_items == 0:
        return 1
    return (total_items + page_size - 1) // page_size
