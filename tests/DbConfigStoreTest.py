import pytest
from pydantic import BaseModel

from fastapi_config import DbConfigStore
from tests.conftest import site

config = DbConfigStore(db = site.db)

class SiteConfig(BaseModel):
    name: str = ''
    url: str = ''

@pytest.mark.asyncio
async def test_string_key():
    key = 'key1'
    val = 'value1'
    data = await config.get(key)
    assert data is None

    await config.set(key, val)
    data = await config.get(key)
    assert data == val

@pytest.mark.asyncio
async def test_schema_key():
    key = SiteConfig
    data = await config.get(key)
    assert data is None

    val = SiteConfig(name = 'amisadmin', url = 'https://docs.amis.work')
    await config.set(val)
    data = await config.get(key)
    assert data == val

    val2 = SiteConfig(name = 'amisadmin2', url = 'https://docs.amis.work')
    await config.set(SiteConfig, val2.json())
    data = await config.get(key)
    assert data == val2
