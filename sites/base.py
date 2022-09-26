"""Generic wrapper for a MediaWiki cargo page."""

from collections.abc import Mapping
from dataclasses import fields
from typing import Iterator, List, Optional

from cargo.cargo import Cargo, CargoParameters, cargo_export
from cargo.scrape import Move, parse_cargo_table


class CargoFetcher(Mapping):
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

    def _get(self, params: CargoParameters) -> List[Move]:
        """Wrap around cargo_export."""
        field_param = ",".join([f.name for f in fields(self.move)])

        merged_params: CargoParameters = {
            "fields": field_param,
            "tables": self.table_name,
        }

        result = cargo_export(self.cargo, merged_params | params)
        return self._list_to_moves(result)

    def get_moves(self, char: str, input: str) -> List[Move]:
        """Return the movelist for a character CHARA."""
        exact_params: CargoParameters = {
            "where": f'chara="{char}" AND input="{input}"',
        }
        result = self._get(exact_params)
        if result:
            return result

        fuzzy_params: CargoParameters = {
            "where": f'chara="{char}" AND input LIKE "%{input}%"',
        }
        return self._get(fuzzy_params)

    def __getitem__(self, char: str) -> List[Move]:
        """Return the movelist for a character CHARA."""
        params: CargoParameters = {
            "where": f"chara='{char}'",
        }
        result = self._get(params)
        return result

    def __iter__(self) -> Iterator[Move]:
        """Iterate over all characters."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Get the character count."""
        length_params: CargoParameters = {
            "group_by": "_pageName",
            "tables": self.table_name,
        }
        return len(cargo_export(self.cargo, length_params))
