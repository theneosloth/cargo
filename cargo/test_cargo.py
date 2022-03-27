from . import cargo

test_cargo = cargo.Cargo(
    "https://example.com",
    "/wiki/superfluous",
    "?title=Special:CargoExport",
)


def test_endpoints() -> None:
    assert (
        test_cargo.index_endpoint() == "https://example.com/wiki/superfluous/index.php"
    )
    assert test_cargo.api_endpoint() == "https://example.com/wiki/superfluous/api.php"

    assert (
        test_cargo.export_endpoint()
        == "https://example.com/wiki/superfluous/index.php?title=Special:CargoExport&format=json"
    )
