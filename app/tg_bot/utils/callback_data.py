from aiogram.filters.callback_data import CallbackData


class CompanyCallback(CallbackData, prefix="company"):
    action: str
    company_id: int = 0
    page: int = 1
