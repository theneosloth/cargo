"""Generic wrapper for a MediaWiki cargo page."""
import logging
import re
import xml.etree.ElementTree as ET
from abc import abstractmethod
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import fields
from functools import cached_property
from html import unescape
from typing import Any, Iterator, Optional

from pydantic.dataclasses import DataclassProxy

from hunting_hawk.mediawiki.cargo import (
    CargoClient,
    CargoParameters,
    File,
    Move,
    Wikitext,
    cargo_export,
    parse_cargo_table,
)
from hunting_hawk.mediawiki.client import ClientError
from hunting_hawk.mediawiki.filepath import get_file_path
from hunting_hawk.mediawiki.scrape.scrape import (
    parse_cargo_table as fallback_parse_table,
)
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
    def query(self, query: CargoParameters) -> list[Move]:
        """Return the movelist for a character CHARA matching query QUERY."""
        pass


class CargoFetcher(MoveDataFetcher):
    """Fetcher more specific to Fighting game wikis."""

    client: CargoClient
    table_name: str

    def __init__(self, cargo: CargoClient, table_name: str, default_key: str = "chara") -> None:
        """Init a cargo object and fetch move definition."""
        self.client = cargo
        self.table_name = table_name
        self.default_key = f"{table_name}.{default_key}"

    @cached_property
    def move(self) -> DataclassProxy:
        """Lazy load the cargo table definition."""
        logging.info(f"Retrieving table definition for {self.table_name}")
        try:
            return parse_cargo_table(self.client, self.table_name)
        except ClientError as e:
            logging.info(f"Table parse failed with:{e} . Falling back to an HTML parser.")
            return fallback_parse_table(self.client, self.table_name)

    # TODO: Use type annotations
    def _convert_url(self, val: list[str] | str) -> list[str] | str:
        match val:
            case list():
                return [get_file_path(self.client, f) for f in val]
            case str():
                return get_file_path(self.client, val)

    # TODO:
    # Send this to the abyss
    def _parse_wikitext(self, val: Wikitext) -> str:
        """Attempt to get the text value of a wikitext tag."""
        wikit = unescape(unescape(val))
        try:
            inner = ET.fromstring(wikit).text
            if not inner:
                return wikit
            return re.sub("^'''|'''$", "", inner)
        except ET.ParseError:
            pass
        return wikit

    def _unescape_html(self, val: list[Wikitext] | Wikitext) -> list[str] | str:
        match val:
            case list():
                # TODO: DEFINITELY NUKE THIS
                # Wiki returns &amp for incomplete codes
                return [unescape(unescape(link)) for link in val if unescape(unescape(link)).strip()]
            case str():
                return self._parse_wikitext(val)
            case int() | float():
                # logging.warning(
                #     f"Wikitext value {val} is not a string. Attempting to convert"
                # )
                return str(val)

    def file_fields(self) -> list[str]:
        return [
            f.name
            for f in fields(self.move)  # type: ignore
            # Some wikis do not annotate the images as hitboxes
            if f.type == Optional[File] or f.type == Optional[list[File]] or f.name in ("images", "hitboxes")
        ]

    def wikitext_fields(self) -> list[str]:
        return [f.name for f in fields(self.move) if f.type == Optional[Wikitext] or f.type == Optional[list[Wikitext]]]  # type: ignore

    def _mutate_fields(self, flds: dict[Any, Any]) -> dict[Any, Any]:
        file_dicts = {k: self._convert_url(v) for k, v in flds.items() if k in self.file_fields()}
        unescaped_html = {k: self._unescape_html(v) for k, v in flds.items() if k in self.wikitext_fields()}

        return flds | unescaped_html | file_dicts

    def fill_move(self, move: dict[Any, Any]) -> Any:
        flds = fields(self.move)  # type: ignore
        blank_fields = {t.name: None for t in flds}
        filled_move = blank_fields | self._mutate_fields(move)
        return self.move(**filled_move)

    def _list_to_moves(self, moves: list[Any]) -> list[Move]:
        """Copy all keys from res to Character."""

        res = []
        with ThreadPoolExecutor() as executor:
            futures = (executor.submit(self.fill_move, move) for move in moves)
            done = as_completed(futures)
            for future in done:
                try:
                    mv = future.result()
                    res.append(mv)
                except Exception as e:
                    logging.warning(f"Move retrieval failed with {e}. Skipping move")

        return res

    def _get(self, params: CargoParameters) -> list[Move]:
        """Wrap around cargo_export."""

        field_param = [f.name for f in fields(self.move)] + [self.default_key]  # type: ignore

        merged_params: CargoParameters = {
            "fields": ",".join(field_param),
            "tables": self.table_name,
        }
        result = cargo_export(self.client, merged_params | params)
        return self._list_to_moves(result)

    def get_moves(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""

        params: CargoParameters = {"where": f"{self.default_key}='{char}'"}
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
            "where": (
                f"({self.default_key}='{char}'"
                f" AND input LIKE '{fuzzy_string(input)}')"
                f" OR ({self.default_key}='{char}'"
                f" AND input LIKE '{fuzzy_string(reverse_notation(input))}')"
                f" OR (name LIKE '{fuzzy_string(input)}')"
            )
        }

        return self._get(fuzzy_params)

    def query(self, query: CargoParameters) -> list[Move]:
        return self._get(query)

    def __getitem__(self, char: str) -> list[Move]:
        """Return the movelist for a character CHARA."""
        return self.get_moves(char)

    def __iter__(self) -> Iterator[Move]:
        """Iterate over all characters."""
        iter_params: CargoParameters = {
            "group_by": self.default_key,
            "tables": self.table_name,
            "fields": self.default_key,
        }
        data = cargo_export(self.client, iter_params)
        return (self._mutate_fields(c)[self.default_key] for c in data)

    def __len__(self) -> int:
        """Get the character count."""
        length_params: CargoParameters = {
            "group_by": "_pageName",
            "tables": self.table_name,
        }
        return len(cargo_export(self.client, length_params))
