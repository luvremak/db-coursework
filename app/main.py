import asyncio
import logging

from app.core.database import database
from app.tg_bot.tg_bot import dp, bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


async def main():
    await database.connect()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
