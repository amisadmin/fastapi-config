from typing import Any

from fastapi_amis_admin import admin
from fastapi_amis_admin.admin import AdminApp
from fastapi_amis_admin.amis import PageSchema, Form, DisplayModeEnum
from fastapi_amis_admin.crud import BaseApiOut
from fastapi_amis_admin.utils.translation import i18n as _
from pydantic import BaseModel
from starlette.requests import Request

from .backends import DbConfigStore, BaseConfigStore
from .models import ConfigModel

class ConfigModelAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label = _('Configuration'), icon = 'fa fa-group')
    model = ConfigModel
    readonly_fields = ['key']

class ConfigAdmin(admin.FormAdmin):
    router_prefix: str = '/config'
    config_store: BaseConfigStore = None
    form_init = True
    form = Form(mode = DisplayModeEnum.horizontal)

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.config_store = self.config_store or DbConfigStore(db = self.site.db)

    @property
    def page_path(self):
        return f'/{getattr(self.schema, "__key__", self.schema.__name__).lower()}'

    async def handle(self, request: Request, data: BaseModel, **kwargs) -> BaseApiOut[Any]:
        return BaseApiOut(data = await self.config_store.set(data))

    async def get_init_data(self, request: Request, **kwargs) -> BaseApiOut[Any]:
        return BaseApiOut(data = await self.config_store.get(self.schema, cache = False))
