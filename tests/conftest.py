import asyncio

import pytest
from fastapi_amis_admin.admin import AdminSite, Settings
from sqlmodel import SQLModel

site = AdminSite(settings=Settings(debug=False, database_url_async="sqlite+aiosqlite:///:memory:"))


@pytest.fixture(scope="session", autouse=True)
def startup():
    asyncio.run(init_db())


async def init_db():
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)
