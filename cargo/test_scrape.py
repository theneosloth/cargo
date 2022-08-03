from inspect import signature

from . import cargo, scrape


def test_scrape_ggst() -> None:
    WIKI_DOMAIN = "https://dustloop.com"
    WIKI_BASE_PATH = "/wiki"
    WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
    WIKI_TABLES_PATH = "/Special:CargoTables"
    WIKI_TABLE = "MoveData_GGST"

    dustloop = cargo.Cargo(
        WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH
    )

    ggst_attributes = {"chara": str, "name": str, "prorate": str, "images": list[str]}

    table = scrape.parse_cargo_table(dustloop, WIKI_TABLE)
    assert scrape.parse_cargo_table(dustloop, WIKI_TABLE) is not None
    # Create an instance of the GGST type with all fields nulled out
    num_args = len(signature(table).parameters)
    attributes = [None] * num_args
    instance = table(*attributes)
    for attr, type in ggst_attributes.items():
        assert hasattr(instance, attr)


def test_scrape_kofxv() -> None:
    WIKI_DOMAIN = "https://dreamcancel.com"
    WIKI_BASE_PATH = "/wiki"
    WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
    WIKI_TABLES_PATH = "/Special:CargoTables"
    WIKI_TABLE = "MoveData_KOFXV"

    dustloop = cargo.Cargo(
        WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH, WIKI_TABLES_PATH
    )

    kofxv_attributes = {
        "chara": str,
        "name": str,
        "guard": str,
        "hitboxes": str,
        "images": list[str],
    }

    table = scrape.parse_cargo_table(dustloop, WIKI_TABLE)
    assert scrape.parse_cargo_table(dustloop, WIKI_TABLE) is not None
    # Create an instance of the GGST type with all fields nulled out
    num_args = len(signature(table).parameters)
    attributes = [None] * num_args
    instance = table(*attributes)
    for attr, type in kofxv_attributes.items():
        assert hasattr(instance, attr)
