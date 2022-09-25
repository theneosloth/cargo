"""Scrape wikipedia for type definitons of a cargo table."""
from dataclasses import make_dataclass
from typing import NewType, cast

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
        case ["list", "of", "integer"]:
            return list[int]
        case ["string" | "wikitext", *_]:
            return str
        case ["list", "of", *_]:
            return list[str]
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

    result = make_dataclass(
        table_name,
        [(f[0], name_to_type(f[1])) for f in fields],
    )
    return cast(Move, result)
