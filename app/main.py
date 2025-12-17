import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.database import database, metadata
from app.core.settings import settings
from app.tg_bot.tg_bot import dp, bot


async def main():
    engine = create_async_engine(str(settings.DB_URI))

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await database.connect()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
