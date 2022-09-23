from fastapi_amis_admin import admin, amis
from fastapi_amis_admin.admin import AdminApp

from demo.config import SiteCfg, SmtpCfg
from fastapi_config import ConfigAdmin


class BaseCfgApp(admin.AdminApp):
    tabs_mode = amis.TabsModeEnum.chrome
    page_schema = amis.PageSchema(label="基础配置")

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.register_admin(SiteCfgAdmin, SmtpCfgAdmin)


class SiteCfgAdmin(ConfigAdmin):
    page_schema = amis.PageSchema(label="站点信息")
    schema = SiteCfg


class SmtpCfgAdmin(ConfigAdmin):
    page_schema = amis.PageSchema(label="SMTP设置")
    schema = SmtpCfg
