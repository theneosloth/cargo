"""Cargo wrapper."""
from dataclasses import dataclass, field
from typing import Any, TypedDict, cast

import requests

from . import __version__

WIKI_DOMAIN = "https://dreamcancel.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
PARAMS_LIMIT_DEFAULT = 50


# As documented here:
# https://discoursedb.org/w/api.php?action=help&modules=cargoquery
class CargoParameters(TypedDict, total=False):
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


@dataclass(eq=True, frozen=True)
class Cargo:
    """Wrapper around the cargo query endpoint of a mediawiki site."""

    domain: str = WIKI_DOMAIN
    base_path: str = WIKI_BASE_PATH
    table_export_path: str = WIKI_TABLE_EXPORT_PATH
    headers: dict[str, str] = field(
        default_factory=lambda: {"User-Agent": f"cargo_export/{__version__}"}
    )

    def index_endpoint(self) -> str:
        """Construct a mediawiki API endpoint for a given mediawiki site."""
        return f"{self.domain}{self.base_path}/index.php"

    def api_endpoint(self) -> str:
        """Construct a mediawiki API endpoint for a given mediawiki site."""
        return f"{self.domain}{self.base_path}/api.php"

    def export_endpoint(self) -> str:
        """Construct a cargo export endpoint for a given mediawiki site."""
        return f"{self.index_endpoint()}{self.table_export_path}&format=json"


def cargo_export(cargo: Cargo, params: CargoParameters) -> Any:
    """Call the export point."""
    if "limit" not in params:
        params["limit"] = PARAMS_LIMIT_DEFAULT
    export = cargo.export_endpoint()
    # Requests types do not properly handle typed dicts
    r = requests.get(
        export, headers=cargo.headers, params=cast(dict[str, int | str], params)
    ).json()
    return r
