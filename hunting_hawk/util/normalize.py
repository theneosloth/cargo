from .numpad import NotationMap
from html import unescape


def normalize(input: str) -> str:
    return "".join(unescape(input).strip().upper().split())


def normalize_name(name: str) -> str:
    return "_".join(normalize(name).split())


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
