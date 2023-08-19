import pytest
from fastapi_amis_admin import globals as g
from fastapi_amis_admin.admin import AdminSite, Settings

from fastapi_config import DbConfigStore
from fastapi_config import globals as g2


def test_globals(config_store):
    g.remove_global()
    # test set the config_store
    g.set_global("config_store", config_store)
    assert g2.config_store is config_store
    g.remove_global()
    # test not set the config store
    with pytest.raises(ValueError):
        assert g2.config_store
    g.set_global("site", AdminSite(settings=Settings()))
    assert g.site
    assert g2.config_store is DbConfigStore(g.site.db)
