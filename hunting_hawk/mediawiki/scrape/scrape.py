"""Scrape wikipedia for type definitons of a cargo table."""
import logging
from dataclasses import field, make_dataclass
from io import StringIO
from typing import Optional, cast

import requests
from lxml import etree
from pydantic.dataclasses import DataclassProxy, dataclass

from hunting_hawk.mediawiki.cargo import (CargoClient, CargoNetworkError,
                                          CargoParseError, File, Wikitext)

"""Web scraping functions that do not call the mediawiki API."""


def name_to_type(name: str) -> type:
    """Match a name to a type."""
    # TODO: Refactor into a more generic method
    normalized_name = name.lower().strip(",").split()
    match normalized_name:
        case ["integer"]:
            return int
        case ["file"]:
            return File
        case ["string", *_]:
            return str
        case ["wikitext", *_]:
            return Wikitext
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

    data = req.content.decode("utf-8")

    parser = etree.HTMLParser()
    # Stub library is incorrect, HTML Parser is a valid argument
    tree = etree.parse(StringIO(data), parser)  # type: ignore

    # More issues with stubs
    (table,) = tree.xpath("//*[@id='mw-content-text']/*[self::ul or self::ol]")  # type: ignore

    if table is None or type(table) is not etree._Element:
        raise CargoNetworkError(f"Could not find table. at {table_url}")

    items = table.xpath("./li")

    if not items or type(items) is not list:
        raise CargoParseError(f"Could not find list items for list at {table_url}")

    field_names = [
        [t.strip() for t in "".join(tag.xpath(".//text()")).split("-")] for tag in items  # type: ignore
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
