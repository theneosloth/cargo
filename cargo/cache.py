"""Redis wrapper."""
import os
from typing import NewType

import redis.client

second = NewType("second", int)

REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
DEFAULT_EXPIRY: second = second(86400)


class CargoCache:
    """Wrapper around Redis."""

    client: redis.client.Redis
    expiry: second

    def get(self, key: str | bytes) -> str | bytes | None:
        """Return the value at KEY. Always attempts to decode to unicode."""
        val = self.client.get(key)
        match val:
            case bytes():
                try:
                    return val.decode()
                except UnicodeError:
                    return val
            case str():
                return val
            case _:
                return None

    def set(self, key: str, val: str | bytes) -> bool:
        """Set the value at KEY."""
        return self.client.set(key, val, self.expiry) or False

    def set_expiry(self, expiry: second) -> None:
        """Set the default expiry for all cached values."""
        self.expiry = expiry

    def __init__(self, expiry: second = DEFAULT_EXPIRY) -> None:
        """Attempt to connect to redis."""
        self.set_expiry(expiry)
        self.client = redis_connect()


def redis_connect() -> redis.client.Redis:
    """Attempt to connect to redis using environmental variables."""
    client = redis.Redis(
        host="localhost", port=6379, password="", db=0, socket_timeout=5
    )
    ping = client.ping()
    if ping:
        return client
    else:
        raise redis.exceptions.RedisError("Redis ping error")
