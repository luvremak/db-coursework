from aiogram import Router
from . import common, company, project, employee, task


def register_handlers(router: Router):
    common.register_common_handlers(router)
    company.register_company_handlers(router)
    project.register_project_handlers(router)
    employee.register_employee_handlers(router)
    task.register_task_handlers(router)
