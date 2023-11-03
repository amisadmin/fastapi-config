from typing import Dict, Optional, Type, TypeVar, Union, overload

import asyncer
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy_database import AbcAsyncDatabase, AsyncDatabase, Database

from fastapi_config.models import ConfigModel

_BaseModelT = TypeVar("_BaseModelT", bound="BaseModel")
_KT = Union[str, Type[_BaseModelT]]


class BaseConfigCache:
    """缓存基类"""

    def __init__(self):
        self.__cached__: Dict[_KT, ConfigModel] = {}

    def get(self, k: _KT) -> Optional[ConfigModel]:
        return self.__cached__.get(k, None)

    def set(self, k: _KT, v: ConfigModel):
        self.__cached__[k] = v

    def delete(self, k: _KT):
        if k in self.__cached__:
            self.__cached__.pop(k)

    def exists(self, k: _KT) -> bool:
        return k in self.__cached__


class BaseConfigStore:
    def __init__(self, *, config_cache: BaseConfigCache = None):
        self._config_cache: BaseConfigCache = config_cache or BaseConfigCache()

    async def read(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        """读取配置存储库中ConfigModel对象"""
        raise NotImplementedError()

    async def save(self, k: _KT, data: str) -> bool:
        """保存ConfigModel对象到存储库,如果不存在则插入,并且更新缓存."""
        if not data:
            return False
        self._config_cache.delete(k)
        return True

    @overload
    async def get(self, k: str, cache: bool = True) -> Optional[str]:
        ...

    @overload
    async def get(self, k: Type[_BaseModelT], cache: bool = True) -> Optional[_BaseModelT]:
        ...

    async def get(self, k: _KT, cache: bool = True) -> Optional[Union[_BaseModelT, str]]:
        obj = await self.read(k, cache=cache)
        return self._get_after(k, obj)

    @overload
    async def set(self, k: _BaseModelT, v: str = None):
        ...

    @overload
    async def set(self, k: _KT, v: str):
        ...

    async def set(self, k: Union[_KT, _BaseModelT], v: str = None):
        """保存数据到存储库;如果不存在则插入"""
        key, data = self._set_before(k, v)
        await self.save(key, data=data)

    """以下方法为同步方法,非必要不推荐频繁调用;如需频繁调用,可重写`sread`,`ssave`方法."""

    def sread(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        """读取配置,同步调用方法"""
        if not cache or self._config_cache.exists(k):
            return asyncer.syncify(self.read, raise_sync_error=False)(k=k, cache=cache)
        return self._config_cache.get(k)

    def ssave(self, k: _KT, data: str) -> bool:
        """保存配置,同步调用方法"""
        return asyncer.syncify(self.save, raise_sync_error=False)(k, data)

    @overload
    def sget(self, k: str, cache: bool = True) -> Optional[str]:
        ...

    @overload
    def sget(self, k: Type[_BaseModelT], cache: bool = True) -> Optional[_BaseModelT]:
        ...

    def sget(self, k: _KT, cache: bool = True) -> Optional[Union[_BaseModelT, str]]:
        obj = self.sread(k, cache=cache)
        return self._get_after(k, obj)

    @overload
    def sset(self, k: _BaseModelT, v: str = None):
        ...

    @overload
    def sset(self, k: _KT, v: str):
        ...

    def sset(self, k: Union[_KT, _BaseModelT], v: str = None):
        """保存数据到存储库;如果不存在则插入"""
        key, data = self._set_before(k, v)
        self.ssave(key, data=data)

    def _set_before(self, k: Union[_KT, _BaseModelT], v: str = None):
        if issubclass(type(k), BaseModel):
            key, data = k.__class__, k.json(by_alias=True)
        else:
            key, data = k, v
        return key, data

    def _get_after(self, k: _KT, obj: Optional[ConfigModel]):
        if not obj:
            return None
        return obj.data if isinstance(k, str) else k.parse_raw(obj.data)


class DbConfigStore(BaseConfigStore):
    __instances__: Dict[AbcAsyncDatabase, "DbConfigStore"] = {}

    def __new__(cls, db: Union[Database, AsyncDatabase], **kwargs):
        if db in cls.__instances__:
            return cls.__instances__[db]
        instance = super().__new__(cls, **kwargs)
        cls.__instances__[db] = instance
        return instance

    def __init__(self, db: Union[Database, AsyncDatabase], *, config_cache: BaseConfigCache = None):
        super().__init__(config_cache=config_cache)
        self.db = db

    def _read_config(self, session: Session, k: _KT):
        key = ConfigModel.get_key(k)
        stmt = select(ConfigModel).where(ConfigModel.key == key)
        obj = session.scalar(stmt)
        return obj

    def _save_config(self, session: Session, k: _KT, data: str):
        key = ConfigModel.get_key(k)
        obj = self._read_config(session, k=k)
        if obj is None:
            obj = ConfigModel(key=key, name=key, data=data)
            session.add(obj)
        else:
            stmt = update(ConfigModel).where(ConfigModel.key == key).values(data=data)
            session.execute(stmt)
        session.commit()

    async def read(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        if not cache or not self._config_cache.exists(k):
            obj = await self.db.async_run_sync(self._read_config, k=k)
            obj = obj.copy() if obj else None  # fix: sqlalchemy Instance is not bound to a Session
            self._config_cache.set(k, obj)
            return obj
        return self._config_cache.get(k)

    async def save(self, k: _KT, data: str) -> bool:
        async with self.db():  # Create a new session
            await self.db.async_run_sync(self._save_config, k=k, data=data)
        self._config_cache.delete(k)
        return True

    def sread(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        if not cache or not self._config_cache.exists(k):
            if isinstance(self.db, Database):
                obj = self._read_config(self.db.session, k=k)
            else:
                obj = asyncer.syncify(self.db.async_run_sync, raise_sync_error=False)(self._read_config, k=k)
            obj = obj.copy() if obj else None  # fix: sqlalchemy Instance is not bound to a Session
            self._config_cache.set(k, obj)
            return obj
        return self._config_cache.get(k)

    def ssave(self, k: _KT, data: str) -> bool:
        if isinstance(self.db, AsyncDatabase):
            return super().ssave(k=k, data=data)
        with self.db():  # Create a new session
            self._save_config(self.db.session, k=k, data=data)
        self._config_cache.delete(k)
        return True
