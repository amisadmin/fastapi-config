from fastapi_amis_admin import amis
from fastapi_amis_admin.models import Field
from fastapi_amis_admin.utils.translation import i18n as _
from sqlalchemy import Column, Text
from sqlmodel import SQLModel


class ConfigModel(SQLModel, table=True):
    __tablename__ = "system_config"
    id: int = Field(default=None, primary_key=True, nullable=False)
    key: str = Field(..., title=_("Identify"), max_length=20, unique=True, index=True, nullable=False)
    name: str = Field(..., title=_("Name"), max_length=20)
    desc: str = Field(default="", title=_("Description"), max_length=400, amis_form_item="textarea")
    data: str = Field(..., title=_("Data"), sa_column=Column(Text, nullable=False), amis_form_item=amis.Editor(language="json"))
