from fastapi_amis_admin import globals as g

from fastapi_config import BaseConfigStore, DbConfigStore

config_store: BaseConfigStore


def __getattr__(name: str):
    if name == "config_store" and not hasattr(g, name):
        return DbConfigStore(g.site.db)
    return getattr(g, name)
