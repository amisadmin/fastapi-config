[简体中文](https://github.com/amisadmin/fastapi_config/blob/master/README.zh.md)
| [English](https://github.com/amisadmin/fastapi_config)

<h2 align="center">
  FastAPI-Config
</h2>
<p align="center">
    <a href="https://pypi.org/project/fastapi-config" target="_blank">
        <img src="https://badgen.net/pypi/v/fastapi-config?color=blue" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/fastapi-config" target="_blank">
        <img src="https://pepy.tech/badge/fastapi-config" alt="Downloads">
    </a>
    <a href="https://gitter.im/amisadmin/fastapi-amis-admin">
        <img src="https://badges.gitter.im/amisadmin/fastapi-amis-admin.svg" alt="Chat on Gitter"/>
    </a>
    <a href="https://jq.qq.com/?_wv=1027&k=U4Dv6x8W" target="_blank">
        <img src="https://badgen.net/badge/qq%E7%BE%A4/229036692/orange" alt="229036692">
    </a>
</p>

## Project Introduction

`Fast API-Config` is a visual dynamic configuration management extension package based on `FastAPI-Amis-Admin`.

## Install

```bash
pip install fastapi-config
```

## Simple example

**main.py**:

```python
from fastapi import FastAPI
from fastapi_amis_admin import amis
from fastapi_amis_admin.admin import Settings, AdminSite
from fastapi_amis_admin.models import Field
from fastapi_config import ConfigModelAdmin, DbConfigStore, ConfigAdmin
from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import List

# Create a `FastAPI` application
app = FastAPI()

# Create `AdminSite` instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))

# Create a configuration repository
dbconfig = DbConfigStore(site.db)

# Register Admin (optional)
site.register_admin(ConfigModelAdmin)


class ContactCfg(BaseModel):
    name: str = Field("", title="联系人")
    qq: List[str] = Field("", title="QQ")


class SiteCfg(BaseModel):
    name: str = Field(..., title="网站名称")
    logo: str = Field("", title="网站LOGO", amis_form_item=amis.InputImage())
    contacts: List[ContactCfg] = Field([], title="客服列表")
    domains: List[str] = Field([], title='域名列表')


class SiteCfgAdmin(ConfigAdmin):
    page_schema = amis.PageSchema(label='站点信息')
    schema = SiteCfg


site.register_admin(SiteCfgAdmin)


@app.get('/config')
async def read_config():
    return await dbconfig.get(SiteCfg)


@app.on_event("startup")
async def startup():
    # Mount the site to the FastAPI instance
    site.mount_app(app)
    # Create database tables (required for first run)
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True)
```

## Interface/UI Preview

- Open `http://127.0.0.1:8000/admin/` in your browser:

![SchedulerAdmin](https://img-blog.csdnimg.cn/0e3b49a10f2d4f65977b60b3fc35057f.png#pic_center)

## Dependendent project

- [FastAPI-Amis-Admin](https://docs.amis.work/)

## License

The project follows the Apache2.0 license agreement.
