"""Generic wrapper for a MediaWiki cargo page."""
from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import fields
from functools import cached_property
from typing import Any, Iterator, Optional

from pydantic.dataclasses import DataclassProxy

from hunting_hawk.mediawiki.cargo import CargoClient, CargoParameters, cargo_export
from hunting_hawk.mediawiki.filepath import get_file_path
from hunting_hawk.scrape.scrape import File, Move, parse_cargo_table

__all__ = ["CargoFetcher", "MoveDataFetcher"]


class MoveDataFetcher(Mapping[Any, Any]):
    """Interface for move fetchers."""

    @abstractmethod
    def get_moves_by_input(self, char: str, input: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        pass

    @abstractmethod
    def get_moves(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        pass

    @abstractmethod
    def query(self, char: str, query: CargoParameters) -> list[Move]:
        """Return the movelist for a character CHARA matching query QUERY."""
        pass


class CargoFetcher(MoveDataFetcher):
    """Fetcher more specific to Fighting game wikis."""

    client: CargoClient
    table_name: str

    def __init__(self, cargo: CargoClient, table_name: str) -> None:
        """Init a cargo object and fetch move definition."""
        self.client = cargo
        self.table_name = table_name
        self.default_key = "chara"

    @cached_property
    def move(self) -> DataclassProxy:
        """Lazy load the cargo table definition."""
        return parse_cargo_table(self.client, self.table_name)

    # TODO: Use type annotations
    def _convert_url(self, val: list[str] | str) -> list[str] | str:
        match val:
            case list():
                return [get_file_path(self.client, f) for f in val]
            case str():
                return get_file_path(self.client, val)

    # TODO: Use type annotations here instead of a hardcoded list
    def _mutate_fields(self, flds: dict[Any, Any]) -> dict[Any, Any]:
        file_fields = [
            f.name
            for f in fields(self.move)
            if f.type == Optional[File] or f.type == Optional[list[File]]
        ]

        file_dicts = {
            k: self._convert_url(v) for k, v in flds.items() if k in file_fields
        }

        return flds | file_dicts

    def _list_to_moves(self, moves: list[Any]) -> list[Move]:
        """Copy all keys from res to Character."""
        res = []
        flds = fields(self.move)

        blank_fields = {t.name: None for t in flds}
        for m in moves:
            filled_move = blank_fields | self._mutate_fields(m)
            move = self.move(**filled_move)
            res.append(move)

        return res

    def _get(self, params: CargoParameters) -> list[Move]:
        """Wrap around cargo_export."""
        # TODO: Prevent excessive API polling while we don't have a proper cache layer

        field_param = ",".join([f.name for f in fields(self.move) if f.type != File])

        merged_params: CargoParameters = {
            "fields": field_param,
            "tables": self.table_name,
        }

        result = cargo_export(self.client, merged_params | params)
        return self._list_to_moves(result)

    def get_moves(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        params: CargoParameters = {
            "where": f"chara='{char}'",
        }
        return self._get(params)

    def get_moves_by_input(self, char: str, input: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        exact_params: CargoParameters = {
            "where": f'{self.default_key}="{char}" AND input="{input}"',
        }
        result = self._get(exact_params)
        if result:
            return result

        fuzzy_params: CargoParameters = {
            "where": f'chara="{char}" AND input LIKE "%{input}%"',
        }
        return self._get(fuzzy_params)

    def query(self, char: str, query: CargoParameters) -> list[Move]:
        return self._get(query)

    def __getitem__(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        return self.get_moves(char)

    def __iter__(self, default_field: str = "chara") -> Iterator[Move]:
        """Iterate over all characters."""
        iter_params: CargoParameters = {
            "group_by": default_field,
            "tables": self.table_name,
            "fields": default_field,
        }
        data = cargo_export(self.client, iter_params)
        return (c[default_field] for c in data)

    def __len__(self) -> int:
        """Get the character count."""
        length_params: CargoParameters = {
            "group_by": "_pageName",
            "tables": self.table_name,
        }
        return len(cargo_export(self.client, length_params))
