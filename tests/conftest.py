from typing import Union

import pytest
from sqlalchemy_database import AsyncDatabase, Database
from sqlmodel import SQLModel

from fastapi_config import DbConfigStore
from fastapi_config.backends import BaseConfigCache

# sqlite
sync_db = Database.create("sqlite:///amisadmin.db?check_same_thread=False")
async_db = AsyncDatabase.create("sqlite+aiosqlite:///amisadmin.db?check_same_thread=False")


@pytest.fixture(params=[async_db, sync_db])
async def db(request) -> Union[Database, AsyncDatabase]:
    database = request.param
    await database.async_run_sync(SQLModel.metadata.create_all, is_session=False)
    yield database
    await database.async_run_sync(SQLModel.metadata.drop_all, is_session=False)
    await database.async_close()


@pytest.fixture
def config_cache() -> BaseConfigCache:
    # import redis
    # from fastapi_config.extensions.redis import RedisConfigCache
    # redis_dsn=""
    # rds: redis.Redis = redis.from_url(redis_dsn, encoding="utf-8", decode_responses=True)
    # return RedisConfigCache(rds)
    return BaseConfigCache()


@pytest.fixture
def config_store(db, config_cache) -> DbConfigStore:
    return DbConfigStore(db=db, config_cache=config_cache)
