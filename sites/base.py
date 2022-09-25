"""Generic wrapper for a MediaWiki cargo page"""
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import List, Optional, TypeVar

from cargo.cargo import Cargo, CargoParameters, cargo_export
from cargo.scrape import Move, parse_cargo_table


class Fetcher(ABC):
    """An interface for fetchers."""

    @abstractmethod
    def __getitem__(self, query: str) -> List:
        """Accept a query and return a list of moves."""
        pass

    @abstractmethod
    def __contains__(self, query: str) -> bool:
        """Check if Q is in the collection."""
        pass


class CargoFetcher(Fetcher):
    """Fetcher more specific to Fighting game wikis."""

    cargo: Cargo
    table_name: str

    def __init__(
        self,
        domain: str,
        base_path: str,
        table_export_path: str,
        tables_path: str,
        table_name: str,
    ) -> None:
        """Init a cargo object and fetch move definition."""
        self.cargo = Cargo(domain, base_path, table_export_path, tables_path)
        self.table_name = table_name

        self._move: Optional[Move] = None

    def __getitem__(self, char: str) -> List[Move]:
        """Return the movelist for a character CHARA."""
        params: CargoParameters = {
            "where": f"chara='{char}'",
        }
        result = self.get(params)
        return result

    def __contains__(self, char: str) -> bool:
        """Check if a character exists."""
        params: CargoParameters = {
            "where": f"chara='{char}'",
        }
        result = self.get(params)
        return len(result) > 0

    @property
    def move(self) -> type:
        """Lazy load the cargo table definition."""
        if self._move is None:
            self._move = parse_cargo_table(self.cargo, self.table_name)
        return self._move

    def _list_to_moves(self, moves: list) -> List[Move]:
        """Copy all keys from res to Character."""
        res = []
        blank_fields = {t.name: None for t in fields(self.move)}

        for m in moves:
            filled_move = blank_fields | m
            move = self.move(**filled_move)
            res.append(move)

        return res

    def get(self, params: CargoParameters) -> List[Move]:
        """Wrap around cargo_export."""
        field_param = ",".join([f.name for f in fields(self.move)])

        merged_params: CargoParameters = {
            "fields": field_param,
            "tables": self.table_name,
        }

        result = cargo_export(self.cargo, merged_params | params)
        match result:
            case list():
                return self._list_to_moves(result)
            case _:
                raise TypeError("Endpoint expected to return list.")

    def get_moves(self, char: str, input: str) -> List[Move]:
        """Return the movelist for a character CHARA."""
        exact_params: CargoParameters = {
            "where": f'chara="{char}" AND input="{input}"',
        }
        result = self.get(exact_params)
        if result:
            return result

        fuzzy_params: CargoParameters = {
            "where": f'chara="{char}" AND input LIKE "%{input}%"',
        }
        return self.get(fuzzy_params)
