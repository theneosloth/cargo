"""REST web service for retreiving frame data"""

from typing import List

from fastapi import FastAPI

from hunting_hawk.cargo.scrape import Move
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import GGACR
from hunting_hawk.sites.mizuumi import UNICLR

app = FastAPI()


@app.get("/KOFXV/{character}/{move}", response_model=List[KOFXV.move])  # type: ignore
def get_move_kofxv(character: str, move: str) -> list[Move]:
    return KOFXV.get_moves_by_input(character, move)


@app.get("/KOFXV/{character}", response_model=List[KOFXV.move])  # type: ignore
def get_moves_kofxv(character: str) -> list[Move]:
    return KOFXV.get_moves(character)


@app.get("/GGACR/{character}/{move}", response_model=List[GGACR.move])  # type: ignore
def get_move_ggacr(character: str, move: str) -> list[Move]:
    return GGACR.get_moves_by_input(character, move)


@app.get("/GGACR/{character}", response_model=List[GGACR.move])  # type: ignore
def get_moves_ggacr(character: str) -> list[Move]:
    return GGACR.get_moves(character)


@app.get("/UNICLR/{character}/{move}", response_model=List[UNICLR.move])  # type: ignore
def get_move_uniclr(character: str, move: str) -> list[Move]:
    return UNICLR.get_moves_by_input(character, move)


@app.get("/UNICLR/{character}", response_model=List[UNICLR.move])  # type: ignore
def get_moves_uniclr(character: str) -> list[Move]:
    return UNICLR.get_moves(character)
