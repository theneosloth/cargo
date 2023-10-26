"""A wrapper around dreamcancel.com cargo export endpoints."""

from hunting_hawk.mediawiki.cargo import CargoClient

from .fetcher import CargoFetcher

WIKI_DOMAIN = "https://wavu.wiki"
WIKI_INDEX_PATH = "/"
WIKI_API_PATH = "/w/api.php"
WIKI_TABLE_EXPORT_PATH = "w/index.php?title=Special:CargoExport"
WIKI_TABLES_PATH = "t/Special:CargoTables"

cargo = CargoClient(
    WIKI_DOMAIN,
    WIKI_INDEX_PATH,
    WIKI_API_PATH,
    WIKI_TABLE_EXPORT_PATH,
    WIKI_TABLES_PATH,
)

__all__ = ["T8"]

T8 = CargoFetcher(cargo, "Move", default_key="_pageName")
