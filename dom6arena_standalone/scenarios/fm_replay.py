"""End-to-end pipeline test against a real game save.

The ``fm`` save is a real (mod-free) game whose current turn replays the same
battles every time a clone is hosted, because the submitted .2h orders are
cloned along with it.  Turn 13 of that game has Ragha (105) attacking Ulm (101)
in Farseer Mountains plus three more battles, so hosting a clone once always
produces real battle log data.

This does not modify ``fm`` itself - the runner clones it to ``fm_1`` ... first.
"""

from dom6arena.scenario import Arena, Army, Side

ARENA = Arena(
    game="fm",
    era=3,
    province=126,
    turns=1,
    attacker=Side(
        nation="Ragha",
        army=Army(commander="Great Hawk"),  # battlecount: "Dreamdance the Great Hawk"
    ),
    defender=Side(
        nation="Ulm",
        army=Army(commander=1016),  # Commander of Ulm (LA); "Gunter the Commander of Ulm" in log
        ai=2,
    ),
)
