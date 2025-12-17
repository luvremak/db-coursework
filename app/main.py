import asyncio

from app.core.database import database
from app.tg_bot.tg_bot import dp, bot


async def main():
    await database.connect()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
