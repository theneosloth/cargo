from .normalize import fuzzy_string, normalize, reverse_notation


def test_normalize() -> None:
    assert normalize("236    P") == "236P"
    assert normalize("214lk") == "214LK"


def test_reverse_notaiton() -> None:
    assert reverse_notation("236P236P") == "QCFPQCFP"
    assert reverse_notation("DPlP") == "623LP"
    assert reverse_notation("qcfS") == "236S"


def test_fuzzy_string() -> None:
    assert fuzzy_string("236P") == "%236P%"
