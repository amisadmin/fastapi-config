<h2 align="center">
  FastAPI-Config
</h2>

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

# 创建`FastAPI`应用
app = FastAPI()

# 创建`AdminSite`实例
site = AdminSite(settings = Settings(database_url_async = 'sqlite+aiosqlite:///amisadmin.db'))

# 创建配置存储库
dbconfig = DbConfigStore(site.db)

# 注册管理页面(可选)
site.register_admin(ConfigModelAdmin)

class SiteCfg(BaseModel):
    name: str = Field(..., title = '网站名称')
    logo: str = Field('', title = '网站LOGO', amis_form_item = amis.InputImage())

class SiteCfgAdmin(ConfigAdmin):
    page_schema = amis.PageSchema(label = '站点信息')
    schema = SiteCfg

site.register_admin(SiteCfgAdmin)

@app.get('/config')
async def read_config():
    return await dbconfig.get(SiteCfg)

@app.on_event("startup")
async def startup():
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session = False)

# 挂载后台管理系统
site.mount_app(app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug = True)
```

## 界面预览

- Open `http://127.0.0.1:8000/admin/` in your browser:

![SchedulerAdmin](https://s2.loli.net/2022/05/10/QEtCLsWi1389BKH.png)

## 依赖项目

- [FastAPI-Amis-Admin](https://docs.amis.work/)

## 许可协议

该项目遵循 Apache2.0 许可协议。
