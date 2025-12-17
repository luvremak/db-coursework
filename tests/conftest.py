import os

os.environ['DB_URI'] = 'sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true'

import pytest
import pytest_asyncio
from sqlalchemy import create_engine

from app.core.database import metadata, database


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    engine = create_engine('sqlite:///file:testdb?mode=memory&cache=shared&uri=true')
    metadata.create_all(engine)
    engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    await database.connect()
    yield
    await database.disconnect()


@pytest_asyncio.fixture(autouse=True)
async def db():
    yield database

    for table in reversed(metadata.sorted_tables):
        await database.execute(table.delete())
