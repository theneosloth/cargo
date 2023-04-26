import os
from inspect import signature

import pytest

from .cargo import CargoClient, CargoField, File, Wikitext, parse_cargo_table, to_type

RUN_SMOKE = os.getenv("HUNTING_HAWK_SMOKE", False)

test_cargo = CargoClient(
    "https://example.com",
    "/wiki/superfluous",
    "/wiki/superfluous_api",
    "?title=Special:CargoExport",
    "/Special:CargoTables",
)


def test_init() -> None:
    match test_cargo.headers:
        case {"User-Agent": header_dict}:
            assert header_dict is not None
        case _:
            raise Exception(f"No user agent found in {test_cargo.headers}")


def test_endpoints() -> None:
    assert test_cargo.index_endpoint() == "https://example.com/wiki/superfluous"

    assert (
        test_cargo.export_endpoint()
        == "https://example.com/wiki/superfluous?title=Special:CargoExport&format=json"
    )

    assert (
        test_cargo.tables_endpoint()
        == "https://example.com/wiki/superfluous/Special:CargoTables"
    )


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_to_type() -> None:
    test_cases = [
        (CargoField(type="String"), str),
        (CargoField(type="Wikitext"), Wikitext),
        (CargoField(type="Wikitext string"), Wikitext),
        (CargoField(type="Integer"), int),
        (CargoField(type="Float"), float),
        (CargoField(type="Boolean"), bool),
        (CargoField(type="File"), File),
        (CargoField(type="String", isList=""), list[str]),
        (CargoField(type="Wikitext", isList=""), list[Wikitext]),
        (CargoField(type="Wikitext string", isList=""), list[Wikitext]),
        (CargoField(type="Integer", isList=""), list[int]),
        (CargoField(type="Float", isList=""), list[float]),
        (CargoField(type="Boolean", isList=""), list[bool]),
        (CargoField(type="File", isList=""), list[File]),
    ]

    for wiki_string, expected_type in test_cases:
        assert to_type(wiki_string) == expected_type


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_scrape_ggst() -> None:
    WIKI_DOMAIN = "https://dustloop.com"
    WIKI_BASE_PATH = "/wiki/index.php"
    WIKI_API_PATH = "/wiki/api.php"
    WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
    WIKI_TABLES_PATH = "/Special:CargoTables"
    WIKI_TABLE = "MoveData_GGST"

    dustloop = CargoClient(
        WIKI_DOMAIN,
        WIKI_BASE_PATH,
        WIKI_API_PATH,
        table_export_path=WIKI_TABLE_EXPORT_PATH,
        tables_path=WIKI_TABLES_PATH,
    )

    ggst_attributes = {"chara": str, "name": str, "prorate": str, "images": list[str]}

    table = parse_cargo_table(dustloop, WIKI_TABLE)
    assert parse_cargo_table(dustloop, WIKI_TABLE) is not None
    # Create an instance of the GGST type with all fields nulled out
    num_args = len(signature(table).parameters)
    attributes = [None] * num_args
    instance = table(*attributes)
    for attr, type in ggst_attributes.items():
        assert hasattr(instance, attr)
