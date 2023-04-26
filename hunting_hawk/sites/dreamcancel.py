"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.mediawiki.cargo import CargoClient

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_INDEX_PATH = "/wiki"
WIKI_API_PATH = "/w/api.php"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

cargo = CargoClient(
    WIKI_DOMAIN,
    WIKI_INDEX_PATH,
    WIKI_API_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
)

__all__ = ["KOFXV"]

KOFXV = CargoFetcher(cargo, "MoveData_KOFXV")
# KOF02UM = CargoFetcher(cargo, "MoveData_KOF02UM")
# SSVI = CargoFetcher(cargo, "MoveData_SSVI")
