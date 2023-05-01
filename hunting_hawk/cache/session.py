import logging

from redis.exceptions import ConnectionError
from requests_cache import CachedSession, RedisCache  # type: ignore

from .cache import RedisCache as CargoCache

# Fails to import RedisCache, but it is there


# TODO: definitely not the right place for this
def get_requests_session() -> CachedSession:
    try:
        backend = RedisCache(connection=CargoCache().client)
        CargoCache().client.ping()
        return CachedSession(backend=backend, expire_after=60 * 60 * 24)
    except (AttributeError, ValueError, ConnectionError) as e:
        logging.info(f"Unable to connect to Redis, falling back to temp files: {e}")
        return CachedSession(use_temp=True)
