"""Example scenario: 12 Machaka warriors vs 8 Mekone gigantes in the arena.

Attacker (the nation you pick in the client) is always the human slot; the
defender is driven by the AI, which attacks the arena province on turn 1 or 2.
"""

from dom6arena.scenario import Arena, Army, Side, Squad, terrain, FOREST

ARENA = Arena(
    game="Dom6ArenaDemo",
    era=1,
    province=10,
    terrain=terrain("large", "forest"),
    province_defense=0,
    turns=3,
    attacker=Side(
        nation="Machaka",
        army=Army(
            commander="Lion Clan Commander",
            squads=[Squad(12, 2300)],  # 2300 = Machaka Warrior (the name exists 3x)
        ),
    ),
    defender=Side(
        nation="Mekone",
        army=Army(
            commander=3111,  # Lochos (two units share that name, so use the id)
            squads=[Squad(8, "Gigante Hoplite")],
        ),
        god="Sphinx",
        ai=2,
    ),
)
