"""REST web service for retreiving frame data"""
from contextlib import asynccontextmanager
from typing import Annotated, Callable, List, Optional
from redis import asyncio as aioredis
from fastapi import BackgroundTasks, FastAPI, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic.json import pydantic_encoder

from hunting_hawk.cache.cache import FallbackCache
from hunting_hawk.mediawiki.cargo import Move
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import BBCF, GGACR, HNK, P4U2R
from hunting_hawk.sites.fetcher import CargoFetcher
from hunting_hawk.sites.mizuumi import MBTL
from hunting_hawk.sites.supercombo import SCVI, SF6
from hunting_hawk.util import normalize

async def initialize_index():
    try:
        await aioredis.execute_command()
    except Exception as e:
        raise e

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = FallbackCache()
    yield


app = FastAPI(lifespan=lifespan)


async def get_characters(m: CargoFetcher, tasks: BackgroundTasks) -> Callable[[], list[str]]:
    async def wrapped() -> list[str]:
        cache_key = f"characterlist:{m.table_name}".lower()

        if r := cache.get_list(cache_key):
            return r

        res = list(m)
        tasks.add_task(cache.set_list, cache_key, res)
        return res

    return wrapped


async def get_moves(
    m: CargoFetcher, tasks: BackgroundTasks
) -> Callable[[str, Optional[str]], list[Move] | JSONResponse]:
    async def wrapped(
        character: str, move: Annotated[str | None, Query(max_length=10)] = None
    ) -> list[Move] | JSONResponse:
        if move is not None:
            move = normalize.normalize(move)
            character = normalize.normalize(character)
            cache_key = f"movedata:{m.table_name}:{character}:{move}".lower()
            if r := cache.get_json(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves_by_input(character, move)
        else:
            cache_key = f"movedata:{m.table_name}:{character}:all".lower()
            if r := cache.get_json(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves(character)
        tasks.add_task(cache.set_json, cache_key, moves, pydantic_encoder)
        return moves

    return wrapped


@app.get("/BBCF/characters/", response_model=List[str])
async def bbcf_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(BBCF, background_tasks)()


@app.get("/BBCF/characters/{character}/", response_model=List[BBCF.move])  # type: ignore
async def bbcf_find_move(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(BBCF, background_tasks)(character, move)


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
async def p4u2r_find_move(
    character: str,
    background_tasks: BackgroundTasks,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(P4U2R, background_tasks)(character, move)


@app.get("/P4U2R/characters/", response_model=List[str])
async def p4u2r_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(P4U2R, background_tasks)()


@app.get("/HNK/characters/", response_model=List[str])
async def hnk_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(HNK, background_tasks)()


@app.get("/HNK/characters/{character}/", response_model=List[HNK.move])  # type: ignore
async def hnk_find_move(
    character: str, move: Annotated[str | None, Query(max_length=10)] = None
) -> list[Move] | JSONResponse:
    return get_moves(HNK, background_tasks)(character, move)


@app.get("/GGACR/characters/", response_model=List[str])
async def ggacr_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(GGACR, background_tasks)()


@app.get("/GGACR/characters/{character}/", response_model=List[GGACR.move])  # type: ignore
async def ggacr_find_move(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(GGACR, background_tasks)(character, move)


@app.get("/MBTL/characters/", response_model=List[str])
async def mbtl_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(MBTL, background_tasks)()


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
async def mbtl_find_move(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(MBTL, background_tasks)(character, move)


@app.get("/SCVI/characters/", response_model=List[str])
async def scvi_get_characters(background_tasks: BackgroundTasks) -> List[str]:
    """Incomplete. Inputs are stored as image file names."""
    return get_characters(SCVI, background_tasks)()


@app.get("/SCVI/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
async def scvi_get_move(
    background_tasks: BackgroundTasks,
    character: str
) -> list[Move] | JSONResponse:
    """Incomplete. Only supports retrieving all of character's moves."""
    return get_moves(SCVI, background_tasks)(character, None)


@app.get("/SF6/characters/", response_model=List[str])
async def sf6_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SF6, background_tasks)()


@app.get("/SF6/characters/{character}/", response_model=List[SF6.move])  # type: ignore
async def sf6_find_move(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(SF6, background_tasks)(character, move)


@app.get("/KOFXV/characters/", response_model=List[str])
async def kofxv_list_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(KOFXV, background_tasks)()


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
async def kofxv_find_move(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(KOFXV, background_tasks)(character, move)
