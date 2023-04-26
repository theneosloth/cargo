import logging
import os
from abc import ABC, abstractmethod
from json import dumps
from typing import Any, Optional

import redis
from pydantic.json import pydantic_encoder

from hunting_hawk.mediawiki.cargo import Move


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set(self, key: str, val: str) -> Optional[bool]:
        pass

    @abstractmethod
    def get_list(self, key: str) -> list[str]:
        pass

    @abstractmethod
    def set_list(self, key: str, vals: list[str]) -> list[Any]:
        pass

    @abstractmethod
    def set_model(self, key: str, val: list[Move]) -> list[Any]:
        pass

    @abstractmethod
    def get_model(self, key: str) -> Optional[dict[Any, Any]]:
        pass


class RedisCache(Cache):
    expiry: int = 60 * 60 * 24 * 7

    def __init__(self, url: str) -> None:
        self.client = redis.from_url(url)

    def get(self, key: str) -> Optional[str]:
        res = self.client.get(key)
        if res:
            return res.decode("utf-8")
        return None

    def set(self, key: str, val: str) -> Optional[bool]:
        return self.client.set(key, val, ex=self.expiry)

    def get_list(self, key: str) -> list[str]:
        if self.client.type(key) != "list":  # type: ignore
            # Potentially invalidate the data here?
            return []
        return [b.decode("utf-8") for b in self.client.lrange(key, 0, -1)]

    def set_list(self, key: str, vals: list[str]) -> list[Any]:
        pipe = self.client.pipeline()
        pipe.delete(key)
        pipe.rpush(key, *vals)
        pipe.expire(key, self.expiry)
        return pipe.execute()

    def set_model(self, key: str, val: list[Move]) -> list[Any]:
        json_vals = dumps(val, default=pydantic_encoder)
        pipe = self.client.pipeline()
        pipe.json().set(key, "$", json_vals)
        pipe.expire(key, self.expiry)
        return pipe.execute()

    def get_model(self, key: str) -> Optional[dict[Any, Any]]:
        if self.client.type(key) != "ReJSON-RL":  # type: ignore
            # Potentially invalidate the data here?
            return None
        res = self.client.json().get(key)
        match res:
            case dict():
                return res
            case _:
                return None


class DictCache(Cache):
    _data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self._data:
            return None

        val = self._data[key]
        if type(val) is str:
            return val
        raise

    def set(self, key: str, val: str) -> Optional[bool]:
        self._data[key] = val
        return True

    def get_list(self, key: str) -> list[str]:
        if key not in self._data:
            return []

        val = self._data[key]
        match val:
            case list():
                return val
            case _:
                raise

    def set_list(self, key: str, val: list[str]) -> list[Any]:
        self._data[key] = val
        return val

    def set_model(self, key: str, val: list[Move]) -> list[Any]:
        json_vals = dumps(val, indent=2, default=pydantic_encoder)
        self._data[key] = json_vals
        return []

    def get_model(self, key: str) -> Optional[dict[Any, Any]]:
        if key not in self._data:
            return {}
        val = self._data[key]
        match val:
            case dict():
                return val
            case _:
                self._data[key] = None
                return None


class FallbackCache(Cache):
    selected_cache: Cache

    def __init__(self) -> None:
        try:
            url = os.environ.get("REDIS_HOST", "redis://localhost:6379")
            self.redis_cache = RedisCache(url=url)
            if self.redis_cache.client.ping():
                self.selected_cache = self.redis_cache
            else:
                raise ValueError("Redis ping failed")
        except (ValueError, redis.exceptions.ConnectionError) as e:
            logging.warning(
                f"Unable to connect to Redis, falling back to an in memory dict: {e}"
            )
            self.selected_cache = DictCache()

    def get(self, key: str) -> Optional[str]:
        return self.selected_cache.get(key)

    def set(self, key: str, val: str) -> Optional[bool]:
        return self.selected_cache.set(key, val)

    def get_list(self, key: str) -> list[str]:
        return self.selected_cache.get_list(key)

    def set_list(self, key: str, val: list[str]) -> list[Any]:
        return self.selected_cache.set_list(key, val)

    def set_model(self, key: str, val: list[Move]) -> list[Any]:
        return self.selected_cache.set_model(key, val)

    def get_model(self, key: str) -> Optional[dict[Any, Any]]:
        return self.selected_cache.get_model(key)
