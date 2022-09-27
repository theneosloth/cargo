from . import cargo

test_cargo = cargo.Cargo(
    "https://example.com",
    "/wiki/superfluous",
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
