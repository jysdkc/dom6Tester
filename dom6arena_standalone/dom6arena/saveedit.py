"""Save game editor: inject army compositions into ftherlnd.

A nation's troop list is stored in ftherlnd right after the nation/pretender
names as:

    [count u16] [0x630a] [0x01] ff ff [unit_type u16] * capacity

(*capacity* is the number of slots the save reserves for that nation.)

Verified operations (all persist through hosting):
- Rewrite the troop list (types + count) as long as the new total fits in the
  reserved capacity; shrinking always works, growing is bounded by *capacity*
- Swap the unit_type u16 of a squad block to change a commander's unit type

Commanders are stored separately from the troop list (the troop list only
accepts troop types; a commander id written there is dropped by the host).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from . import config

XOR = 0x4F
# Bound for the heuristic scanners that walk arbitrary bytes (a stray ff ff
# must not open a fake list).
MAX_UNIT_TYPE = 6000
# Bound for readers that take the type from a known field (unit table record,
# squad block header).  Mods use ids far above 6000 -- Debug6 hands out 9001
# and 9002 -- so the vanilla-era 6000 silently dropped them from the province
# reports and the copied-squad checks.
MAX_ANY_UNIT_TYPE = 65535
MAX_INSTANCE_ID = 500
SQUAD_PREFIX = b"\xff\xff\xff\xff"


@dataclass
class SquadBlock:
    """A squad block inside ftherlnd: ff ff ff ff [type] [member ids...]."""

    offset: int
    unit_type: int
    members: list[int] = field(default_factory=list)

    @property
    def type_offset(self) -> int:
        return self.offset + 4  # after ff ff ff ff

    @property
    def member_start(self) -> int:
        return self.offset + 6  # after prefix + type

    @property
    def end(self) -> int:
        return self.member_start + len(self.members) * 2


def find_squad_blocks(raw: bytes, unit_types: set[int] | None = None) -> list[SquadBlock]:
    """Find all squad blocks, optionally filtered by unit type."""
    blocks: list[SquadBlock] = []
    pos = 0
    length = len(raw)
    while pos < length - 8:
        idx = raw.find(SQUAD_PREFIX, pos)
        if idx == -1:
            break
        utype = struct.unpack_from("<H", raw, idx + 4)[0]
        if 0 < utype < MAX_UNIT_TYPE and (unit_types is None or utype in unit_types):
            members: list[int] = []
            p = idx + 6
            while p + 2 <= length:
                val = struct.unpack_from("<H", raw, p)[0]
                if 0 < val < MAX_INSTANCE_ID:
                    members.append(val)
                    p += 2
                else:
                    break
            if members:
                blocks.append(SquadBlock(offset=idx, unit_type=utype, members=members))
        pos = idx + 1
    return blocks


@dataclass
class RosterBlock:
    """A nation's troop list: [count u16][0x630a][0x01] ff ff [types...]."""

    count_offset: int
    types_offset: int
    declared_count: int
    entries: list[int] = field(default_factory=list)

    @property
    def capacity(self) -> int:
        """Number of troop slots the save reserves for this nation."""
        return len(self.entries)


def _find_nation_name(raw: bytes, nation_name: str) -> int:
    """Return the offset of the XOR encoded nation name, or -1."""
    candidates = [nation_name]
    for era in ("EA ", "MA ", "LA "):
        candidates.append(era + nation_name)
    alts = {
        "Nid": ["Nidhogg", "Nidhögg"],
        "Utgard": ["Utgard", "Midgård"],
    }
    for alt in alts.get(nation_name, []):
        candidates.append(alt)
        for era in ("EA ", "MA ", "LA "):
            candidates.append(era + alt)

    for name in candidates:
        enc = bytes(ord(c) ^ XOR for c in name)
        idx = raw.find(enc)
        if idx >= 0:
            return idx
    return -1


