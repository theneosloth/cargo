import logging

from redis.commands.search.field import TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.exceptions import ConnectionError, ResponseError, TimeoutError
from requests_cache import CachedSession, RedisCache  # type: ignore

from .cache import RedisCache as CargoCache

TABLE_NAME = "movesIdx"


# TODO: definitely not the right place for this
def get_requests_session() -> CachedSession:
    try:
        backend = RedisCache(connection=CargoCache().client)
        CargoCache().client.ping()
        return CachedSession(backend=backend, expire_after=60 * 60 * 24)
    except (AttributeError, ValueError, ConnectionError, TimeoutError) as e:
        logging.warning(f"Unable to connect to Redis, falling back to temp files: {e}")
        return CachedSession(use_temp=True)


def create_redis_index() -> None:
    try:
        c = CargoCache().client

        try:
            c.ping()
        except (AttributeError, ValueError, ConnectionError, TimeoutError) as e:
            logging.warn(f"Unable to connect to Redis. Not creating an index: {e}")
            return

        schema = (
            TagField("$._pageName", as_name="_pageName", separator=";"),
            TagField("$.chara", as_name="chara", separator=";"),
            TagField("$.input", as_name="input", separator=";"),
            TextField("$.id", as_name="id"),
            TextField("$.name", as_name="name", phonetic_matcher="dm:en"),
        )

        rs = c.ft(TABLE_NAME)
        r = rs.create_index(
            schema,
            definition=IndexDefinition(prefix=["moves"], index_type=IndexType.JSON),  # type: ignore
        )
        if r != b"OK":
            raise ValueError(f"Failed to create an index.: {r}")

    except ResponseError:
        logging.warn("Index already exists. Attempting to recreate")
        rs.dropindex()
        create_redis_index()
