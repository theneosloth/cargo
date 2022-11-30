"""Scrape wikipedia for type definitons of a cargo table."""
from dataclasses import field, make_dataclass
from typing import NewType, Optional, cast

import pydantic
from bs4 import BeautifulSoup
from requests import get

from .cargo import Cargo, CargoError

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
            return cast(type, list[name_to_type(t)])  # type: ignore
        case default:
            raise CargoError(f'Unknown type: "{default}"')


def parse_cargo_table(cargo: Cargo, table_name: str) -> Move:
    """Dynamically construct a type for a cargo table with TABLE_NAME."""
    tables_endpoint = cargo.tables_endpoint()

    table_url = f"{tables_endpoint}/{table_name}"
    req = get(table_url)

    req.raise_for_status()

    data = req.content

    soup = BeautifulSoup(data, features="html.parser")

    table = soup.select_one("#mw-content-text > ul")

    if not table:
        raise CargoError(f"Could not find table. at {table_url}")

    fields = [[t.strip() for t in tag.text.split("-")] for tag in table.find_all("li")]

    try:
        result = make_dataclass(
            table_name,
            [(f[0], Optional[name_to_type(f[1])], field(default=None)) for f in fields],
        )
    except CargoError as e:
        raise CargoError(f"Failed to construct types for {table_url}") from e

    return pydantic.dataclasses.dataclass(result)
