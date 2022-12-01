"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.cargo.cargo import Cargo

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://wiki.gbl.gg"
WIKI_BASE_PATH = "/w"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLES_PATH = "/Special:CargoTables"

cargo = Cargo(WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH)

__all__ = ["UNICLR", "MBTL"]

UNICLR = CargoFetcher(cargo, "UNICLR_MoveData")
MBTL = CargoFetcher(cargo, "MBTL_MoveData")
