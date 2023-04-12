from collections import ChainMap

"""Utils for converting to and from numpad notation"""

to_numpad: dict[str, str] = {
    "QCF": "236",
    "QCB": "214",
    "HCF": "41236",
    "HCB": "63214",
    "DP": "623",
    "RDP": "421",
}

to_numpad_lower_priority: dict[str, str] = {
    "F": "6",
    "B": "4",
    "D": "2",
    "U": "8",
}

from_numpad: dict[str, str] = dict([(v, i) for i, v in to_numpad.items()])

from_numpad_lower_priority: dict[str, str] = dict(
    [(v, i) for i, v in to_numpad_lower_priority.items()]
)


_all__ = ["NotationMap"]

NotationMap = ChainMap(to_numpad, from_numpad)