def find_roster_block(raw: bytes, nation_name: str) -> RosterBlock | None:
    """Locate a nation's troop list block in ftherlnd."""
    name_idx = _find_nation_name(raw, nation_name)
    if name_idx < 0:
        return None

    # Scan forward for the roster: ff ff followed by valid unit types
    scan_end = min(name_idx + 1024, len(raw))
    for pos in range(name_idx, scan_end - 8):
        if raw[pos] == 0xFF and raw[pos + 1] == 0xFF:
            entries: list[int] = []
            p = pos + 2
            for _ in range(1000):
                if p + 2 > len(raw):
                    break
                t = struct.unpack_from("<H", raw, p)[0]
                if t == 0 or t > MAX_UNIT_TYPE:
                    break
                entries.append(t)
                p += 2
            # A real troop list holds at least two entries; single u16 hits are
            # stray ff ff padding elsewhere in the nation block.
            if len(entries) >= 2:
                count_offset = pos - 5
                declared = 0
                if count_offset >= 0:
                    declared = struct.unpack_from("<H", raw, count_offset)[0]
                return RosterBlock(
                    count_offset=count_offset,
                    types_offset=pos + 2,
                    declared_count=declared,
                    entries=entries,
                )
    return None


def find_nation_roster(raw: bytes, nation_name: str) -> list[int]:
    """Return the list of unit types in a nation's army roster."""
    block = find_roster_block(raw, nation_name)
    return block.entries if block else []


def set_squad_type(raw: bytearray, squad: SquadBlock, new_type: int) -> None:
    struct.pack_into("<H", raw, squad.type_offset, new_type)
    squad.unit_type = new_type


def _deduplicate_squads(squads: list[SquadBlock]) -> list[SquadBlock]:
    """Keep only one squad per (type, member-tuple); the host duplicates them."""
    seen: set[tuple[int, tuple[int, ...]]] = set()
    unique: list[SquadBlock] = []
    for s in squads:
        key = (s.unit_type, tuple(s.members))
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def write_troops(raw: bytearray, block: RosterBlock, troops: list[int]) -> None:
    """Replace a nation's troop list, keeping its reserved capacity."""
    if len(troops) > block.capacity:
        raise ValueError(
            f"army of {len(troops)} exceeds the {block.capacity} slots reserved "
            f"by the template save"
        )
    for i in range(block.capacity):
        struct.pack_into("<H", raw, block.types_offset + 2 * i, 0)
    for i, unit_type in enumerate(troops):
        struct.pack_into("<H", raw, block.types_offset + 2 * i, unit_type)
    struct.pack_into("<H", raw, block.count_offset, len(troops))
    block.entries = list(troops)


def inject_nation_army(
    raw: bytearray,
    nation_name: str,
    commander_type: int,
    squads_config: list[tuple[int, int]],
) -> dict:
    """Modify ``raw`` so that ``nation_name``'s army matches the config.

    Troop composition is written into the nation's roster block (the
    authoritative troop list). The commander can only be retargeted by
    swapping the unit type of an existing squad block, so a template save
    with at least one commander squad of the right era is required.

    Args:
        raw: ftherlnd contents (modified in place).
        nation_name: nation name e.g. "Mekone".
        commander_type: unit type id for the commander.
        squads_config: list of (count, unit_type) tuples.

    Returns:
        A dict describing what was changed.
    """
    block = find_roster_block(bytes(raw), nation_name)
    if block is None:
        raise ValueError(f"nation {nation_name!r} not found in save")

    troops = [unit_type for count, unit_type in squads_config for _ in range(count)]
    if not troops:
        raise ValueError(f"no troops configured for {nation_name!r}")

    changes = {
        "nation": nation_name,
        "commander_type": commander_type,
        "capacity": block.capacity,
        "declared_count": block.declared_count,
        "troops": len(troops),
    }

    old_types = set(block.entries)
    write_troops(raw, block, troops)

    # Commander: retarget the nation's smallest existing squad (the leader's
    # personal squad) to the configured commander type.
    candidates = _deduplicate_squads(find_squad_blocks(bytes(raw), old_types))
    if any(s.unit_type == commander_type for s in candidates):
        changes["commander_set"] = True
    elif candidates:
        leader = min(candidates, key=lambda s: len(s.members))
        set_squad_type(raw, leader, commander_type)
        changes["commander_set"] = True
    else:
        changes["commander_set"] = False

    return changes


