from typing import Union

import pytest
from sqlalchemy_database import AsyncDatabase, Database
from sqlmodel import SQLModel

from fastapi_config import BaseConfigStore, DbConfigStore

# sqlite
sync_db = Database.create("sqlite:///amisadmin.db?check_same_thread=False")
async_db = AsyncDatabase.create("sqlite+aiosqlite:///amisadmin.db?check_same_thread=False")


@pytest.fixture(params=[async_db, sync_db])
async def db(request) -> Union[Database, AsyncDatabase]:
    database = request.param
    await database.async_run_sync(SQLModel.metadata.create_all, is_session=False)
    yield database
    await database.async_run_sync(SQLModel.metadata.drop_all, is_session=False)


@pytest.fixture
def config_store(db) -> BaseConfigStore:
    return DbConfigStore(db=db)
