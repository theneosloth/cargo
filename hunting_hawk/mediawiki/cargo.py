"""Cargo wrapper."""
from dataclasses import dataclass, field
from typing import Any, List, TypedDict

from .client import Client, cached_get

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
