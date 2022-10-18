from typing import List

from fastapi_amis_admin import amis
from fastapi_amis_admin.models import Field
from pydantic import BaseModel, EmailStr


class ContactCfg(BaseModel):
    name: str = Field("", title="联系人")
    qq: List[str] = Field("", title="QQ")


class SiteCfg(BaseModel):
    name: str = Field(..., title="网站名称")
    logo: str = Field("", title="网站LOGO", amis_form_item=amis.InputImage())
    contacts: List[ContactCfg] = Field([], title="客服列表")
    domains: List[str] = Field([], title="域名列表")


class SmtpCfg(BaseModel):
    host: str = Field(..., title="SMTP服务器")
    port: int = Field(..., title="SMTP端口")
    email: EmailStr = Field(..., title="邮箱账号", amis_form_item=amis.InputText(type="input-email"))
    password: str = Field("", title="密码")
