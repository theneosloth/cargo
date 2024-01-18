"""REST web service for retreiving frame data"""
import logging
from json import loads
from typing import Annotated, Callable, List, Optional, Awaitable
from fastapi import BackgroundTasks, FastAPI, Query, HTTPException, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic.json import pydantic_encoder

from urllib.parse import quote
from hunting_hawk.util.oembed import parse_url, Photo
from hunting_hawk.cache.cache import FallbackCache
from hunting_hawk.cache.util import create_redis_index
from hunting_hawk.mediawiki.cargo import Move
from hunting_hawk.sites.dreamcancel import KOFXV
from hunting_hawk.sites.dustloop import BBCF, GBVSR, GGACR, HNK, P4U2R
from hunting_hawk.sites.fetcher import CargoFetcher
from hunting_hawk.sites.mizuumi import MBTL
from hunting_hawk.sites.supercombo import SF6

# from hunting_hawk.sites.wavu import T8
from hunting_hawk.util import normalize

MAX_MOVE_LENGTH = 25

cache = FallbackCache()
app = FastAPI(
    title="HuntingHawk",
    servers=[
        {"url": "/", "description": "Huntinghawk"},
    ],
    docs_url="/",
)


@app.on_event("startup")
async def startup_event() -> None:
    logging.info("Initializing...")
    create_redis_index()


def populate_cache_for(character: str) -> None:
    raise NotImplementedError


def get_characters(m: CargoFetcher, tasks: BackgroundTasks) -> Callable[[], list[str]]:
    def wrapped() -> list[str]:
        cache_key = f"characterlist_{m.table_name}".lower()

        try:
            if r := cache.get_list(cache_key):
                return r
        except Exception as e:
            logging.error(f"Character cache lookup failed with {e}")

        res = list(m)
        tasks.add_task(cache.set_list, cache_key, res)
        return res

    return wrapped


def get_moves(m: CargoFetcher, tasks: BackgroundTasks) -> Callable[[str, Optional[str]], list[Move] | JSONResponse]:
    def wrapped(
        character: str,
        move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
    ) -> list[Move] | JSONResponse:
        if move is not None:
            normalized_move = normalize.normalize(move)
            cache_key = f"moves:{m.table_name}:{character}:{normalized_move}".lower()
            # If we have an exact key match return that first
            try:
                if r := cache.get_json(cache_key):
                    return JSONResponse(content=jsonable_encoder(r))
            except Exception as e:
                logging.error(f"Cache lookup failed with {e}")

            # Try to do a fuzzy query on our json
            try:
                if res := list(cache.query(character, move)):
                    # TODO: almost definitely a bottleneck
                    return JSONResponse(content=jsonable_encoder([loads(r) for r in res]))
            except Exception as e:
                logging.error(f"Cache query failed with {e}")
            moves = m.get_moves_by_input(character, normalized_move)
        else:
            cache_key = f"moves:{m.table_name}:{character}".lower()
            if r := cache.get_json(cache_key):
                return JSONResponse(content=jsonable_encoder(r))
            moves = m.get_moves(character)

            logging.info(f"Populating cache for {character}")
            for mo in moves:
                if hasattr(mo, "input"):
                    normalized = normalize.normalize(mo.input)
                    logging.debug(f"Storing {normalized} for {character}")
                    cache_key = f"moves:{m.table_name}:{character}:{normalized}".lower()
                    tasks.add_task(cache.set_json, cache_key, mo, pydantic_encoder)
                else:
                    logging.warn(f"Could not find input for {mo}")

        return moves

    return wrapped


@app.get("/BBCF/characters/", response_model=List[str])
def bbcf_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(BBCF, background_tasks)()


@app.get("/BBCF/characters/{character}/", response_model=List[BBCF.move])  # type: ignore
def bbcf_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(BBCF, background_tasks)(character, move)


@app.get("/P4U2R/characters/{character}/", response_model=List[P4U2R.move])  # type: ignore
def p4u2r_moves(
    character: str,
    background_tasks: BackgroundTasks,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
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
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
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
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(GGACR, background_tasks)(character, move)


@app.get("/MBTL/characters/", response_model=List[str])
def mbtl_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(MBTL, background_tasks)()


@app.get("/MBTL/characters/{character}/", response_model=List[MBTL.move])  # type: ignore
def mbtl_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(MBTL, background_tasks)(character, move)


@app.get("/SF6/characters/", response_model=List[str])
def sf6_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(SF6, background_tasks)()


@app.get("/SF6/characters/{character}/", response_model=List[SF6.move])  # type: ignore
def sf6_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(SF6, background_tasks)(character, move)


@app.get("/KOFXV/characters/", response_model=List[str])
def kofxv_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(KOFXV, background_tasks)()


@app.get("/KOFXV/characters/{character}/", response_model=List[KOFXV.move])  # type: ignore
def kofxv_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(KOFXV, background_tasks)(character, move)


@app.get("/GBVSR/characters/", response_model=List[str])
def gbvsr_characters(background_tasks: BackgroundTasks) -> List[str]:
    return get_characters(GBVSR, background_tasks)()


@app.get("/GBVSR/characters/{character}/", response_model=List[GBVSR.move])  # type: ignore
def gbvsr_moves(
    background_tasks: BackgroundTasks,
    character: str,
    move: Annotated[str | None, Query(max_length=MAX_MOVE_LENGTH)] = None,
) -> list[Move] | JSONResponse:
    return get_moves(GBVSR, background_tasks)(character, move)


# Here be dragons
# I need to make a live deploy to test this, so hacking together an awful implementation


def generate_oembed_for(game: str, character: str, move: str) -> Photo:
    fetcher = None
    match game.upper():
        case "GBVSR":
            fetcher = GBVSR
        case "BBCF":
            fetcher = BBCF
        case "GGACR":
            fetcher = GGACR
        case "KOFXV":
            fetcher = KOFXV
        case "SF6":
            fetcher = SF6
        case _:
            raise ValueError("Game not supported")
    moves = fetcher.get_moves_by_input(character, move)
    if len(moves) == 0:
        raise HTTPException(status_code=404)
    res = moves[0]
    image = "about:blank"

    if not (hasattr(res, "images")):
        raise ValueError("No images")

    match res.images:
        case str():
            image = res.images
        case [url, *_]:
            image = url
        case _:
            raise ValueError("Could not find an image")

    return Photo(
        width=200,
        height=200,
        url=image,
        author_name=character,
        title=move,
        provider_name="Huntinghawk",
        provider_url="https://huntinghawk.fly.dev/",
    )


@app.middleware("http")
async def add_oembed_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    url = f"{request.base_url}oembed?url={quote(str(request.url))}&format=json"
    response.headers[
        "Link"
    ] = f'<{url}>; rel="alternate"; type="application/json+oembed"; title="Huntinghawk frame data parser"'
    return response


@app.get("/oembed")
def generate_oembed(background_tasks: BackgroundTasks, format: str, url: str) -> Photo:
    if format != "json":
        raise HTTPException(status_code=501)
    requested_url = parse_url(url)

    if len(requested_url.parsed_url.parts) < 4:
        raise HTTPException(status_code=404)

    # ["/", "KOFXV", "characters", "Iori"]
    _, game, _, character, *_ = requested_url.parsed_url.parts

    if "move" not in requested_url.queries:
        raise HTTPException(status_code=503)

    move = requested_url.queries["move"][0]
    embed = generate_oembed_for(game, character, move)

    return embed
