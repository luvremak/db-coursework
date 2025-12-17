from aiogram.filters.callback_data import CallbackData


class CompanyCallback(CallbackData, prefix="company"):
    action: str
    company_id: int = 0
    page: int = 1


class ProjectCallback(CallbackData, prefix="project"):
    action: str
    project_id: int = 0
    company_id: int = 0
    page: int = 1
