from functools import cached_property
from typing import Any

from fastapi_amis_admin import admin
from fastapi_amis_admin.amis import DisplayModeEnum, Form, PageSchema
from fastapi_amis_admin.crud import BaseApiOut
from fastapi_amis_admin.utils.translation import i18n as _
from pydantic import BaseModel
from starlette.requests import Request

from .backends import BaseConfigStore, DbConfigStore
from .models import ConfigModel


class ConfigModelAdmin(admin.ModelAdmin):
    unique_id = "Config>ConfigModelAdmin"
    page_schema = PageSchema(label=_("Configuration"), icon="fa fa-cog")
    model = ConfigModel
    create_exclude = {"id", "create_time", "update_time"}
    update_exclude = {"id", "key", "create_time", "update_time"}


class ConfigAdmin(admin.FormAdmin):
    router_prefix: str = "/config"
    form_init = True
    form = Form(mode=DisplayModeEnum.horizontal)

    @cached_property
    def config_store(self) -> BaseConfigStore:
        return DbConfigStore(db=self.site.db)

    @property
    def page_path(self):
        return f'/{getattr(self.schema, "__key__", self.schema.__name__).lower()}'

    async def handle(self, request: Request, data: BaseModel, **kwargs) -> BaseApiOut[Any]:
        return BaseApiOut(data=await self.config_store.set(data))

    async def get_init_data(self, request: Request, **kwargs) -> BaseApiOut[Any]:
        return BaseApiOut(data=await self.config_store.get(self.schema, cache=False))
