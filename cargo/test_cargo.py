from cargo import Cargo, api_endpoint, export_endpoint, index_endpoint

test_cargo = Cargo(
    "https://example.com",
    "/wiki/superfluous",
    "?title=Special:CargoExport",
)


def test_endpoints() -> None:
    assert (
        index_endpoint(test_cargo) == "https://example.com/wiki/superfluous/index.php"
    )
    assert api_endpoint(test_cargo) == "https://example.com/wiki/superfluous/api.php"

    assert (
        export_endpoint(test_cargo)
        == "https://example.com/wiki/superfluous/index.php?title=Special:CargoExport&format=json"
    )
