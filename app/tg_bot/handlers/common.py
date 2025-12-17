from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Welcome to AnyaDB Bot!</b>\n\n"
        "<b>Company Commands:</b>\n"
        "/new_company - Create a new company\n"
        "/my_companies - View your companies\n\n"
        "<b>Project Commands:</b>\n"
        "/new_project - Create a new project\n"
        "/projects - View projects\n\n"
        "/help - Show this help message",
        parse_mode="HTML"
    )


async def cmd_help(message: Message):
    await message.answer(
        "<b>Available Commands:</b>\n\n"
        "<b>Company Management:</b>\n"
        "/new_company - Create a new company\n"
        "/my_companies - View your companies\n\n"
        "<b>Project Management:</b>\n"
        "/new_project - Create a new project\n"
        "/projects - View projects\n\n"
        "/start - Show welcome message",
        parse_mode="HTML"
    )


def register_common_handlers(router: Router):
    router.message.register(cmd_start, Command("start"))
    router.message.register(cmd_help, Command("help"))
