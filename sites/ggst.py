"""A wrapper around dreamcancel.com cargo export endpoints."""

from dataclasses import dataclass, field, fields
from typing import List

from cargo.cargo import (Cargo, CargoCache, CargoError, CargoParameters,
                         cargo_export)

WIKI_DOMAIN = "https://dustloop.com"
WIKI_BASE_PATH = "/wiki"
WIKI_TABLE_EXPORT_PATH = "?title=Special:CargoExport"
WIKI_TABLE = "MoveData_GGST"

dreamcancel = Cargo(WIKI_DOMAIN, WIKI_BASE_PATH, WIKI_TABLE_EXPORT_PATH)
cache = CargoCache()


@dataclass(eq=True, frozen=True)
class Move:
    """A representation of a KOFXV character."""

    chara: str = ""
    images: str = ""
    name: str = ""
    input: str = ""
    damage: str = ""
    guard: str = ""
    startup: str = ""
    active: str = ""
    recovery: str = ""
    onBlock: str = ""
    onHit: str = ""
    level: str = ""
    # chType: str = ""
    # hitboxes: str = ""
    # notes: str = ""
    # type: str = ""
    # riscGain: str = ""
    # riscLoss: str = ""
    # wallDamage: str = ""
    # proration: str = ""
    # invuln: str = ""
    # cancel: str = ""


# TODO:  DOES NOT ACTUALLY TYPECHECK
def list_to_moves(moves: list) -> List[Move]:
    """Copy all keys from res to Character."""
    res = []

    for m in moves:
        move = Move(**m)
        res.append(move)

    return res


def get_ggst(params: CargoParameters) -> List[Move]:
    """Wrap around MoveData_KOFXV."""
    field_param = ",".join([f.name for f in fields(Move)])

    merged_params: CargoParameters = {
        "fields": field_param,
        "tables": WIKI_TABLE,
    }

    result = cargo_export(dreamcancel, merged_params | params, cache)

    match result:
        case list():
            return list_to_moves(result)
        case _:
            raise CargoError("Unexpected type.")


def get_character(char: str) -> List[Move]:
    """Return the movelist for a character CHARA."""
    params: CargoParameters = {
        "where": f"chara='{char}'",
    }
    result = get_ggst(params)
    return result


def get_move(char: str, input: str) -> List[Move]:
    """Return the movelist for a character CHARA."""
    params: CargoParameters = {
        "where": f'chara="{char}" AND input="{input}"',
    }
    result = get_ggst(params)
    return result
