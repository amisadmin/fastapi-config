from typing import Dict, Optional, Type, TypeVar, Union, overload

import asyncer
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy_database import AsyncDatabase, Database

from fastapi_config.models import ConfigModel

_BaseModelT = TypeVar("_BaseModelT", bound="BaseModel")
_KT = Union[str, Type[_BaseModelT]]


class BaseConfigStore:
    def __init__(self):
        self.__cached__: Dict[str, ConfigModel] = {}

    def get_key(self, k: _KT) -> str:
        return k if isinstance(k, str) else getattr(k, "__key__", k.__name__)

    def clear_cache(self, k: _KT):
        key = self.get_key(k)
        if key in self.__cached__:
            self.__cached__.pop(key)

    async def read(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        """读取配置存储库中ConfigModel对象"""
        raise NotImplementedError()

    async def save(self, k: _KT, data: str) -> bool:
        """保存ConfigModel对象到存储库,如果不存在则插入,并且更新缓存."""
        if not data:
            return False
        self.clear_cache(k)
        return True

    @overload
    async def get(self, k: str, cache: bool = True) -> Optional[str]:
        ...

    @overload
    async def get(self, k: Type[_BaseModelT], cache: bool = True) -> Optional[_BaseModelT]:
        ...

    async def get(self, k: _KT, cache: bool = True) -> Optional[Union[_BaseModelT, str]]:
        obj = await self.read(k, cache=cache)
        if not obj:
            return None
        return obj.data if isinstance(k, str) else k.parse_raw(obj.data)

    @overload
    async def set(self, k: _BaseModelT, v: str = None):
        ...

    @overload
    async def set(self, k: _KT, v: str):
        ...

    async def set(self, k: Union[_KT, _BaseModelT], v: str = None):
        """保存数据到存储库;如果不存在则插入"""
        if issubclass(type(k), BaseModel):
            key, data = k.__class__, k.json()
        else:
            key, data = k, v
        await self.save(key, data=data)

    """以下方法为同步方法,非必要不推荐频繁调用;如需频繁调用,可重写`sread`,`ssave`方法."""

    def sread(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        """读取配置,同步调用方法"""
        key = self.get_key(k)
        if not cache or key not in self.__cached__:
            return asyncer.syncify(self.read, raise_sync_error=False)(k=k, cache=cache)
        return self.__cached__[key]

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
        if not obj:
            return None
        return obj.data if isinstance(k, str) else k.parse_raw(obj.data)

    @overload
    def sset(self, k: _BaseModelT, v: str = None):
        ...

    @overload
    def sset(self, k: _KT, v: str):
        ...

    def sset(self, k: Union[_KT, _BaseModelT], v: str = None):
        """保存数据到存储库;如果不存在则插入"""
        if issubclass(type(k), BaseModel):
            key, data = k.__class__, k.json()
        else:
            key, data = k, v
        self.ssave(key, data=data)


class DbConfigStore(BaseConfigStore):
    def __init__(self, db: Union[Database, AsyncDatabase]):
        super().__init__()
        self.db = db

    async def read(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        key = self.get_key(k)
        if not cache or key not in self.__cached__:
            stmt = select(ConfigModel).where(ConfigModel.key == key)
            obj = await self.db.async_scalar(stmt)
            self.__cached__[key] = obj.copy() if obj else None  # fix: sqlalchemy Instance is not bound to a Session
        return self.__cached__[key]

    async def save(self, k: _KT, data: str) -> bool:
        obj = await self.read(k, cache=False)
        if obj is None:
            key = self.get_key(k)
            obj = ConfigModel(key=key, name=key, data=data)
            await self.db.async_save(obj)
        else:
            await self.db.async_execute(update(ConfigModel).where(ConfigModel.key == obj.key).values(data=data))
        self.clear_cache(k)
        return True

    def sread(self, k: _KT, cache: bool = True) -> Optional[ConfigModel]:
        key = self.get_key(k)
        if not cache or key not in self.__cached__:
            stmt = select(ConfigModel).where(ConfigModel.key == key)
            if isinstance(self.db, Database):
                obj = self.db.scalar(stmt)
            else:
                obj = asyncer.syncify(self.db.scalar, raise_sync_error=False)(stmt)
            self.__cached__[key] = obj.copy() if obj else None  # fix: sqlalchemy Instance is not bound to a Session
        return self.__cached__[key]

    def ssave(self, k: _KT, data: str) -> bool:
        if not isinstance(self.db, Database):
            return super().ssave(k=k, data=data)
        obj = self.sread(k, cache=False)
        if obj is None:
            key = self.get_key(k)
            obj = ConfigModel(key=key, name=key, data=data)
            self.db.save(obj)
        else:
            self.db.execute(update(ConfigModel).where(ConfigModel.key == obj.key).values(data=data))
        self.clear_cache(k)
        return True
