"""Scenario description objects: who fights whom, with what, and where.

A scenario file is plain Python and exposes either an ``Arena`` named
``ARENA`` or a zero argument ``build()`` function returning one, e.g.::

    from dom6arena.scenario import Arena, Army, Side, Squad, terrain

    ARENA = Arena(
        game="MachakaVsMekone",
        attacker=Side(nation="Machaka", army=Army("Lion Clan Commander",
                                                 [Squad(12, "Machaka Warrior")])),
        defender=Side(nation="Mekone", army=Army("Lochos", [Squad(8, "Gigante Hoplite")]),
                      god="Sphinx"),
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import gamedata

# Terrain mask values from the Dominions 6 map manual ("Common Terrain Masks").
PLAINS = 0
SMALL_PROVINCE = 1
LARGE_PROVINCE = 2
SEA = 4
FRESHWATER = 8
HIGHLANDS = 16
SWAMP = 32
WASTE = 64
FOREST = 128
FARM = 256
NOSTART = 512
MANY_SITES = 1024
DEEP = 2048
CAVE = 4096
MOUNTAINS = 8388608

TERRAIN_NAMES = {
    "plains": PLAINS,
    "small": SMALL_PROVINCE,
    "large": LARGE_PROVINCE,
    "sea": SEA,
    "freshwater": FRESHWATER,
    "highlands": HIGHLANDS,
    "swamp": SWAMP,
    "waste": WASTE,
    "forest": FOREST,
    "farm": FARM,
    "nostart": NOSTART,
    "many_sites": MANY_SITES,
    "deep": DEEP,
    "cave": CAVE,
    "mountains": MOUNTAINS,
}


def terrain(*names: str) -> int:
    """Combine terrain names into a province terrain mask."""
    mask = 0
    for name in names:
        key = name.strip().lower().replace(" ", "_")
        if key not in TERRAIN_NAMES:
            raise KeyError(f"unknown terrain {name!r}; known: {', '.join(sorted(TERRAIN_NAMES))}")
        mask |= TERRAIN_NAMES[key]
    return mask


@dataclass(frozen=True)
class Squad:
    """A group of identical units."""

    count: int
    unit: str | int


@dataclass
class Army:
    """A commander and the squads that follow him."""

    commander: str | int
    squads: list[Squad] = field(default_factory=list)
    magic: dict[str, int] = field(default_factory=dict)


@dataclass
class Side:
    nation: str | int
    army: Army
    god: str | int | None = None
    ai: int | None = None
    dominion: int | None = None
    scales: dict[str, int] = field(default_factory=dict)
    place: int | None = None


@dataclass
class Arena:
    """One scripted battle: two nations fighting over a single province."""

    attacker: Side
    defender: Side
    game: str = "Dom6Arena"
    province: int = 10
    terrain: int | None = None
    province_defense: int = 0
    era: int = 1
    turns: int = 3


@dataclass(frozen=True)
class ResolvedSide:
    nation: gamedata.Nation
    commander: gamedata.Unit
    squads: tuple[tuple[int, gamedata.Unit], ...]
    god: gamedata.Unit | None
    ai: int | None
    place: int
    dominion: int | None
    scales: dict[str, int]
    magic: dict[str, int]

    @property
    def human(self) -> bool:
        return self.ai is None


@dataclass(frozen=True)
class ResolvedArena:
    game: str
    province: int
    terrain: int | None
    province_defense: int
    era: int
    turns: int
    attacker: ResolvedSide
    defender: ResolvedSide

    @property
    def sides(self) -> tuple[ResolvedSide, ResolvedSide]:
        return (self.attacker, self.defender)

    @property
    def human(self) -> ResolvedSide:
        for side in self.sides:
            if side.human:
                return side
        raise LookupError("no human controlled side")

    @property
    def nations(self) -> tuple[gamedata.Nation, gamedata.Nation]:
        return (self.attacker.nation, self.defender.nation)


SCALE_NAMES = {
    "order": 0,
    "productivity": 1,
    "heat": 2,
    "growth": 3,
    "fortune": 4,
    "magic": 5,
}
MAGIC_PATHS = {
    "fire": 0,
    "air": 1,
    "water": 2,
    "earth": 3,
    "astral": 4,
    "death": 5,
    "nature": 6,
    "blood": 7,
}


class ScenarioError(ValueError):
    """Raised when a scenario cannot be turned into a valid map."""


def _side_from_dict(data: dict, label: str) -> "Side":
    try:
        army_data = data["army"]
        army = Army(
            commander=army_data["commander"],
            squads=[Squad(count=int(s["count"]), unit=s["unit"]) for s in army_data.get("squads", [])],
            magic=dict(army_data.get("magic", {})),
        )
        return Side(
            nation=data["nation"],
            army=army,
            god=data.get("god"),
            ai=data.get("ai"),
            dominion=data.get("dominion"),
            scales=dict(data.get("scales", {})),
            place=data.get("place"),
        )
    except (KeyError, TypeError, AttributeError) as error:
        raise ScenarioError(f"{label}: invalid side definition: {error}") from None


def from_dict(data: dict) -> "Arena":
    """Build an Arena from a plain dict (JSON text config)."""
    try:
        return Arena(
            game=data.get("game", "Dom6Arena"),
            province=int(data.get("province", 10)),
            terrain=data.get("terrain"),
            province_defense=int(data.get("province_defense", 0)),
            era=int(data.get("era", 1)),
            turns=int(data.get("turns", 3)),
            attacker=_side_from_dict(data["attacker"], "attacker"),
            defender=_side_from_dict(data["defender"], "defender"),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ScenarioError(f"invalid scenario config: {error}") from None


def _resolve_side(side: Side, era: int, province: int, label: str) -> ResolvedSide:
    try:
        nation = gamedata.find_nation(side.nation, era=era)
        commander = gamedata.find_unit(side.army.commander)
        squads = tuple((squad.count, gamedata.find_unit(squad.unit)) for squad in side.army.squads)
        god = gamedata.find_pretender(nation, side.god) if side.god is not None else None
    except KeyError as error:
        raise ScenarioError(f"{label}: {error.args[0]}") from None

    for name in side.scales:
        if name.lower() not in SCALE_NAMES:
            raise ScenarioError(f"{label}: unknown scale {name!r}")
    for name in side.army.magic:
        if name.lower() not in MAGIC_PATHS:
            raise ScenarioError(f"{label}: unknown magic path {name!r}")
    for count, unit in squads:
        if count <= 0:
            raise ScenarioError(f"{label}: squad of {unit.name} needs a positive count")
    if side.ai is not None and not 1 <= side.ai <= 5:
        raise ScenarioError(f"{label}: ai level must be 1-5, got {side.ai}")

    return ResolvedSide(
        nation=nation,
        commander=commander,
        squads=squads,
        god=god,
        ai=side.ai,
        place=side.place or province,
        dominion=side.dominion,
        scales=dict(side.scales),
        magic=dict(side.army.magic),
    )


def resolve(arena: Arena) -> ResolvedArena:
    attacker = _resolve_side(arena.attacker, arena.era, arena.province, "attacker")
    defender = _resolve_side(arena.defender, arena.era, arena.province, "defender")

    if attacker.nation.id == defender.nation.id:
        raise ScenarioError("attacker and defender must be different nations")
    return ResolvedArena(
        game=arena.game,
        province=arena.province,
        terrain=arena.terrain,
        province_defense=arena.province_defense,
        era=arena.era,
        turns=arena.turns,
        attacker=attacker,
        defender=defender,
    )
