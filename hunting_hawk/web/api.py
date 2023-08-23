"""REST web service for retreiving frame data"""
import logging
from typing import Annotated, Callable, List, Optional

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

app = FastAPI()
cache = FallbackCache()


def get_characters(m: CargoFetcher, tasks: BackgroundTasks) -> Callable[[], list[str]]:
    def wrapped() -> list[str]:
        cache_key = f"characterlist:{m.table_name}".lower()

        try:
            if r := cache.get_list(cache_key):
                return r
        except Exception as e:
            logging.error(f"Character cache lookup failed with {e}")

        res = list(m)
        tasks.add_task(cache.set_list, cache_key, res)
        return res

    return wrapped


def get_moves(
    m: CargoFetcher, tasks: BackgroundTasks
) -> Callable[[str, Optional[str]], list[Move] | JSONResponse]:
    def wrapped(
        character: str, move: Annotated[str | None, Query(max_length=10)] = None
    ) -> list[Move] | JSONResponse:
        if move is not None:
            move = normalize.normalize(move)
            cache_key = f"characters:{m.table_name}:{character}:{move}".lower()
            try:
                if r := cache.get_json(cache_key):
                    return JSONResponse(content=jsonable_encoder(r))
            except Exception as e:
                logging.error(f"Cache lookup failed with {e}")
            moves = m.get_moves_by_input(character, move)
        else:
            cache_key = f"characters:{m.table_name}:{character}:list".lower()
            if r := cache.get_json(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves(character)
        if len(moves) == 1:
            tasks.add_task(cache.set_json, cache_key, moves[0], pydantic_encoder)
        return moves

    return wrapped


@app.get("/BBCF/characters/", response_model=List[str])
def bbcf_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(BBCF, background_tasks)()


@app.get("/BBCF/characters/{character}/", response_model=List[BBCF.move])  # type: ignore
def bbcf_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(BBCF, background_tasks)(character, move)


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
def p4u2r_moves(
    character: str,
    background_tasks: BackgroundTasks,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(P4U2R, background_tasks)(character, move)


@app.get("/P4U2R/characters/", response_model=List[str])
def p4u2r_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(P4U2R, background_tasks)()


@app.get("/HNK/characters/", response_model=List[str])
def hnk_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(HNK, background_tasks)()


@app.get("/HNK/characters/{character}/", response_model=List[HNK.move])  # type: ignore
def hnk_moves(
    character: str, move: Annotated[str | None, Query(max_length=10)] = None
) -> list[Move] | JSONResponse:
    if move is not None:
        return HNK.get_moves_by_input(character, move)
    return HNK.get_moves(character)


@app.get("/GGACR/characters/", response_model=List[str])
def ggacr_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(GGACR, background_tasks)()


@app.get("/GGACR/characters/{character}/", response_model=List[GGACR.move])  # type: ignore
def ggacr_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(GGACR, background_tasks)(character, move)


@app.get("/MBTL/characters/", response_model=List[str])
def mbtl_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(MBTL, background_tasks)()


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
def mbtl_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(MBTL, background_tasks)(character, move)


@app.get("/SCVI/characters/", response_model=List[str])
def scvi_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SCVI, background_tasks)()


@app.get("/SCVI/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
def scvi_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(SCVI, background_tasks)(character, move)


@app.get("/SF6/characters/", response_model=List[str])
def sf6_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SF6, background_tasks)()


@app.get("/SF6/characters/{character}/", response_model=List[SF6.move])  # type: ignore
def sf6_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(SF6, background_tasks)(character, move)


@app.get("/KOFXV/characters/", response_model=List[str])
def kofxv_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(KOFXV, background_tasks)()


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
def kofxv_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=10)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(KOFXV, background_tasks)(character, move)
