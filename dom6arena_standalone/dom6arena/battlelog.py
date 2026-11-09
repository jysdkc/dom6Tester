"""Read battle information out of the Dominions 6 host log.

Marker formats below are validated against a real host log (fm game, turn 13,
four battles in one turn):

* ``  105 vs 101 in lnr 126 (castlemode 2) lsatt0 lsdef0 xvcr105`` opens a
  battle block: tactical attacker player number, defender player number and
  province.  Player numbers are game slots (0 = independents, 100+ = nations);
  the host log never maps them to nation names.
* ``deploybfterrain: lnr 126 (Farseer Mountains), ...`` gives the province name.
* ``battle winner 101, afterbatticks 150000`` ends the battle proper.
* ``broken unit: Black Hawk (unr 8659, hp 5, lnr -9), canret 1`` lists routed
  units in the aftermath (dead units are not itemised in the host log).
* ``battlecount Gunter the Commander of Ulm, kills 1`` lists the commanders of
  both sides, once before the battle (kills 0) and once after; the tactical
  attacker's commanders come first.
* per unit before/after arrays are only written when a battle replay is opened
  in the client (``getbattlecountfromvcr``); when present they give exact
  losses for the replayed battle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

BATTLE_STARTED = re.compile(r"^\s*(\d+) vs (\d+) in lnr (\d+) \(castlemode (\d+)\)", re.M)
WINNER = re.compile(r"battle winner (\d+), afterbatticks (\d+)")
PROVINCE_NAME = re.compile(r"deploybfterrain: lnr (\d+) \(([^)]+)\)")
BROKEN = re.compile(r"broken unit: (.+?) \(unr \d+, hp -?\d+, lnr -?\d+\), canret \d")
BATTLECOUNT = re.compile(r"battlecount (.+?), kills (\d+)")
VCR = "getbattlecountfromvcr"
# "<side> : <count> <unit name>" - side 0/1 attacker before/after, 2/3 defender.
UNIT_ARRAY = re.compile(r"^\s*([0-3])\s*:\s*(\d+)\s+(\S.*?)\s*$")

BEFORE_CODES = {"0": "attacker", "2": "defender"}
AFTER_CODES = {"1": "attacker", "3": "defender"}


@dataclass
class UnitEntry:
    side: str  # "attacker" | "defender"
    phase: str  # "before" | "after"
    count: int
    unit: str


@dataclass
class Battle:
    index: int
    attacker_id: int | None = None
    defender_id: int | None = None
    province: int | None = None
    province_name: str | None = None
    winner_id: int | None = None
    routed: list[str] = field(default_factory=list)
    commanders: list[str] = field(default_factory=list)
    entries: list[UnitEntry] = field(default_factory=list)

    @property
    def has_unit_data(self) -> bool:
        return bool(self.entries)

    @property
    def winner_side(self) -> str | None:
        """Tactical winner: "attacker", "defender" or None (unknown/indy)."""
        if self.winner_id is None:
            return None
        if self.winner_id == self.attacker_id:
            return "attacker"
        if self.winner_id == self.defender_id:
            return "defender"
        return None

    def counts(self, side: str, phase: str) -> dict[str, int]:
        return {
            entry.unit: entry.count
            for entry in self.entries
            if entry.side == side and entry.phase == phase
        }

    def losses(self, side: str) -> dict[str, int]:
        before = self.counts(side, "before")
        after = self.counts(side, "after")
        return {unit: before[unit] - after.get(unit, 0) for unit in before}


@dataclass
class LogScan:
    battles: list[Battle]
    raw_battle_count: int

    @property
    def found(self) -> bool:
        return bool(self.battles)


def _parse_arrays(text: str) -> list[Battle]:
    """Extract per unit arrays that follow a getbattlecountfromvcr marker."""
    battles: list[Battle] = []
    position = 0
    while True:
        start = text.find(VCR, position)
        if start < 0:
            break
        position = start + len(VCR)
        entries: list[UnitEntry] = []
        for line in text[position:].splitlines()[1:]:
            if not line.strip():
                continue
            match = UNIT_ARRAY.match(line)
            if not match:
                break
            code, count, unit = match.groups()
            side = BEFORE_CODES.get(code) or AFTER_CODES[code]
            phase = "before" if code in BEFORE_CODES else "after"
            entries.append(UnitEntry(side=side, phase=phase, count=int(count), unit=unit.strip()))
        if entries:
            battles.append(Battle(index=len(battles), entries=entries))
    return battles


def _parse_block(index: int, block: str, started: re.Match[str]) -> Battle:
    battle = Battle(
        index=index,
        attacker_id=int(started.group(1)),
        defender_id=int(started.group(2)),
        province=int(started.group(3)),
    )
    winner = WINNER.search(block)
    if winner:
        battle.winner_id = int(winner.group(1))
    for name in PROVINCE_NAME.finditer(block):
        if int(name.group(1)) == battle.province:
            battle.province_name = name.group(2).strip()
            break
    battle.routed = [match.group(1).strip() for match in BROKEN.finditer(block)]

    # battlecount lines appear twice per battle; the post-battle wave (after the
    # winner line) carries the final kill counts.
    kills_text = block[winner.end():] if winner else block
    battle.commanders = [match.group(1).strip() for match in BATTLECOUNT.finditer(kills_text)]
    return battle


def scan(text: str) -> LogScan:
    """Return every battle mentioned in a host log."""
    starts = list(BATTLE_STARTED.finditer(text))
    battles: list[Battle] = []
    for index, started in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        battles.append(_parse_block(index, text[started.start():end], started))

    arrays = _parse_arrays(text)
    for index, extra in enumerate(arrays):
        if index < len(battles):
            battles[index].entries = extra.entries
        else:
            extra.index = len(battles)
            battles.append(extra)
    return LogScan(battles=battles, raw_battle_count=len(battles))


def any_battle(text: str) -> bool:
    return bool(WINNER.search(text) or BATTLE_STARTED.search(text))
