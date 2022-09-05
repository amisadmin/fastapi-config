from fastapi import FastAPI
from fastapi_amis_admin.admin import Settings, AdminSite
from sqlmodel import SQLModel

from demo.admin import BaseCfgApp
from demo.config import SmtpCfg, SiteCfg
from fastapi_config import ConfigModelAdmin, DbConfigStore

# 创建`FastAPI`应用
app = FastAPI()

# 创建`AdminSite`实例
site = AdminSite(settings = Settings(database_url_async = 'sqlite+aiosqlite:///amisadmin.db'))

# 创建配置存储库
dbconfig = DbConfigStore(site.db)

# 注册管理页面(可选)
site.register_admin(ConfigModelAdmin)
site.register_admin(BaseCfgApp)

@app.get('/config')
async def read_config():
    site_cfg = await dbconfig.get(SiteCfg)
    smtp_cfg = await dbconfig.get(SmtpCfg)
    return {
        'site': site_cfg,
        'smtp': smtp_cfg,
    }

@app.on_event("startup")
async def startup():
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session = False)

# 挂载后台管理系统
site.mount_app(app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug = True)
