import logging
import os
from abc import ABC, abstractmethod
from json import JSONDecodeError, dumps, loads
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
    def set_json(
        self, key: str, val: Any, encoder: Optional[Callable[[Any], Any]]
    ) -> Optional[bool]:
        pass

    @abstractmethod
    def get_json(self, key: str) -> Optional[list[Any]]:
        pass


class RedisCache(Cache):
    expiry: int = 60 * 60 * 24 * 7
    _shared_state: dict[Any, Any] = {}

    # Red alert: Borg pattern
    def __init__(self) -> None:
        self.__dict__ = self._shared_state

    def connect(self) -> None:
        url = os.environ.get("REDIS_HOST", "redis://localhost:6379")
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

    def set_json(
        self, key: str, val: Any, encoder: Optional[Callable[[Any], Any]]
    ) -> Optional[bool]:
        json_vals = dumps(val, default=encoder)
        return self.client.set(key, json_vals, ex=self.expiry)

    def get_json(self, key: str) -> Any:
        val = self.client.get(key)
        if not val:
            return None
        try:
            json = loads(val)
            match json:
                case dict():
                    return json
                case list():
                    return json
                case _:
                    raise ValueError(f"Value not a list: {json}")
        except (JSONDecodeError, ValueError) as e:
            logging.info(f"Invalid json stored: {e}")
            return None


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

    def set_json(
        self, key: str, val: Any, encoder: Optional[Callable[[Any], Any]]
    ) -> Optional[bool]:
        json_vals = dumps(val, indent=2, default=encoder)
        self._data[key] = json_vals
        return True

    def get_json(self, key: str) -> Optional[list[Any]]:
        if key not in self._data:
            return []
        val = self._data[key]
        match val:
            case list():
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
        except (ValueError, redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
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

    def set_json(
        self, key: str, val: Any, encoder: Optional[Callable[[Any], Any]]
    ) -> Optional[bool]:
        return self.selected_cache.set_json(key, val, encoder)

    def get_json(self, key: str) -> Optional[list[Any]]:
        return self.selected_cache.get_json(key)