def inject_scenario(game: str, arena) -> list[dict]:
    """Apply both sides of a resolved arena to a save's ftherlnd.

    ``arena`` is a ResolvedArena (from scenario.resolve).
    """
    ftherlnd_path = config.save_dir(game) / "ftherlnd"
    raw = bytearray(ftherlnd_path.read_bytes())

    results = []
    for side in (arena.attacker, arena.defender):
        squads_config = [(count, unit.id) for count, unit in side.squads]
        changes = inject_nation_army(
            raw,
            side.nation.name,
            side.commander.id,
            squads_config,
        )
        results.append(changes)

    ftherlnd_path.write_bytes(bytes(raw))
    return results


# --- Fresh save (turn 1-2) layout -------------------------------------------------
# A freshly created game stores one record per unit, packed at a fixed stride:
#   +0  u32 unit id (1, 2, 3, ... in creation order)
#   +28 ff ff ff ff
#   +32 u16 unit type
#   +34 u16 current hit points (NOT a count; the host recomputes it)
#   +36 u16 province, +38 u16 province
#   +60 u16 per-unit value, +62 u16 nation id
# Army "squads" inside a province record use the same prefix followed by
#   [type u16] [hit points u16] [province u16] [province u16]
# so a fresh save has no squad member-id list at all; the unit records are the
# authority for which units exist.
UNIT_TABLE_STRIDE = 173
UNIT_TYPE_OFFSET = 32
UNIT_PROVINCE_OFFSET = 36


@dataclass
class UnitRecord:
    """One unit record of a fresh save (see the layout note above)."""

    offset: int
    unit_type: int

    @property
    def type_offset(self) -> int:
        return self.offset + UNIT_TYPE_OFFSET


def find_unit_table(raw: bytes) -> tuple[int, int, int] | None:
    """Locate the packed unit record table: (base offset, stride, count).

    The records are found by their u32 ids: 1, 2, 3, ... at exactly the record
    stride, which no other packed array in the save reproduces.  (The bytes
    between the id and the type are not a reliable marker: they hold per-unit
    flags such as 0x80 at +25 for a rider, and a stray 0x08 at +12.)
    """
    limit = len(raw) - UNIT_TABLE_STRIDE * 10
    for base in range(0, max(0, limit)):
        if struct.unpack_from("<I", raw, base)[0] != 1:
            continue
        count = 0
        pos = base
        while pos + UNIT_TABLE_STRIDE <= len(raw):
            if struct.unpack_from("<I", raw, pos)[0] != 1 + count:
                break
            count += 1
            pos += UNIT_TABLE_STRIDE
        if count >= 10:
            return base, UNIT_TABLE_STRIDE, count
    return None


def find_province_units(raw: bytes, province: int) -> list[UnitRecord]:
    """Unit records that sit in ``province`` (commander first, then troops)."""
    table = find_unit_table(raw)
    if table is None:
        return []
    base, stride, count = table
    records: list[UnitRecord] = []
    for index in range(count):
        offset = base + index * stride
        unit_type = struct.unpack_from("<H", raw, offset + UNIT_TYPE_OFFSET)[0]
        p1, p2 = struct.unpack_from("<HH", raw, offset + UNIT_PROVINCE_OFFSET)
        if (p1 == province and p2 == province
                and 0 < unit_type < MAX_ANY_UNIT_TYPE):
            records.append(UnitRecord(offset=offset, unit_type=unit_type))
    return records


def province_composition(raw: bytes, province: int) -> list[int]:
    """Unit types of ``province``, in record (creation) order."""
    return [record.unit_type for record in find_province_units(raw, province)]


def rewrite_province_composition(game: str, province: int,
                                 composition: list[int]) -> dict:
    """Make ``province`` hold exactly ``composition`` (unit types, in order).

    The engine fixes how many unit records a province starts with, so a
    composition has to fit into that count. Surplus records are set to unit
    type 0, which the host deletes; the first record of a province becomes the
    leading commander, so the first entry of ``composition`` should be a
    commander type.
    """
    path = config.save_dir(game) / "ftherlnd"
    raw = bytearray(path.read_bytes())
    records = find_province_units(bytes(raw), province)
    if len(records) < len(composition):
        raise ValueError(
            f"province {province} holds {len(records)} units, "
            f"cannot fit a composition of {len(composition)}"
        )
    for index, record in enumerate(records):
        unit_type = composition[index] if index < len(composition) else 0
        struct.pack_into("<H", raw, record.type_offset, unit_type)
    path.write_bytes(bytes(raw))
    return {
        "province": province,
        "available": len(records),
        "kept": len(composition),
        "removed": len(records) - len(composition),
        "composition": list(composition),
    }


