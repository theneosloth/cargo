from .numpad import NotationMap
from html import unescape
from re import sub


def normalize(input: str) -> str:
    unescaped = unescape(input)
    ascii = sub(r"[^\x00-\x7f]", "", unescaped)
    return "".join(ascii.strip().upper().split())


# TODO: Only works on the first instance of the input
def reverse_notation(input: str) -> str:
    normalized = normalize(input)

    for k in NotationMap.keys():
        if k in normalized:
            normalized = normalized.replace(k, NotationMap[k])
            break
    return normalized


def fuzzy_string(input: str) -> str:
    return f"%{input}%"
