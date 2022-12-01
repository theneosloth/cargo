"""REST web service for retreiving frame data"""

from typing import List, Optional

from fastapi import FastAPI

from hunting_hawk.cargo.scrape import Move
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
