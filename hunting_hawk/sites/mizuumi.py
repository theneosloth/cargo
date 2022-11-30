"""A wrapper around dreamcancel.com cargo export endpoints."""

from functools import partial

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://wiki.gbl.gg"
WIKI_BASE_PATH = "/w"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"


init_fetcher = partial(
    CargoFetcher, WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH
)

__all__ = ["UNICLR", "MBTL"]

UNICLR = init_fetcher("UNICLR_MoveData")
MBTL = init_fetcher("MBTL_MoveData")
