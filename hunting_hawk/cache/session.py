from requests_cache import CachedSession, RedisCache  # type: Ignore

from .cache import RedisCache as CargoCache

# Fails to import RedisCache, but it is there


# TODO: definitely not the right place for this
def get_requests_session(cache_name: str) -> CachedSession:
    if CargoCache().client is not None:
        backend = RedisCache(connection=CargoCache().client)
        return CachedSession(cache_name, backend=backend, expire_after=60 * 60 * 24)
    else:
        return CachedSession(cache_name, use_temp=True)
