"""A wrapper around dreamcancel.com cargo export endpoints."""
from .base import BaseFetcher
from functools import partial

WIKI_DOMAIN = "https://dustloop.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"
GGST_TABLE_NAME = "MoveData_GGST"

init_fetcher = partial(BaseFetcher, WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH)

GGST = lambda: init_fetcher("MoveData_GGST")

BBCF = lambda: init_fetcher("MoveData_BBCF")

GGACR = lambda: init_fetcher("MoveData_GGACR")

P4U2R = lambda: init_fetcher("MoveData_P4U2R")

HNK = lambda: init_fetcher("MoveData_HNK")
