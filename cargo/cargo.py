"""Cargo wrapper."""
import json
from dataclasses import dataclass, field
from typing import Any, List, TypedDict, cast

import requests

from cargo.__version__ import VERSION
from cargo.cache import CargoCache

PARAMS_LIMIT_DEFAULT = 50

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
class Cargo:
    """Wrapper around the cargo query endpoint of a mediawiki site."""

    domain: str
    base_path: str
    table_export_path: str
    headers: dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the version header."""
        object.__setattr__(self, "headers", {"User-Agent": f"cargo_export/{VERSION}"})

    def index_endpoint(self) -> str:
        """Construct a mediawiki API endpoint for a given mediawiki site."""
        return f"{self.domain}{self.base_path}/index.php"

    def api_endpoint(self) -> str:
        """Construct a mediawiki API endpoint for a given mediawiki site."""
        return f"{self.domain}{self.base_path}/api.php"

    def export_endpoint(self) -> str:
        """Construct a cargo export endpoint for a given mediawiki site."""
        return f"{self.index_endpoint()}{self.table_export_path}&format=json"


class CargoError(Exception):
    """Base class for cargo thrown exceptions."""

    pass


def cargo_export(
    cargo: Cargo, params: CargoParameters, cache: CargoCache | None = None
) -> Any | CargoError:
    """Call the export point."""
    req_params = params.copy()

    if "limit" not in req_params:
        req_params["limit"] = PARAMS_LIMIT_DEFAULT

    export = cargo.export_endpoint()

    req = requests.Request(export, headers=cargo.headers, params=cast(dict, req_params))
    prepped = req.prepare()
    s = requests.Session()
    url = prepped.url

    if url is None:
        raise CargoError("Failed to construct url.")

    if cache is not None:
        cached = cache.get(url)
        if cached:
            return json.loads(cached)

    try:
        request = s.send(prepped)

        request.raise_for_status()

    except requests.exceptions.JSONDecodeError as e:
        raise CargoError from e

    except requests.exceptions.HTTPError as e:
        raise CargoError from e

    res = request.json()
    if "error" in res:
        raise CargoError(res["error"])

    if cache is not None:
        cache.set(
            url,
            request.content,
        )
    import pdb

    pdb.set_trace()

    return res
