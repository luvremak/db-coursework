from aiogram.types import Message, CallbackQuery
from app.core.exceptions import ApplicationError
from app.company.exceptions import (
    CompanyNotFoundError,
    CompanyAccessDeniedError,
    InvalidCompanyCodeError,
    CompanyAlreadyExistsError,
)
from app.project.exceptions import (
    ProjectNotFoundError,
    ProjectAccessDeniedError,
    InvalidProjectCodeError,
    ProjectAlreadyExistsError,
)
from app.employee.exceptions import (
    EmployeeNotFoundError,
    EmployeeAccessDeniedError,
    EmployeeAlreadyExistsError,
)
from app.task.exceptions import (
    TaskNotFoundError,
    TaskAccessDeniedError,
    TaskAlreadyExistsError,
)
from app.time_tracking.exceptions import (
    TimeTrackingEntryNotFoundError,
    TimeTrackingEntryAlreadyExistsError,
)


ERROR_MESSAGES = {
    CompanyNotFoundError: "Company not found",
    CompanyAccessDeniedError: "You don't have permission to perform this action",
    InvalidCompanyCodeError: "Invalid company code. Must be exactly 3 letters",
    CompanyAlreadyExistsError: "A company with this code already exists",
    ProjectNotFoundError: "Project not found",
    ProjectAccessDeniedError: "You don't have permission to perform this action",
    InvalidProjectCodeError: "Invalid project code. Must be exactly 3 letters",
    ProjectAlreadyExistsError: "A project with this code already exists",
    EmployeeNotFoundError: "Employee not found",
    EmployeeAccessDeniedError: "You don't have permission to perform this action",
    EmployeeAlreadyExistsError: "Employee already exists in this company",
    TaskNotFoundError: "Task not found",
    TaskAccessDeniedError: "You don't have permission to perform this action",
    TaskAlreadyExistsError: "Task already exists",
    TimeTrackingEntryNotFoundError: "Time tracking entry not found",
    TimeTrackingEntryAlreadyExistsError: "Time tracking entry already exists",
}


async def handle_service_error(error: Exception, message: Message | CallbackQuery):
    error_msg = ERROR_MESSAGES.get(type(error), f"An error occurred: {str(error)}")

    if isinstance(message, Message):
        await message.answer(f"❌ {error_msg}")
    else:  # CallbackQuery
        await message.answer(error_msg, show_alert=True)


def format_error_message(error: Exception) -> str:
    return ERROR_MESSAGES.get(type(error), f"An error occurred: {str(error)}")
