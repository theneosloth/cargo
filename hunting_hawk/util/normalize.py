from .numpad import NotationMap


# TODO: Only works on the first instance of the input
def reverse_notation(input: str) -> str:
    normalized = input.strip().upper()

    for k in NotationMap.keys():
        if k in normalized:
            normalized = normalized.replace(k, NotationMap[k])
            break
    return normalized


def fuzzy_string(input: str) -> str:
    normalized = input.strip().upper().split(" ")
    valid_inputs = [input for input in normalized if input not in [",", "."]]
    return f"{'%'.join(valid_inputs)}"
