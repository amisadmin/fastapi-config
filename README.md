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

## 项目介绍

`FastAPI-Config`是一个基于`FastAPI-Amis-Admin`的可视化动态配置管理拓展包.

## 安装

```bash
pip install fastapi-config
```

## 简单示例

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

# 创建`FastAPI`应用
app = FastAPI()

# 创建`AdminSite`实例
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))

# 创建配置存储库
dbconfig = DbConfigStore(site.db)

# 注册管理页面(可选)
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
    # 挂载后台管理系统
    site.mount_app(app)
    # 创建数据库表(第一次运行时需要)
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True)
```

## 界面预览

- Open `http://127.0.0.1:8000/admin/` in your browser:

![SchedulerAdmin](https://img-blog.csdnimg.cn/0e3b49a10f2d4f65977b60b3fc35057f.png#pic_center)

## 依赖项目

- [FastAPI-Amis-Admin](https://docs.amis.work/)

## 许可协议

该项目遵循 Apache2.0 许可协议。
