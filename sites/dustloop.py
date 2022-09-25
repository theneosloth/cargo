"""A wrapper around dreamcancel.com cargo export endpoints."""
from functools import partial

from .base import CargoFetcher

WIKI_DOMAIN = "https://dustloop.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

init_fetcher = partial(
    CargoFetcher, WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH
)

GGST = init_fetcher("MoveData_GGST")

BBCF = init_fetcher("MoveData_BBCF")

GGACR = init_fetcher("MoveData_GGACR")

P4U2R = init_fetcher("MoveData_P4U2R")

HNK = init_fetcher("MoveData_HNK")
