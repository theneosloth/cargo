import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

import redis


class Cache(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

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
    def set_json(self, key: str, val: Any, encoder: Callable[[Any], Any]) -> list[Any]:
        pass

    @abstractmethod
    def get_json(self, key: str) -> Any:
        pass


class RedisCache(Cache):
    expiry: int = 60 * 60 * 24 * 7
    _shared_state: dict[Any, Any] = {}

    # Red alert: Borg pattern
    def __init__(self) -> None:
        self.__dict__ = self._shared_state

    def connect(self) -> None:
        url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(url, socket_connect_timeout=2)

    def get(self, key: str) -> Optional[str]:
        res = self.client.get(key)
        if res:
            return res.decode("utf-8")
        return None

    def set(self, key: str, val: str) -> Optional[bool]:
        return self.client.set(key, val, ex=self.expiry)

    def get_list(self, key: str) -> list[str]:
        r = [b.decode("utf-8") for b in self.client.lrange(key, 0, -1)]
        return r

    def set_list(self, key: str, vals: list[str]) -> list[Any]:
        pipe = self.client.pipeline()
        pipe.delete(key)
        pipe.rpush(key, *vals)
        pipe.expire(key, self.expiry)
        return pipe.execute()

    def set_json(self, key: str, val: Any, encoder: Callable[[Any], Any]) -> list[Any]:
        pipe = self.client.pipeline()
        pipe.json().set(key, "$", encoder(val))
        pipe.expire(key, self.expiry)
        return pipe.execute()

    def get_json(self, key: str) -> Any:
        if self.client.type(key) != "ReJSON-RL":  # type: ignore
            return None
        return self.client.json().get(key)


class DictCache(Cache):
    _data: dict[str, Any] = {}

    def connect(self) -> None:
        return None

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

    def set_json(self, key: str, val: Any, encoder: Callable[[Any], Any]) -> list[Any]:
        self._data[key] = encoder(val)
        return []

    def get_json(self, key: str) -> Any:
        if key not in self._data:
            return []
        val = self._data[key]
        match val:
            case list() | dict():
                return val
            case _:
                self._data[key] = None
                return None


class FallbackCache(Cache):
    selected_cache: Cache

    def __init__(self) -> None:
        try:
            self.selected_cache = RedisCache()
            self.connect()
            self.selected_cache.client.ping()
        except (
            ValueError,
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
        ) as e:
            logging.info(
                f"Unable to connect to Redis, falling back to an in memory dict: {e}"
            )
            self.selected_cache = DictCache()

    def connect(self) -> None:
        return self.selected_cache.connect()

    def get(self, key: str) -> Optional[str]:
        return self.selected_cache.get(key)

    def set(self, key: str, val: str) -> Optional[bool]:
        return self.selected_cache.set(key, val)

    def get_list(self, key: str) -> list[str]:
        return self.selected_cache.get_list(key)

    def set_list(self, key: str, val: list[str]) -> list[Any]:
        return self.selected_cache.set_list(key, val)

    def set_json(self, key: str, val: Any, encoder: Callable[[Any], Any]) -> list[Any]:
        return self.selected_cache.set_json(key, val, encoder)

    def get_json(self, key: str) -> Any:
        return self.selected_cache.get_json(key)
