"""REST web service for retreiving frame data"""

import os
from typing import List, Optional

import uvicorn
from fastapi import FastAPI

from hunting_hawk.scrape.scrape import Move
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import BBCF, GGACR, HNK, P4U2R
from hunting_hawk.sites.mizuumi import MBTL
from hunting_hawk.sites.supercombo import SCVI, SF6

app = FastAPI()


@app.get("/P4U2R/characters/", response_model=List[str])
def get_characters_p4u2r() -> List[str]:
    return list(P4U2R)


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
def get_move_p4u2r(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return P4U2R.get_moves_by_input(character, move)
    return P4U2R.get_moves(character)


@app.get("/HNK/characters/", response_model=List[str])
def get_characters_hnk() -> List[str]:
    return list(HNK)


@app.get("/HNK/characters/{character}/", response_model=List[HNK.move])  # type: ignore
def get_move_hnk(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return HNK.get_moves_by_input(character, move)
    return HNK.get_moves(character)


@app.get("/GGACR/characters/", response_model=List[str])
def get_characters_ggacr() -> List[str]:
    return list(GGACR)


@app.get("/GGACR/characters/{character}/", response_model=List[GGACR.move])  # type: ignore
def get_move_ggacr(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return GGACR.get_moves_by_input(character, move)
    return GGACR.get_moves(character)


@app.get("/MBTL/characters/", response_model=List[str])
def get_characters_mbtl() -> List[str]:
    return list(MBTL)


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
def get_move_mbtl(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return MBTL.get_moves_by_input(character, move)
    return MBTL.get_moves(character)


@app.get("/SCVI/characters/", response_model=List[str])
def get_characters_scvi() -> List[str]:
    return list(SCVI)


@app.get("/SCVI/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
def get_move_scvi(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return SCVI.get_moves_by_input(character, move)
    return SCVI.get_moves(character)


@app.get("/SF6/characters/", response_model=List[str])
def get_characters_sf6() -> List[str]:
    return list(SF6)


@app.get("/SF6/characters/{character}/", response_model=List[SCVI.move])  # type: ignore
def get_move_sf6(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return SF6.get_moves_by_input(character, move)
    return SF6.get_moves(character)


@app.get("/KOFXV/characters/", response_model=List[str])
def get_characters_kofxv() -> List[str]:
    return list(KOFXV)


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
def get_move_kofxv(character: str, move: Optional[str] = None) -> list[Move]:
    if move is not None:
        return KOFXV.get_moves_by_input(character, move)
    return KOFXV.get_moves(character)


@app.get("/BBCF/characters/", response_model=List[str])
def get_characters_bbcf() -> List[str]:
    return list(BBCF)


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
