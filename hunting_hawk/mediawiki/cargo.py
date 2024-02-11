"""Cargo wrapper."""
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Generator, List, Literal, NewType, Optional, TypedDict

from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import DataclassProxy
from pydantic.dataclasses import dataclass as pydantic_dataclass

from .client import Client, ClientError, cached_get, get

DEFAULT_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
DEFAULT_TABLES_PATH = "Special:CargoTables"
DEFAULT_PARAMS_LIMIT = 200

cargo_query = str | List[str]
Move = NewType("Move", type)
FieldType = Literal[
    "Page",
    "String",
    "Text",
    "Integer",
    "Float",
    "Date",
    "Start date",
    "End date",
    "Start datetime",
    "End datetime",
    "Datetime",
    "Boolean",
    "Coordinates",
    "Wikitext string",
    "Wikitext",
    "Searchtext",
    "File",
    "URL",
    "Email",
    "Rating",
]


class CargoField(BaseModel):
    type: FieldType
    isList: Optional[str]
    delimiter: Optional[str]


class CargoFields(BaseModel):
    cargofields: dict[str, CargoField]


class File(str):
    """A mediawiki Image link type"""

    @classmethod
    def __get_validators__(cls) -> Generator[Any, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v) -> None:  # type: ignore
        if not isinstance(v, str):
            raise TypeError("Not a string value")
        return v  # type: ignore


class Wikitext(str):
    """A mediawiki Wikitext link type"""

    @classmethod
    def __get_validators__(cls) -> Generator[Any, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v) -> None:  # type: ignore
        if not isinstance(v, str):
            raise TypeError("Not a string value")
        return v  # type: ignore


# As documented here:
# /w/api.php?action=help&modules=cargofields
class CargoFieldsParams(BaseModel):
    """A dict that only permits imageinfo parameters."""

    table: str
    action: str = "cargofields"
    format: str = "json"


def to_type(field: CargoField) -> type:
    """Match a name to a type."""

    field_types: dict[FieldType, type] = {
        "Integer": int,
        "Float": float,
        "Boolean": bool,
        "File": File,
        "Wikitext": Wikitext,
        "Wikitext string": Wikitext,
        "String": str,
    }

    if field.type not in field_types:
        raise CargoParseError(f"Unhandled type encountered: '{field}'")

    match field:
        case CargoField(isList=None):
            return field_types[field.type]
        case CargoField(isList=""):
            return list[field_types[field.type]]  # type: ignore

        case default:
            raise CargoParseError(f"Unhandled field encountered: '{default}'")


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
    limit: int = 200

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


def parse_cargo_table(client: Client, table_name: str) -> DataclassProxy:
    """Dynamically construct a type for a cargo table with TABLE_NAME."""
    params = CargoFieldsParams(table=table_name).__dict__
    res = cached_get(client, client.api_endpoint(), params)
    try:
        c = CargoFields.parse_obj(res)

    except ValidationError as e:
        raise TypeError("Failed to unmarshal the model") from e

    fields = [(k, Optional[to_type(v)], field(default=None)) for k, v in c.cargofields.items()]
    result = make_dataclass(table_name, fields, frozen=True)  # type: ignore
    proxy = pydantic_dataclass(result)

    match proxy:
        case DataclassProxy():
            return proxy
        case default:
            raise CargoParseError(f"Failed to construct a data class proxy for {table_name}. Got {default}")


def cargo_export(cargo: CargoClient, params: CargoParameters) -> list[Any]:
    # TODO: Leaky Typing
    """Call the export point. Caches the URL."""
    req_params = params

    try:
        res = get(cargo, cargo.export_endpoint(), dict(req_params))
    except ClientError as e:
        raise CargoNetworkError from e

    match res:
        case list():
            return res
        case _:
            raise CargoParseError("Endpoint expected to return list.")
