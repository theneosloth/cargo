"""Generic wrapper for a MediaWiki cargo page."""
import logging
from abc import abstractmethod
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields
from functools import cached_property
from html import unescape
from typing import Any, Iterator, Optional

from pydantic.dataclasses import DataclassProxy

from hunting_hawk.mediawiki.cargo import (CargoClient, CargoParameters, File, Move,
                                          Wikitext, cargo_export, parse_cargo_table)
from hunting_hawk.mediawiki.client import ClientError
from hunting_hawk.mediawiki.filepath import get_file_path
from hunting_hawk.mediawiki.scrape.scrape import \
    parse_cargo_table as fallback_parse_table
from hunting_hawk.util.normalize import fuzzy_string, reverse_notation

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
        logging.info(f"Retrieving table definition for {self.table_name}")
        try:
            return parse_cargo_table(self.client, self.table_name)
        except ClientError as e:
            logging.info(
                f"Table parse failed with:{e} . Falling back to an HTML parser."
            )
            return fallback_parse_table(self.client, self.table_name)

    # TODO: Use type annotations
    def _convert_url(self, val: list[str] | str) -> list[str] | str:
        match val:
            case list():
                return [get_file_path(self.client, f) for f in val]
            case str():
                return get_file_path(self.client, val)

    def _unescape_html(self, val: list[Wikitext] | Wikitext) -> list[str] | str:
        match val:
            case list():
                # TODO: DEFINITELY NUKE THIS
                # Wiki returns &amp for incomplete codes
                return [unescape(unescape(link)) for link in val]
            case str():
                return unescape(val)

    def file_fields(self) -> list[str]:
        return [
            f.name
            for f in fields(self.move)
            if f.type == Optional[File] or f.type == Optional[list[File]]
        ]

    def wikitext_fields(self) -> list[str]:
        return [
            f.name
            for f in fields(self.move)
            if f.type == Optional[Wikitext] or f.type == Optional[list[Wikitext]]
        ]

    def _mutate_fields(self, flds: dict[Any, Any]) -> dict[Any, Any]:
        file_dicts = {
            k: self._convert_url(v) for k, v in flds.items() if k in self.file_fields()
        }

        unescaped_html = {
            k: self._unescape_html(v)
            for k, v in flds.items()
            if k in self.wikitext_fields()
        }

        return flds | unescaped_html | file_dicts

    def fill_move(self, move: dict[Any, Any]) -> Any:
        flds = fields(self.move)
        blank_fields = {t.name: None for t in flds}
        filled_move = blank_fields | self._mutate_fields(move)
        return self.move(**filled_move)

    def _list_to_moves(self, moves: list[Any]) -> list[Move]:
        """Copy all keys from res to Character."""
        with ThreadPoolExecutor(max_workers=5) as executor:
            res = executor.map(self.fill_move, moves)

        return list(res)

    def _get(self, params: CargoParameters, retrieve_images: bool) -> list[Move]:
        """Wrap around cargo_export."""

        file_fields = self.file_fields()
        field_param = [f.name for f in fields(self.move) if f.name not in file_fields]

        if retrieve_images:
            field_param = field_param + file_fields

        merged_params: CargoParameters = {
            "fields": ",".join(field_param),
            "tables": self.table_name,
        }
        result = cargo_export(self.client, merged_params | params)
        return self._list_to_moves(result)

    def get_moves(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""

        params: CargoParameters = {"where": f"chara='{char}'"}
        return self._get(params, True)

    def get_moves_by_input(self, char: str, input: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        exact_params: CargoParameters = {
            "where": f'{self.default_key}="{char}" AND input="{input}"',
        }
        result = self._get(exact_params, True)
        if result:
            return result

        fuzzy_params: CargoParameters = {
            "where": (
                f'({self.default_key}="{char}"'
                f' AND input LIKE "{fuzzy_string(input)}")'
                f' OR ({self.default_key}="{char}"'
                f' AND input LIKE "{fuzzy_string(reverse_notation(input))}")'
            )
        }

        return self._get(fuzzy_params, True)

    def query(self, char: str, query: CargoParameters) -> list[Move]:
        return self._get(query, True)

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
        return (self._mutate_fields(c)[default_field] for c in data)

    def __len__(self) -> int:
        """Get the character count."""
        length_params: CargoParameters = {
            "group_by": "_pageName",
            "tables": self.table_name,
        }
        return len(cargo_export(self.client, length_params))
