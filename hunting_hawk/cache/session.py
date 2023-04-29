from requests_cache import CachedSession, RedisCache  # type: ignore

from .cache import RedisCache as CargoCache

# Fails to import RedisCache, but it is there


# TODO: definitely not the right place for this
def get_requests_session() -> CachedSession:
    try:
        backend = RedisCache(connection=CargoCache().client)
        return CachedSession(backend=backend, expire_after=60 * 60 * 24)
    except AttributeError:
        return CachedSession(use_temp=True)
