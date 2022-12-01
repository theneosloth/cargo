"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.cargo.cargo import Cargo

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://dustloop.com"
WIKI_BASE_PATH = "/wiki/index.php"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

cargo = Cargo(WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH)

__all__ = ["GGST", "BBCF", "GGACR", "P4U2R", "HNK"]

GGST = CargoFetcher(cargo, "MoveData_GGST")

BBCF = CargoFetcher(cargo, "MoveData_BBCF")

GGACR = CargoFetcher(cargo, "MoveData_GGACR")

P4U2R = CargoFetcher(cargo, "MoveData_P4U2R")

HNK = CargoFetcher(cargo, "MoveData_HNK")
