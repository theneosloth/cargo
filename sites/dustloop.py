"""A wrapper around dreamcancel.com cargo export endpoints."""
from .base import BaseFetcher

WIKI_DOMAIN = "https://dustloop.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"
GGST_TABLE_NAME = "MoveData_GGST"

GGST = BaseFetcher(
    WIKI_DOMAIN,
    WIKI_BASE_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
    GGST_TABLE_NAME,
)


BBCF_TABLE_NAME = "MoveData_BBCF"

BBCF = BaseFetcher(
    WIKI_DOMAIN,
    WIKI_BASE_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
    BBCF_TABLE_NAME,
)
