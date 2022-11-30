"""A wrapper around dreamcancel.com cargo export endpoints."""

from functools import partial

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"


init_fetcher = partial(
    CargoFetcher, WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH
)

__all__ = ["KOFXV", "KOF02UM"]

KOFXV = init_fetcher("MoveData_KOFXV")
KOF02UM = init_fetcher("MoveData_KOF02UM")
