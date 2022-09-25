from .dreamcancel import KOFXV
from .dustloop import BBCF, GGACR, GGST


def test_data_smoke() -> None:
    assert len(KOFXV.get_moves("Kyo Kusanagi", "214236A/C")) == 1
    assert GGST.get_moves("Baiken", "41236H") is not None
    assert BBCF.get_moves("Jin Kisaragi", "214B") is not None
    assert GGACR.get_moves("Ky Kiske", "236S")[0].name == "S Stun Edge"  # type: ignore
    assert len(KOFXV.get_moves("Iori Yagami", "236")) >= 12
