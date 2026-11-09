"""Unit, nation and pretender lookups backed by the CSV exports in data/.

The CSVs come from the Dom6 Inspector data export (same tables the community
modding tools use).  Every map command accepts numeric ids, but writing names
in a scenario is much easier to read, so scenarios may use either.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import DATA_DIR

GOLD_OFFSET = 10000  # leader costs include a +10000 gold marker in the data
# Monster 134 (Royal Guard) is wrongly listed in pretenders.csv for nation 61;
# the Inspector filters that single record out (see ``pretenders``).
ROYAL_GUARD_TROOP = 134


@dataclass(frozen=True)
class Unit:
    id: int
    name: str
    gold: int
    resources: int
    paths: tuple[int, ...] = ()
    startdom: int = 0
    pathcost: int = 0
    leader: int = 0
    magicleader: int = 0
    undeadleader: int = 0
    unique: bool = False
    fixedname: str = ""
    immobile: bool = False


@dataclass(frozen=True)
class Nation:
    id: int
    name: str
    epithet: str
    abbreviation: str
    era: int
    file_name_base: str = ""


def _split_rows(path: Path) -> list[list[str]]:
    """Read a tab separated export that may or may not be CSV-quoted.

    The delimiter is decided per line: the exports are tab separated, but a
    quoted field may still contain commas (``"Bear, Wolf and Crow"``), so
    splitting on commas alone would cut those rows in half.
    """
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        delimiter = "\t" if "\t" in line else ","
        cells = [cell.strip() for cell in next(csv.reader([line], delimiter=delimiter))]
        while cells and cells[-1] == "":
            cells.pop()
        if cells:
            rows.append(cells)
    return rows


@lru_cache(maxsize=1)
def units() -> dict[int, Unit]:
    path = DATA_DIR / "units.csv"
    rows = _split_rows(path)
    header = rows[0]
    index = {name: i for i, name in enumerate(header)}

    def cell(row: list[str], key: str, default: str = "0") -> str:
        i = index.get(key)
        return row[i] if i is not None and i < len(row) and row[i] != "" else default

    result: dict[int, Unit] = {}
    for row in rows[1:]:
        try:
            uid = int(cell(row, "id"))
            basecost = int(cell(row, "basecost"))
            rcost = int(cell(row, "rcost"))
        except ValueError:
            continue
        def number(key: str) -> int:
            try:
                return int(cell(row, key))
            except ValueError:
                return 0

        result[uid] = Unit(
            id=uid,
            name=cell(row, "name", f"unit {uid}"),
            gold=max(0, basecost - GOLD_OFFSET) if basecost >= GOLD_OFFSET else basecost,
            resources=rcost,
            paths=tuple(number(k) for k in ("F", "A", "W", "E", "S",
                                            "D", "N", "G", "B", "H")),
            startdom=number("startdom"),
            pathcost=number("pathcost"),
            leader=number("leader"),
            magicleader=number("magicleader"),
            undeadleader=number("undeadleader"),
            unique=number("unique") != 0,
            fixedname=cell(row, "fixedname", ""),
            immobile=number("immobile") != 0,
        )
    return result


@lru_cache(maxsize=1)
def nations() -> dict[int, Nation]:
    result: dict[int, Nation] = {}
    for row in _split_rows(DATA_DIR / "nations.csv")[1:]:
        try:
            nid = int(row[0])
            era = int(row[5]) if len(row) > 5 else 0
        except (IndexError, ValueError):
            continue
        result[nid] = Nation(
            id=nid,
            name=row[1] if len(row) > 1 else f"nation {nid}",
            epithet=row[2] if len(row) > 2 else "",
            abbreviation=row[3] if len(row) > 3 else "",
            file_name_base=row[4] if len(row) > 4 else "",
            era=era,
        )
    return result


@lru_cache(maxsize=1)
def pretenders() -> dict[int, set[int]]:
    """nation id -> set of pretender monster ids that nation may take.

    ``pretender_types_by_nation.csv`` carries one bogus entry: monster 134
    (Royal Guard) is listed for nation 61 but is an ordinary troop there.
    The Inspector drops exactly that one record when it builds the
    ``Pretenders`` category (``if (attr.monster_number != 134)`` in
    MNation.js, commented "Why is royal guard marked as pretender?"), so it
    is dropped here too.
    """
    result: dict[int, set[int]] = {}
    for row in _split_rows(DATA_DIR / "pretenders.csv")[1:]:
        try:
            monster, nation = int(row[0]), int(row[1])
        except (IndexError, ValueError):
            continue
        if monster == ROYAL_GUARD_TROOP:
            continue
        result.setdefault(nation, set()).add(monster)
    return result


@lru_cache(maxsize=1)
def pretender_chassis() -> set[int]:
    """Every unit id that some nation may take as a pretender.

    A nation has exactly one god, so a chassis taken from a scout report
    cannot be a second god of that nation.  The engine still keeps such a
    chassis in an ordinary unit record (checked by hosting one): it is copied
    as a regular unit, not as a god.
    """
    return {monster for ids in pretenders().values() for monster in ids}


@lru_cache(maxsize=1)
def heroes() -> dict[int, set[int]]:
    """nation id -> its hero unit ids (the Inspector's "Heroes" category).

    The Inspector never reads a "hero" column: MNation.js collects the nation
    attributes 139..144 (hero1..hero6, unique heroes) and 145/146/149
    (multihero1..3) and stamps those units ``hero (unique)`` /
    ``hero (multi)``.  MUnit.unitSortableTypes maps both to a ``cmdr`` sort
    key, so a hero is always a commander.
    """
    result: dict[int, set[int]] = {}
    for row in _split_rows(DATA_DIR / "hero_types_by_nation.csv")[1:]:
        try:
            monster, nation = int(row[0]), int(row[1])
        except (IndexError, ValueError):
            continue
        result.setdefault(nation, set()).add(monster)
    return result


@lru_cache(maxsize=1)
def hero_units() -> set[int]:
    """Every unit id that is the hero of some nation.

    Hero-ness is a property of the unit, not of the army that fields it, so
    this set is not filtered by nation.
    """
    return {monster for ids in heroes().values() for monster in ids}


@lru_cache(maxsize=1)
def recruit_lists() -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """nation id -> commander ids / troop ids, per the Dom6 Inspector export.

    The Inspector does not classify units from ``BaseU.csv`` columns (that
    export has no commander flag).  It builds every nation's type lists from
    ``gamedata/{fort,nonfort,coast}_{leader,troop}_types_by_nation.csv``:
    ``fort_leader_types_by_nation`` becomes ``nation.commanders`` and
    ``fort_troop_types_by_nation`` becomes ``nation.units`` (MNation.js), and
    each listed unit is stamped ``type = 'c'`` / ``'u'``.  That stamp is what
    ``MUnit.isCmdr`` reads, so these tables are the authority for "is this
    unit a commander".
    """
    commanders: dict[int, set[int]] = {}
    troops: dict[int, set[int]] = {}
    for kind, table in (("leader", commanders), ("troop", troops)):
        for area in ("fort", "nonfort", "coast"):
            rows = _split_rows(DATA_DIR / f"{area}_{kind}_types_by_nation.csv")
            for row in rows[1:]:
                try:
                    monster, nation = int(row[0]), int(row[1])
                except (IndexError, ValueError):
                    continue
                table.setdefault(nation, set()).add(monster)
    return commanders, troops


@lru_cache(maxsize=1)
def commander_units() -> set[int]:
    """Every unit id some nation recruits as a commander.

    The unit *is* a commander regardless of which nation fields it, so the
    per-nation tables are folded into one set: the arena enemy nation is
    chosen at random, and a copied unit must be typed by its id alone.
    """
    commanders, _ = recruit_lists()
    return {monster for ids in commanders.values() for monster in ids}


@lru_cache(maxsize=1)
def troop_units() -> set[int]:
    """Every unit id some nation recruits as a troop (see commander_units)."""
    _, troops = recruit_lists()
    return {monster for ids in troops.values() for monster in ids}


def unit_type_role(unit_id: int) -> str | None:
    """``'pretender'``/``'cmdr'``/``'unit'`` for ``unit_id``, by id alone.

    Same precedence the Inspector applies when it stamps a unit's type: a
    pretender chassis first, then a commander, then a hero, then a troop
    (``'Pretender'`` / ``cmdr`` / ``hero (unique)`` / ``hero (multi)`` /
    ``unit``).  The per-nation leader/troop tables are folded into unions
    instead of being looked up for one nation: the copied units come from a
    scout report, which never names their nation, and the arena's enemy nation
    is random, so only an id-level answer can be right.  The two unions are
    disjoint (0 shared ids in the export), so there is no ambiguity.  ``None``
    means the export lists the unit nowhere (summons, mercenaries,
    independents and mod units are absent from these tables), so the caller
    has to fall back to unit attributes.
    """
    if unit_id in pretender_chassis():
        return "pretender"
    if unit_id in commander_units():
        return "cmdr"
    if unit_id in hero_units():
        return "cmdr"
    if unit_id in troop_units():
        return "unit"
    return None


def find_unit(token: str | int) -> Unit:
    table = units()
    if isinstance(token, int) or str(token).strip().isdigit():
        uid = int(token)
        if uid not in table:
            raise KeyError(f"unknown unit id {uid}")
        return table[uid]
    wanted = str(token).strip().lower()
    exact = [unit for unit in table.values() if unit.name.lower() == wanted]
    if len(exact) == 1:
        return exact[0]
    partial = [unit for unit in table.values() if wanted in unit.name.lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise KeyError(f"unknown unit {token!r}")
    options = ", ".join(f"{unit.name} ({unit.id})" for unit in sorted(partial, key=lambda u: u.id)[:8])
    raise KeyError(
        f"ambiguous unit {token!r} matches {len(partial)} units, use the id: {options}"
    )


def find_nation(token: str | int, era: int | None = None) -> Nation:
    table = nations()
    if isinstance(token, int) or str(token).strip().isdigit():
        nid = int(token)
        if nid not in table:
            raise KeyError(f"unknown nation id {nid}")
        return table[nid]

    wanted = str(token).strip().lower()
    matches = [
        nation
        for nation in table.values()
        if wanted in (nation.name.lower(), nation.abbreviation.lower())
        or wanted == nation.name.lower().replace(" ", "")
    ]
    if era is not None:
        matches = [nation for nation in matches if nation.era == era]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise KeyError(f"unknown nation {token!r}" + (f" in era {era}" if era else ""))
    options = ", ".join(f"{n.name} ({n.id}, era {n.era})" for n in matches[:8])
    raise KeyError(f"ambiguous nation {token!r}: {options}")


def find_pretender(nation: Nation, token: str | int) -> Unit:
    unit = find_unit(token)
    allowed = pretenders().get(nation.id)
    if allowed is not None and unit.id not in allowed:
        raise KeyError(
            f"{unit.name} ({unit.id}) is not a pretender available to {nation.name} ({nation.id})"
        )
    return unit
