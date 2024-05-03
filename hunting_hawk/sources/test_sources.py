from .wavu import T8
from .dustloop import BBCF, GGACR, GGST
from .dreamcancel import KOFXV
import pytest
import os

RUN_SMOKE = os.getenv("HUNTING_HAWK_SMOKE", False)


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_data_smoke() -> None:
    assert len(KOFXV.get_moves_by_input("Kyo Kusanagi", "214236A/C")) == 1
    assert (KOFXV["Kyo Kusanagi"]) is not None
    assert GGST.get_moves_by_input("Baiken", "41236H") is not None
    assert T8.get_moves_by_input("Hwoarang", "f+1+2")[0].name == "Push Hands"  # type: ignore
    assert BBCF.get_moves_by_input("Jin Kisaragi", "214B") is not None
    assert GGACR.get_moves_by_input("Ky Kiske", "236S")[0].name == "S Stun Edge"  # type: ignore
    # GGACR.get_moves_by_input("Ky Kiske", "qcfS")[0].name == "S Stun Edge"  # type: ignore
    # assert GGACR.get_moves_by_input("Ky Kiske", "qcfS")[0].name == "S Stun Edge"  # type: ignore
