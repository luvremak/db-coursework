from aiogram import Dispatcher, Bot, Router
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.settings import settings
from app.tg_bot.handlers import register_handlers

bot = Bot(settings.TG_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

aiogram_router = Router()
register_handlers(aiogram_router)
dp.include_router(aiogram_router)
