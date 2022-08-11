from dataclasses import make_dataclass
from typing import Any, NewType, cast

from bs4 import BeautifulSoup
from requests import get

from .cargo import Cargo, CargoError

"""Web scraping functions."""

Move = NewType("Move", type)


def name_to_type(name: str) -> type:
    """Match a name to a type."""
    name_dict = {
        "list of": list[str],
        "string": str,
        "wikitext": str,
    }

    found = ""
    for n, _ in name_dict.items():
        if n in name.lower():
            found = n

    if found == "":
        raise CargoError(f'Unknown type: "{name}"')

    return name_dict[found]


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
