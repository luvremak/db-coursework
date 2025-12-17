import os
import uuid
from unittest.mock import patch

import pytest_asyncio
from databases import Database
from sqlalchemy import create_engine

from app.core.database import metadata


@pytest_asyncio.fixture(autouse=True)
async def db():
    db_file = f"test_{uuid.uuid4().hex}.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    sync_url = f"sqlite:///{db_file}"

    engine = create_engine(sync_url)
    metadata.create_all(engine)
    engine.dispose()

    test_database = Database(db_url)
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
    if os.path.exists(db_file):
        os.remove(db_file)
