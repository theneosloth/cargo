from .numpad import NotationMap
from html import unescape


def normalize(input: str) -> str:
    return unescape(input.strip()).upper()


# TODO: Only works on the first instance of the input
def reverse_notation(input: str) -> str:
    normalized = normalize(input)

    for k in NotationMap.keys():
        if k in normalized:
            normalized = normalized.replace(k, NotationMap[k])
            break
    return normalized


def fuzzy_string(input: str) -> str:
    normalized = normalize(input)
    valid_inputs = [input for input in normalized if input not in [",", "."]]
    return f"{'%'.join(valid_inputs)}"
