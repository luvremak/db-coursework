from unittest.mock import patch
import uuid

import pytest_asyncio
from databases import Database
from sqlalchemy import create_engine

from app.core.database import metadata


@pytest_asyncio.fixture(autouse=True)
async def db():
    db_name = f"test_{uuid.uuid4().hex}"
    test_database = Database(f'sqlite+aiosqlite:///file:{db_name}?mode=memory&cache=shared&uri=true')

    engine = create_engine(f'sqlite:///file:{db_name}?mode=memory&cache=shared&uri=true')
    metadata.create_all(engine)
    engine.dispose()

    await test_database.connect()

    with (
        patch('app.core.database.database', test_database),
        patch('app.core.crud_base.database', test_database),
        patch('app.company.dal.database', test_database),
        patch('app.employee.dal.database', test_database),
        patch('app.project.dal.database', test_database),
        patch('app.task.dal.database', test_database),
        patch('app.time_tracking.dal.database', test_database)
    ):
        yield test_database

    await test_database.disconnect()
