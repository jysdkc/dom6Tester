"""Turn a resolved scenario into a Dominions 6 map file (and its image)."""

from __future__ import annotations

import shutil
from pathlib import Path

from . import config
from .scenario import MAGIC_PATHS, SCALE_NAMES, ResolvedArena, ResolvedSide

TEMPLATE_MAP = config.ASSETS_DIR / "arena.map"
TEMPLATE_TGA = config.ASSETS_DIR / "arena.tga"

# Province 5 and 8 are the two land start locations of the arena template,
# 10 is the big central "Land Arena" province where the armies meet.
CENTER_PROVINCE = 10
START_PROVINCES = (5, 8)


def _side_lines(side: ResolvedSide, start: int, arena: ResolvedArena) -> list[str]:
    lines = [
        f"#computerplayer {side.nation.id} {side.ai}" if side.ai is not None
        else f"#allowedplayer {side.nation.id}",
        f"#specstart {side.nation.id} {start}",
    ]
    if side.god is not None:
        lines.append(f"#god {side.nation.id} {side.god.id}")
    if side.dominion is not None:
        lines.append(f"#dominionstr {side.nation.id} {side.dominion}")
    for name, value in side.scales.items():
        lines.append(f"#scale {side.nation.id} {SCALE_NAMES[name.lower()]} {value}")

    lines.append(f"#setland {side.place}")
    if side.magic:
        lines.append("#clearmagic")
        for name, level in side.magic.items():
            lines.append(f"#mag_{name.lower()} {level}")
    lines.append(f"#commander {side.commander.id}")
    for count, unit in side.squads:
        lines.append(f"#units {count} {unit.id}")
    return lines


def render_map(arena: ResolvedArena) -> str:
    text = TEMPLATE_MAP.read_text(encoding="utf-8", errors="replace")
    text = text.replace("#dom2title $map_name", f"#dom2title {arena.game}")
    text = text.replace("#imagefile CustomArena.tga", f"#imagefile {arena.game}.tga")
    text = text.replace("#winterimagefile CustomArena_winter.tga\n", "")

    kept = [line for line in text.splitlines() if not line.strip().startswith("$")]
    text = "\n".join(kept) + "\n"

    if arena.terrain is not None:
        text = _override_terrain(text, arena.province, arena.terrain)

    block = [f"#victorycondition 0"]
    if arena.province_defense:
        block.append(f"#defence {arena.province} {arena.province_defense}")
    block += _side_lines(arena.attacker, START_PROVINCES[0], arena)
    block += _side_lines(arena.defender, START_PROVINCES[1], arena)
    # Put both sides at war so the armies fight as soon as they share a province,
    # instead of waiting for the AI to declare war.
    block.append(
        f"#startwar {arena.attacker.nation.id} {arena.defender.nation.id}"
    )

    # The very first "#scenario" line is the template's own marker.
    return text.replace("#scenario", "#scenario\n" + "\n".join(block), 1)


def _override_terrain(text: str, province: int, mask: int) -> str:
    """Add terrain bits to the template mask instead of replacing it.

    The arena province uses a few flags of its own (gate, arena size), so the
    scenario terrain is OR-ed on top of whatever the template already has.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"#terrain {province} "):
            try:
                current = int(stripped.split()[2])
            except (IndexError, ValueError):
                current = 0
            lines[index] = f"#terrain {province} {current | mask}"
            break
    else:
        lines.append(f"#terrain {province} {mask}")
    return "\n".join(lines) + "\n"


def write_map(arena: ResolvedArena) -> tuple[Path, Path]:
    """Write <game>.map and <game>.tga into <appdata>/maps/<game>/.

    Dominions looks maps up inside a folder named after the map, so the map and
    its image live in their own directory.
    """
    folder = config.maps_dir() / arena.game
    folder.mkdir(parents=True, exist_ok=True)

    map_path = folder / f"{arena.game}.map"
    tga_path = folder / f"{arena.game}.tga"
    with map_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_map(arena))
    shutil.copyfile(TEMPLATE_TGA, tga_path)
    return map_path, tga_path
