"""A wrapper around dreamcancel.com cargo export endpoints."""


from .fetcher import CargoFetcher
from typing import Iterator, Any
from hunting_hawk.mediawiki.cargo import (
    CargoClient,
    CargoParameters,
    Move,
    cargo_export,
)

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


class StripSuffixFetcher(CargoFetcher):
    """
    Add a suffix to every cargo request.
    Useful for websites where all the movelist table structures can be identified by a common suffix
    """

    valid_table_sufix: str = " movelist"

    def __init__(self, cargo: CargoClient, table_name: str, default_key: str) -> None:
        super().__init__(cargo, table_name, default_key)

    def _mutate_fields(self, flds: dict[Any, Any]) -> dict[Any, Any]:
        flds[self.default_key] = flds[self.default_key].removesuffix(self.valid_table_sufix)
        return super()._mutate_fields(flds)

    def get_moves(self, char: str) -> list[Move]:
        return super().get_moves(char + self.valid_table_sufix)

    def get_moves_by_input(self, char: str, input: str) -> list[Move]:
        return super().get_moves_by_input(char + self.valid_table_sufix, input)

    def __iter__(self) -> Iterator[Move]:
        iter_params: CargoParameters = {
            "group_by": self.default_key,
            "tables": self.table_name,
            "fields": self.default_key,
            "where": f"{self.table_name}.{self.default_key} LIKE '%{self.valid_table_sufix}'",
        }
        data = cargo_export(self.client, iter_params)
        return (self._mutate_fields(c)[self.default_key] for c in data)


T8 = StripSuffixFetcher(cargo, "Move", default_key="_pageName")
