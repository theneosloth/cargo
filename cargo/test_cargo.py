from . import cargo

test_cargo = cargo.Cargo(
    "https://example.com",
    "/wiki/superfluous",
    "?title=Special:CargoExport",
)


def test_init() -> None:
    match test_cargo.headers:
        case {'User-Agent': header_dict}:
            assert header_dict is not None
        case _:
            raise Exception(f"No user agent found in {test_cargo.headers}")


def test_endpoints() -> None:
    assert (
        test_cargo.index_endpoint() == "https://example.com/wiki/superfluous/index.php"
    )
    assert test_cargo.api_endpoint() == "https://example.com/wiki/superfluous/api.php"

    assert (
        test_cargo.export_endpoint()
        == "https://example.com/wiki/superfluous/index.php?title=Special:CargoExport&format=json"
    )


def test_simple_comma_join() -> None:
    empty_query_str = ""
    query_str = "test,one"
    query_list = ["test", "one"]
    assert(cargo.simple_comma_join(empty_query_str) == "")
    assert(cargo.simple_comma_join(query_str) == "test,one")
    assert(cargo.simple_comma_join(query_list) == "test,one")

