from .dreamcancel import KOFXV
from .dustloop import BBCF, GGST


def test_data() -> None:
    assert len(KOFXV.get_move("Kyo Kusanagi", "214236A/C")) == 1
    assert GGST.get_move("Baiken", "41236H") is not None
    assert BBCF.get_move("Jin Kisaragi", "214B") is not None
