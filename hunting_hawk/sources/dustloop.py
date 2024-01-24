"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.mediawiki.cargo import CargoClient

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://dustloop.com"
WIKI_INDEX_PATH = "/wiki/index.php"
WIKI_API_PATH = "/wiki/api.php"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

cargo = CargoClient(
    WIKI_DOMAIN,
    WIKI_INDEX_PATH,
    WIKI_API_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
)

__all__ = ["GGST", "BBCF", "GGACR", "P4U2R", "HNK"]

GGST = CargoFetcher(cargo, "MoveData_GGST")

BBCF = CargoFetcher(cargo, "MoveData_BBCF")

GGACR = CargoFetcher(cargo, "MoveData_GGACR")

P4U2R = CargoFetcher(cargo, "MoveData_P4U2R")

HNK = CargoFetcher(cargo, "MoveData_HNK")

GBVSR = CargoFetcher(cargo, "MoveData_GBVSR")
