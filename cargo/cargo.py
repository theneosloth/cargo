"""Cargo wrapper."""
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TypedDict

import requests

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
LRU_MAXSIZE = 128

CARGO_TABLES = [
    "MoveData_KOFXV",
]


# As documented here:
# https://discoursedb.org/w/api.php?action=help&modules=cargoquery
class CargoParameter(TypedDict, total=False):
    """A dict that only permits valid cargo parameters."""

    limit: int
    tables: str
    fields: str
    where: str
    join_on: str
    group_by: str
    having: str
    order_by: str
    offset: int


@dataclass
class Cargo:
    """Wrapper around the cargo query endpoint of a mediawiki site."""

    domain: str = WIKI_DOMAIN
    base_path: str = WIKI_BASE_PATH
    table_export_path: str = WIKI_TABLE_EXPORT_PATH


def index_endpoint(cargo: Cargo) -> str:
    """Construct a mediawiki API endpoint for a given mediawiki site."""
    return f"{cargo.domain}{cargo.base_path}/index.php"


def api_endpoint(cargo: Cargo) -> str:
    """Construct a mediawiki API endpoint for a given mediawiki site."""
    return f"{cargo.domain}{cargo.base_path}/api.php"


def export_endpoint(cargo: Cargo) -> str:
    """Construct a cargo export endpoint for a given mediawiki site."""
    index = index_endpoint(cargo)
    return f"{index}{cargo.table_export_path}&format=json"


# @lru_cache(maxsize=LRU_MAXSIZE)
def cargo_export(cargo: Cargo, params: CargoParameter) -> dict:
    """Call the export point."""
    export = export_endpoint(cargo)
    r = requests.get(export, params)
    return r.json()

valid_fields = ["chara", "moveId", "orderId", "input","name", "header", "version", "images", "hitboxes", "damage", "guard", "cancel", "startup", "active", "recovery", "hitadv", "blockadv", "invul", "stun", "guardDamage"]

field_param = ",".join(valid_fields)

cargo = Cargo()
c = cargo_export(cargo, {"tables": "MoveData_KOFXV", "fields": field_param})
print(c)
