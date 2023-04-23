"""REST web service for retreiving frame data"""

import os
from typing import List, Optional, Callable
from .cache import FallbackCache
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from hunting_hawk.scrape.scrape import Move
from hunting_hawk.sites.fetcher import MoveDataFetcher
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import BBCF, GGACR, HNK, P4U2R
from hunting_hawk.sites.mizuumi import MBTL
from hunting_hawk.sites.supercombo import SCVI, SF6

app = FastAPI()
cache = FallbackCache()


def get_characters(
    m: MoveDataFetcher, tasks: BackgroundTasks
) -> Callable[[], list[str]]:
    def wrapped() -> list[str]:
        # Not sure why it doesnt see the attr
        cache_key = f"{m.table_name}:CHARACTERS:ALL"  # type: ignore
        if r := cache.get_list(cache_key):
            if len(r) > 0:
                return r

        res = list(m)
        tasks.add_task(cache.set_list, cache_key, res)
        return res

    return wrapped


def get_moves(m: MoveDataFetcher) -> Callable[[str, Optional[str]], list[Move]]:
    def wrapped(character: str, move: Optional[str] = None) -> list[Move]:
        if move is not None:
            return m.get_moves_by_input(character, move)
        return m.get_moves(character)

    return wrapped


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
def get_move_p4u2r(character: str, move: Optional[str] = None) -> list[Move]:
    return get_moves(P4U2R)(character, move)


@app.get("/P4U2R/characters/", response_model=List[str])
def get_characters_p4u2r(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(P4U2R, background_tasks)()


@app.get("/HNK/characters/", response_model=List[str])
def get_characters_hnk(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(HNK, background_tasks)()


@app.get("/HNK/characters/{character}/", response_model=List[HNK.move])  # type: ignore
def get_move_hnk(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return HNK.get_moves_by_input(character, move)
    return HNK.get_moves(character)


@app.get("/GGACR/characters/", response_model=List[str])
def get_characters_ggacr(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(GGACR, background_tasks)()


@app.get("/GGACR/characters/{character}/", response_model=List[GGACR.move])  # type: ignore
def get_move_ggacr(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return GGACR.get_moves_by_input(character, move)
    return GGACR.get_moves(character)


@app.get("/MBTL/characters/", response_model=List[str])
def get_characters_mbtl(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(MBTL, background_tasks)()


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
def get_move_mbtl(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return MBTL.get_moves_by_input(character, move)
    return MBTL.get_moves(character)


@app.get("/SCVI/characters/", response_model=List[str])
def get_characters_scvi(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SCVI, background_tasks)()


@app.get("/SCVI/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
def get_move_scvi(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return SCVI.get_moves_by_input(character, move)
    return SCVI.get_moves(character)


@app.get("/SF6/characters/", response_model=List[str])
def get_characters_sf6(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SF6, background_tasks)()


@app.get("/SF6/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
def get_move_sf6(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return SF6.get_moves_by_input(character, move)
    return SF6.get_moves(character)


@app.get("/KOFXV/characters/", response_model=List[str])
def get_characters_kofxv(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(KOFXV, background_tasks)()


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
def get_move_kofxv(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return KOFXV.get_moves_by_input(character, move)
    return KOFXV.get_moves(character)


@app.get("/BBCF/characters/", response_model=List[str])
def get_characters_bbcf(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(BBCF, background_tasks)()


@app.get("/BBCF/characters/{character}/", response_model=List[BBCF.move])  # type: ignore
def get_move_bbcf(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return BBCF.get_moves_by_input(character, move)
    return BBCF.get_moves(character)


def start() -> None:
    port = int(os.getenv("HUNTING_HAWK_PORT", "8080"))
    uvicorn.run("hunting_hawk.web.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    start()
