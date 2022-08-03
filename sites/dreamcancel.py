"""A wrapper around dreamcancel.com cargo export endpoints."""

from .base import BaseFetcher

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

XV_TABLE_NAME = "MoveData_KOFXV"
KOFXV = BaseFetcher(
    WIKI_DOMAIN,
    WIKI_BASE_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
    XV_TABLE_NAME,
)
