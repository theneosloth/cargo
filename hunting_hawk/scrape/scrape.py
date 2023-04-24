"""Scrape wikipedia for type definitons of a cargo table."""
from dataclasses import field, make_dataclass
from typing import Any, Generator, NewType, Optional, cast

import requests
import logging
from bs4 import BeautifulSoup
from pydantic.dataclasses import DataclassProxy, dataclass

from hunting_hawk.mediawiki.cargo import CargoClient, CargoNetworkError, CargoParseError

"""Web scraping functions."""

Move = NewType("Move", type)


class File(str):
    @classmethod
    def __get_validators__(cls) -> Generator[Any, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v) -> None:  # type: ignore
        if not isinstance(v, str):
            raise TypeError("Not a string value")
        return v  # type: ignore


def name_to_type(name: str) -> type:
    """Match a name to a type."""
    # TODO: Refactor into a more generic method
    normalized_name = name.lower().strip(",").split()
    match normalized_name:
        case ["integer"]:
            return int
        case ["file"]:
            return File
        case ["string" | "wikitext", *_]:
            return str
        case ["list", "of", t, *_]:
            # Mypy does not handle dynamic type names
            return cast(type, list[name_to_type(t)])  # type: ignore
        case default:
            raise CargoParseError(f'Unknown type: "{default}"')


def parse_cargo_table(cargo: CargoClient, table_name: str) -> DataclassProxy:
    """Dynamically construct a type for a cargo table with TABLE_NAME."""
    tables_endpoint = cargo.tables_endpoint()

    table_url = f"{tables_endpoint}/{table_name}"
    logging.info(f"Attempting to scrape {table_url}")
    try:
        req = requests.get(table_url, headers=cargo.headers, timeout=cargo.timeout)
    except requests.exceptions.HTTPError as e:
        raise CargoNetworkError from e
    except requests.exceptions.ReadTimeout as e:
        raise CargoNetworkError from e

    req.raise_for_status()

    data = req.content

    soup = BeautifulSoup(data, features="html.parser")

    table = soup.select_one("#mw-content-text > ul")

    if not table:
        # TODO: Refactor into a generic class
        table = soup.select_one("#mw-content-text > ol")
        if not table:
            raise CargoNetworkError(f"Could not find table. at {table_url}")

    field_names = [
        [t.strip() for t in tag.text.split("-")] for tag in table.find_all("li")
    ]

    fields = [
        (f[0], Optional[name_to_type(f[1])], field(default=None)) for f in field_names
    ]

    result = make_dataclass(
        table_name,
        # Mypy does not handle dynamic type names
        fields,  # type: ignore
        frozen=True,
    )

    proxy = dataclass(result)
    match proxy:
        case DataclassProxy():
            return proxy
        case default:
            raise CargoParseError(
                f"Failed to construct a data class proxy for {table_url}. Got {default}"
            )
