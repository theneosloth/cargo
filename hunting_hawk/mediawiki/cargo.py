"""Cargo wrapper."""
from dataclasses import dataclass
from typing import Any, List, TypedDict

from .client import Client, ClientError, get

DEFAULT_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
DEFAULT_TABLES_PATH = "Special:CargoTables"
DEFAULT_PARAMS_LIMIT = 500

sql_query = str
cargo_query = str | List[str]


# As documented here:
# https://discoursedb.org/w/api.php?action=help&modules=cargoquery
class CargoParameters(TypedDict, total=False):
    """A dict that only permits valid cargo parameters."""

    limit: int
    tables: cargo_query
    fields: cargo_query
    where: cargo_query
    join_on: cargo_query
    group_by: cargo_query
    having: cargo_query
    order_by: cargo_query
    offset: int


@dataclass(eq=True, frozen=True)
class CargoClient(Client):
    """Wrapper around the cargo query endpoint of a mediawiki site."""

    table_export_path: str
    tables_path: str
    limit: int = 500

    def export_endpoint(self) -> str:
        """Construct a cargo export endpoint for a given mediawiki site."""
        return f"{self.index_endpoint()}{self.table_export_path}&format=json"

    def tables_endpoint(self) -> str:
        """Construct a cargo export endpoint for a given mediawiki site."""
        return f"{self.index_endpoint()}{self.tables_path}"


class CargoError(Exception):
    """Base class for cargo thrown exceptions."""

    pass


class CargoNetworkError(CargoError):
    """Exception class for cargo exceptions related to network failures."""


class CargoParseError(CargoError):
    """Exception class for cargo exceptions related to parsing Cargo tables."""


def cargo_export(cargo: CargoClient, params: CargoParameters) -> list[Any]:
    # TODO: Leaky Typing
    """Call the export point. Caches the URL."""
    req_params = {"limit": cargo.limit} | params

    try:
        res = get(cargo, cargo.export_endpoint(), req_params)
    except ClientError as e:
        raise CargoNetworkError from e

    match res:
        case list():
            return res
        case _:
            raise CargoParseError("Endpoint expected to return list.")
