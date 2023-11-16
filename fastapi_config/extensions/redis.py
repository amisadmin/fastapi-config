from typing import Optional

from redis import Redis

from fastapi_config import ConfigModel
from fastapi_config.backends import BaseConfigCache, _KT


class RedisConfigCache(BaseConfigCache):
    """Redis缓存"""

    def __init__(self, redis_client: Redis, default_expire: int = 60 * 60 * 24):
        super().__init__()
        self.redis_client = redis_client
        self.default_expire = default_expire

    def _get_cache_key(self, k: _KT) -> str:
        key = ConfigModel.get_key(k)
        return f"config:{key}"

    def get(self, k: _KT) -> Optional[ConfigModel]:
        key = self._get_cache_key(k)
        data = self.redis_client.get(key)
        if data:
            return ConfigModel.parse_raw(data)
        return None

    def set(self, k: _KT, v: ConfigModel):
        key = self._get_cache_key(k)
        value=v.json(by_alias=True) if v else ''
        self.redis_client.set(key, value, ex=self.default_expire)

    def delete(self, k: _KT):
        key = self._get_cache_key(k)
        self.redis_client.delete(key)

    def exists(self, k: _KT) -> bool:
        key = self._get_cache_key(k)
        return self.redis_client.exists(key)
