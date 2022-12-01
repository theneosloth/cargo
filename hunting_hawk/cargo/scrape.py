"""Scrape wikipedia for type definitons of a cargo table."""
from dataclasses import field, make_dataclass
from typing import NewType, Optional, Type, cast

import requests
from bs4 import BeautifulSoup
from pydantic.dataclasses import DataclassProxy, dataclass

from .cargo import DEFAULT_TIMEOUT, Cargo, CargoNetworkError, CargoParseError

"""Web scraping functions."""

Move = NewType("Move", type)


def name_to_type(name: str) -> type:
    """Match a name to a type."""
    match name.lower().split():
        case ["integer"]:
            return int
        case ["file"]:
            # Could add a special type later
            return str
        case ["string" | "wikitext", *_]:
            return str
        case ["list", "of", t, *_]:
            # Mypy does not handle dynamic type names
            return cast(type, list[name_to_type(t)])  # type: ignore
        case default:
            raise CargoParseError(f'Unknown type: "{default}"')


def parse_cargo_table(cargo: Cargo, table_name: str) -> DataclassProxy:
    """Dynamically construct a type for a cargo table with TABLE_NAME."""
    tables_endpoint = cargo.tables_endpoint()

    table_url = f"{tables_endpoint}/{table_name}"
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
        raise CargoNetworkError(f"Could not find table. at {table_url}")

    fields = [[t.strip() for t in tag.text.split("-")] for tag in table.find_all("li")]

    result = make_dataclass(
        table_name,
        # Mypy does not handle dynamic type names
        [(f[0], Optional[name_to_type(f[1])], field(default=None)) for f in fields],  # type: ignore
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
