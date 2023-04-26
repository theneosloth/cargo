"""REST web service for retreiving frame data"""
from json import loads
from typing import Callable, List, Optional

from fastapi import BackgroundTasks, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from hunting_hawk.mediawiki.cargo import Move
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import BBCF, GGACR, HNK, P4U2R
from hunting_hawk.sites.fetcher import CargoFetcher
from hunting_hawk.sites.mizuumi import MBTL
from hunting_hawk.sites.supercombo import SF6

from .cache import FallbackCache

app = FastAPI()
cache = FallbackCache()


def get_characters(m: CargoFetcher, tasks: BackgroundTasks) -> Callable[[], list[str]]:
    def wrapped() -> list[str]:
        # Not sure why it doesnt see the attr
        cache_key = f"{m.table_name}:CHARACTERS:ALL"
        if r := cache.get_list(cache_key):
            return r

        res = list(m)
        tasks.add_task(cache.set_list, cache_key, res)
        return res

    return wrapped


def get_moves(
    m: CargoFetcher, tasks: BackgroundTasks
) -> Callable[[str, Optional[str]], list[Move] | JSONResponse]:
    def wrapped(
        character: str, move: Optional[str] = None
    ) -> list[Move] | JSONResponse:
        if move is not None:
            cache_key = f"{m.table_name}:CHARACTERS:{character}:{move}"
            if r := cache.get_model(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves_by_input(character, move)
        else:
            cache_key = f"{m.table_name}:CHARACTERS:{character}:ALL"
            if r := cache.get_model(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves(character)
        tasks.add_task(cache.set_model, cache_key, moves)
        return moves

    return wrapped


@app.get("/BBCF/characters/", response_model=List[str])
def get_characters_bbcf(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(BBCF, background_tasks)()


@app.get("/BBCF/characters/{character}/", response_model=List[BBCF.move])  # type: ignore
def get_move_bbcf(
    background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(BBCF, background_tasks)(character, move)


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
def get_move_p4u2r(
    character: str, background_tasks: BackgroundTasks, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(P4U2R, background_tasks)(character, move)


@app.get("/P4U2R/characters/", response_model=List[str])
def get_characters_p4u2r(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(P4U2R, background_tasks)()


@app.get("/HNK/characters/", response_model=List[str])
def get_characters_hnk(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(HNK, background_tasks)()


@app.get("/HNK/characters/{character}/", response_model=List[HNK.move])  # type: ignore
def get_move_hnk(
    character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    if move is not None:
        return HNK.get_moves_by_input(character, move)
    return HNK.get_moves(character)


@app.get("/GGACR/characters/", response_model=List[str])
def get_characters_ggacr(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(GGACR, background_tasks)()


@app.get("/GGACR/characters/{character}/", response_model=List[GGACR.move])  # type: ignore
def get_move_ggacr(
    background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(GGACR, background_tasks)(character, move)


@app.get("/MBTL/characters/", response_model=List[str])
def get_characters_mbtl(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(MBTL, background_tasks)()


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
def get_move_mbtl(
    background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(MBTL, background_tasks)(character, move)


# @app.get("/SCVI/characters/", response_model=List[str])
# def get_characters_scvi(background_tasks: BackgroundTasks) -> List[str]:
#     return get_characters(SCVI, background_tasks)()


# @app.get("/SCVI/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
# def get_move_scvi(
#     background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
# ) -> list[Move] | JSONResponse:
#     return get_moves(SCVI, background_tasks)(character, move)


@app.get("/SF6/characters/", response_model=List[str])
def get_characters_sf6(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SF6, background_tasks)()


@app.get("/SF6/characters/{character}/", response_model=List[SF6.move])  # type: ignore
def get_move_sf6(
    background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(SF6, background_tasks)(character, move)


@app.get("/KOFXV/characters/", response_model=List[str])
def get_characters_kofxv(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(KOFXV, background_tasks)()


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
def get_move_kofxv(
    background_tasks: BackgroundTasks, character: str, move: Optional[str] = None
) -> list[Move] | JSONResponse:
    return get_moves(KOFXV, background_tasks)(character, move)
