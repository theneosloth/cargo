"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.cargo.cargo import Cargo

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

cargo = Cargo(WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH)

__all__ = ["KOFXV", "KOF02UM"]

KOFXV = CargoFetcher(cargo, "MoveData_KOFXV")
KOF02UM = CargoFetcher(cargo, "MoveData_KOF02UM")
