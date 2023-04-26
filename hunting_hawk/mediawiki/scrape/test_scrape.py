import os
from inspect import signature

import pytest

from hunting_hawk.mediawiki import cargo

from . import scrape

RUN_SMOKE = os.getenv("HUNTING_HAWK_SMOKE", False)


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_name_to_type() -> None:
    test_cases = [
        ("String", str),
        ("Wikitext", cargo.Wikitext),
        ("File", cargo.File),
        ("Integer", int),
        ("List of File", list[cargo.File]),
        ("List of String", list[str]),
        ("List of Wikitext", list[cargo.Wikitext]),
        ("List of Integer", list[int]),
    ]

    for wiki_string, expected_type in test_cases:
        assert scrape.name_to_type(wiki_string) == expected_type


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_scrape_kofxv() -> None:
    WIKI_DOMAIN = "https://dreamcancel.com"
    WIKI_BASE_PATH = "/wiki"
    WIKI_API_PATH = "/w/api.phpp"
    WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
    WIKI_TABLES_PATH = "/Special:CargoTables"
    WIKI_TABLE = "MoveData_KOFXV"

    dustloop = cargo.CargoClient(
        WIKI_DOMAIN,
        WIKI_BASE_PATH,
        WIKI_API_PATH,
        table_export_path=WIKI_TABLE_EXPORT_PATH,
        tables_path=WIKI_TABLES_PATH,
    )

    kofxv_attributes = {
        "chara": str,
        "name": str,
        "guard": str,
        "hitboxes": str,
        "images": list[cargo.File],
    }

    table = scrape.parse_cargo_table(dustloop, WIKI_TABLE)
    assert scrape.parse_cargo_table(dustloop, WIKI_TABLE) is not None
    # Create an instance of the GGST type with all fields nulled out
    num_args = len(signature(table).parameters)
    attributes = [None] * num_args
    instance = table(*attributes)
    for attr, type in kofxv_attributes.items():
        assert hasattr(instance, attr)
