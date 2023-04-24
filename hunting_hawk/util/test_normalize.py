from .normalize import reverse_notation


def test_reverse_notaiton() -> None:
    assert reverse_notation("236P") == "QCFP"
    assert reverse_notation("DPlP") == "623LP"
    assert reverse_notation("qcfS") == "236S"