def find_province_squads(raw: bytes, province: int) -> list[SquadBlock]:
    """Squad blocks of a fresh save that belong to ``province``."""
    blocks: list[SquadBlock] = []
    pos = 0
    while True:
        idx = raw.find(SQUAD_PREFIX, pos)
        if idx < 0 or idx + 12 > len(raw):
            break
        unit_type, hp, p1, p2 = struct.unpack_from("<HHHH", raw, idx + 4)
        if (
            0 < unit_type < MAX_ANY_UNIT_TYPE
            and p1 == province and p2 == province
        ):
            blocks.append(SquadBlock(offset=idx, unit_type=unit_type, members=[hp, p1, p2]))
        pos = idx + 1
    return blocks


def allocate_records(total: int, weights: list[int]) -> list[int]:
    """Split ``total`` records over ``weights`` proportionally.

    Dominions fixes the size of a starting army, so a configuration can only
    decide the *mix* of unit types. Largest-remainder rounding keeps the
    configured ratio as close as the record count allows.
    """
    weight_sum = sum(weights)
    if weight_sum <= 0:
        raise ValueError("configured counts must be positive")
    exact = [total * weight / weight_sum for weight in weights]
    shares = [int(value) for value in exact]
    leftover = total - sum(shares)
    order = sorted(range(len(weights)), key=lambda i: exact[i] - shares[i], reverse=True)
    for index in order[:leftover]:
        shares[index] += 1
    return shares


def inject_province_army(game: str, province: int, commander_type: int,
                         squads_config: list[tuple[int, int]]) -> dict:
    """Rewrite the army of ``province`` to the configured composition.

    The fresh-save army is made of unit records plus a few squad blocks. Unit
    types can be changed freely (verified to persist through hosting); the
    *number* of units in a province is fixed by the starting army the engine
    created, so the configured counts are scaled to the records that exist.

    Args:
        game: save directory name.
        province: starting province of the nation.
        commander_type: unit type for the leading record / first squad block.
        squads_config: list of (count, unit_type) tuples.
    """
    path = config.save_dir(game) / "ftherlnd"
    raw = bytearray(path.read_bytes())

    blocks = find_province_squads(raw, province)
    units = find_province_units(raw, province)
    if not blocks:
        raise ValueError(f"no squad blocks found in province {province}")
    if not units:
        raise ValueError(f"no unit records found in province {province}")
    if not squads_config:
        raise ValueError("no troops configured")

    # Unit records: the first record is the commander (creation order).
    commander = units[0]
    troops = units[1:]
    allocation = allocate_records(len(troops), [count for count, _ in squads_config])
    applied: dict[int, int] = {}
    index = 0
    for (_, unit_type), share in zip(squads_config, allocation):
        for _ in range(share):
            struct.pack_into("<H", raw, troops[index].type_offset, unit_type)
            index += 1
        if share:
            applied[unit_type] = applied.get(unit_type, 0) + share
    struct.pack_into("<H", raw, commander.type_offset, commander_type)

    # Squad blocks: first one is the commander's, the rest show the configured
    # troop types in order (they only control what the .trn displays).
    troop_types: list[int] = []
    for count, unit_type in squads_config:
        if unit_type not in troop_types:
            troop_types.append(unit_type)
    for i, block in enumerate(blocks[1:]):
        set_squad_type(raw, block, troop_types[min(i, len(troop_types) - 1)])
    set_squad_type(raw, blocks[0], commander_type)

    path.write_bytes(bytes(raw))

    requested = sum(count for count, _ in squads_config)
    return {
        "province": province,
        "commander_type": commander_type,
        "squad_blocks": len(blocks),
        "unit_records": len(units),
        "requested": requested,
        "applied": sum(applied.values()),
        "composition": sorted(applied.items()),
    }


def read_squads(game: str, nation_name: str) -> list[tuple[int, int]]:
    """Return a nation's current army as (unit_type, count) pairs from the roster."""
    raw = (config.save_dir(game) / "ftherlnd").read_bytes()
    roster = find_nation_roster(raw, nation_name)
    if not roster:
        return []
    from collections import Counter

    counts = Counter(roster)
    return sorted(counts.items())
