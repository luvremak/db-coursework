from aiogram.types import Message, CallbackQuery
from app.core.exceptions import ApplicationError
from app.company.exceptions import (
    CompanyNotFoundError,
    CompanyAccessDeniedError,
    InvalidCompanyCodeError,
    CompanyAlreadyExistsError,
)


ERROR_MESSAGES = {
    CompanyNotFoundError: "Company not found",
    CompanyAccessDeniedError: "You don't have permission to perform this action",
    InvalidCompanyCodeError: "Invalid company code. Must be exactly 3 letters",
    CompanyAlreadyExistsError: "A company with this code already exists",
}


async def handle_service_error(error: Exception, message: Message | CallbackQuery):
    error_msg = ERROR_MESSAGES.get(type(error), f"An error occurred: {str(error)}")

    if isinstance(message, Message):
        await message.answer(f"❌ {error_msg}")
    else:  # CallbackQuery
        await message.answer(error_msg, show_alert=True)


def format_error_message(error: Exception) -> str:
    return ERROR_MESSAGES.get(type(error), f"An error occurred: {str(error)}")
