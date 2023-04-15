from .dreamcancel import KOFXV
from .dustloop import BBCF, GGACR, GGST


def test_data_smoke() -> None:
    assert len(KOFXV.get_moves_by_input("Kyo Kusanagi", "214236A/C")) == 1
    assert (KOFXV["Kyo Kusanagi"]) is not None
    assert len(KOFXV) >= 49
    assert GGST.get_moves_by_input("Baiken", "41236H") is not None
    assert BBCF.get_moves_by_input("Jin Kisaragi", "214B") is not None
    assert GGACR.get_moves_by_input("Ky Kiske", "236S")[0].name == "S Stun Edge"  # type: ignore
    list = GGACR.get_moves_by_input("Ky Kiske", "qcfS")[0].name == "S Stun Edge"  # type: ignore
    assert GGACR.get_moves_by_input("Ky Kiske", "qcfS")[0].name == "S Stun Edge"  # type: ignore
