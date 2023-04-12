from .numpad import NotationMap


def test_numpad() -> None:
    assert NotationMap["QCF"] == "236"
    assert NotationMap["236"] == "QCF"
