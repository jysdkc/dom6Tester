"""Create a two human player game without the GUI, then configure both armies.

Dominions 6 keeps a game alive only while a human player owns a pretender, so
``--newgame`` needs pretender files already sitting in the new save directory:
for every nation ``<era>_<file_name_base>.2h`` is loaded as a human god and a
``.trn`` is written for that player.  The map is produced by ``--makemap``
(land only, no rivers), patched into a two player scenario and the armies from
the scenario file are then written into ftherlnd before a first host.
"""

from __future__ import annotations

import itertools
import json
import random
import re
import shutil
import struct
import subprocess
import time
from collections import deque
from pathlib import Path

from . import config, gamedata, saveedit, scenario

ERA_PREFIX = {1: "early", 2: "mid", 3: "late"}
NEWGAME_FLAGS = ["--nosteam", "--nopopups", "--textonly", "--nocrashbox"]
RIVER_BORDER = re.compile(r"^#neighbourspec\s+\d+\s+\d+\s+2\s*$")
CHEAT_MARKERS = ("bad unit", "has cheated", "king has bad mnr")
CRC_LINE = re.compile(r"checkcrc done\. len \d+ crc (\d+) readcrc (\d+)")
SEA_FLAG = 0x4                # #terrain "sea" bit; deep sea (0x800) sets it too
# Chassis of the shipped ``resources/pretender_placeholder.2h`` ("Spirit of
# Bones").  It comes from a pretender mod, so the engine rejects the god as
# an unknown monster ("king has bad mnr") unless that mod is enabled.
PLACEHOLDER_CHASSIS = 8997


class NewGameError(RuntimeError):
    """Raised when the game or its map could not be created."""


def _exe() -> str:
    return str(config.game_dir() / config.EXE_NAME)


def _read_log(settle: float = 0.4) -> str:
    path = config.log_path()
    if not path.exists():
        return ""
    text = ""
    size = -1
    for _ in range(10):
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) == size:
            break
        size = len(text)
        time.sleep(settle / 4)
    return text


def _run(args: list[str], timeout: float) -> str:
    """Run the game executable, wait for it to exit and return log.txt."""
    log_file = config.log_path()
    if log_file.exists():
        log_file.unlink()
    process = subprocess.Popen(args, cwd=str(config.game_dir()))
    deadline = time.time() + timeout
    while process.poll() is None and time.time() < deadline:
        time.sleep(0.25)
    if process.poll() is None:
        process.kill()
    process.wait()
    return _read_log()


def pretender_candidates(nation: gamedata.Nation, era: int | None = None) -> list[Path]:
    """Pretender files ``newlords`` offers for a nation, in slot order.

    ``file_name_base`` in nations.csv already carries the era prefix (e.g.
    ``early_tienchi``), so the files are ``early_tienchi_0.2h`` ...
    """
    folder = config.saved_games_dir() / "newlords"
    return sorted(folder.glob(f"{nation.file_name_base}_*.2h"))


def nations_with_pretenders(era: int) -> list[gamedata.Nation]:
    """Nations that have at least one stored pretender for ``era``."""
    result = []
    for nation in sorted(gamedata.nations().values(), key=lambda n: n.id):
        if nation.era == era and pretender_candidates(nation, era):
            result.append(nation)
    return result


def generate_map(game: str, provinces: int = 40, seapart: int = 0,
                 timeout: float = 180.0) -> Path:
    """Run ``--makemap`` and return the generated map file.

    ``--makemap NAME.map`` writes ``maps/NAME/NAME.map`` plus the packed
    ``NAME.d6m`` image, so the map name is the game name.  ``seapart`` is the
    percentage of sea provinces; a water nation can only play on a map that
    has some.
    """
    folder = config.maps_dir() / game
    if folder.exists():
        shutil.rmtree(folder)
    args = [
        _exe(), "--makemap", f"{game}.map",
        "--mapprov", str(provinces),
        "--riverpart", "0", "--seapart", str(seapart),
        *NEWGAME_FLAGS, "-d",
    ]
    log = _run(args, timeout)
    map_path = folder / f"{game}.map"
    if not map_path.exists():
        raise NewGameError(
            f"--makemap did not produce {map_path}\n{_excerpt(log)}"
        )
    return map_path


def _excerpt(text: str, limit: int = 700) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-limit // 60:])


def _graph(lines: list[str]) -> dict[int, set[int]]:
    edges: dict[int, set[int]] = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "#neighbour":
            try:
                a, b = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            edges.setdefault(a, set()).add(b)
            edges.setdefault(b, set()).add(a)
    return edges


def _sea_provinces(lines: list[str]) -> set[int]:
    """Provinces whose ``#terrain`` bitmask carries the sea flag (0x800000)."""
    out: set[int] = set()
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "#terrain":
            try:
                if int(parts[2]) & SEA_FLAG:
                    out.add(int(parts[1]))
            except ValueError:
                continue
    return out


def scenarize(map_path: Path, nation_a: int, nation_b: int,
              water_a: bool = False, water_b: bool = False) -> tuple[int, int]:
    """Strip rivers, check connectivity and make the map a two player scenario.

    Returns the two starting provinces (the farthest connected pair, so both
    capitals have room to grow).  A water nation only accepts a sea start, a
    land nation only a land one.
    """
    lines = map_path.read_text(encoding="utf-8", errors="replace").splitlines()
    kept = [line for line in lines if not RIVER_BORDER.match(line.strip())]
    lines = kept

    edges = _graph(lines)
    if not edges:
        raise NewGameError(f"{map_path} has no #neighbour lines")
    nodes = sorted(edges)
    sea = _sea_provinces(lines)

    def pick(water: bool) -> list[int]:
        pool = [node for node in nodes if (node in sea) == water]
        return pool or nodes

    start = pick(water_a)[0]
    dist = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in edges[current]:
            if nxt not in dist:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    missing = [node for node in nodes if node not in dist]
    if missing:
        raise NewGameError(
            f"{map_path}: province(s) {missing[:6]} are not connected to the map"
        )
    far = max(pick(water_b), key=lambda node: dist.get(node, -1))

    block = [
        "#scenario",
        "#victorycondition 0",
        f"#allowedplayer {nation_a}",
        f"#specstart {nation_a} {start}",
        f"#allowedplayer {nation_b}",
        f"#specstart {nation_b} {far}",
        f"#startwar {nation_a} {nation_b}",
    ]
    stripped = [
        line for line in lines
        if line.strip() != "#scenario" and not line.strip().startswith("#victorycondition")
    ]
    insert_at = next(
        (i for i, line in enumerate(stripped) if line.startswith("#neighbour")),
        len(stripped),
    )
    out = stripped[:insert_at] + block + stripped[insert_at:]
    map_path.write_bytes(("\n".join(out) + "\n").encode("utf-8"))
    return start, far


def assign_owners(map_path: Path, nation_a: int, nation_b: int,
                  water_a: bool = False, water_b: bool = False) -> int:
    """Give every province without an ``#owner`` to the nearer player.

    A freshly generated map leaves all provinces but the two capitals neutral,
    and the arena must not have neutral provinces: each side takes the
    provinces closest to its ``#specstart`` in the ``#neighbour`` graph.  Sea
    provinces go to the water nation and land provinces to the land nation;
    when both share a terrain the nearer one wins.
    Returns how many provinces were assigned.
    """
    lines = map_path.read_text(encoding="utf-8", errors="replace").splitlines()
    edges = _graph(lines)
    sea = _sea_provinces(lines)
    starts: dict[int, int] = {}
    owned: set[int] = set()
    for line in lines:
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            if parts[0] == "#specstart":
                starts[int(parts[1])] = int(parts[2])
            elif parts[0] == "#owner":
                owned.add(int(parts[1]))
        except ValueError:
            continue
    nodes = sorted(edges)
    if not nodes:
        return 0
    anchors = {
        nation_a: starts.get(nation_a, nodes[0]),
        nation_b: starts.get(nation_b, nodes[-1]),
    }
    water = {nation_a: water_a, nation_b: water_b}
    nearest: dict[int, tuple[int, int]] = {}
    for nation, anchor in anchors.items():
        dist = {anchor: 0}
        queue = deque([anchor])
        while queue:
            cur = queue.popleft()
            for nxt in edges.get(cur, ()):
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    queue.append(nxt)
        for node, d in dist.items():
            if node not in nearest or d < nearest[node][0]:
                nearest[node] = (d, nation)
    taken = owned | set(anchors.values())
    add = []
    for p in nodes:
        if p in taken:
            continue
        fits = [n for n in (nation_a, nation_b) if (p in sea) == water[n]]
        if not fits:
            fits = [nation_a, nation_b]
        if len(fits) == 1:
            owner = fits[0]
        else:
            owner = min(fits, key=lambda n: nearest.get(p, (99, n))[0])
        add.append(f"#owner {p} {owner}")
    if not add:
        return 0
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("#neighbour")),
        len(lines),
    )
    lines[insert_at:insert_at] = add
    map_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(add)


def _strip_god_password(data: bytes) -> bytes:
    """Replace the encoded password right after the game name with an empty one.

    God files saved in the GUI carry the password the player set, and a game
    created from them inherits it.  The field is a running-XOR string (key
    starts at 0x78, updated by adding each plaintext byte), followed by the
    encoded NUL and a literal 0x78 terminator; an empty password is just
    ``78 78``.  Removing bytes shifts the rest of the file, which the parser
    tolerates because strings are terminator-scanned.
    """
    pos = 38
    while pos < len(data):
        if data[pos] == 0x4F:
            pos += 1
            break
        pos += 1
    else:
        return data
    key = 0x78
    end = pos
    while end < len(data):
        plain = data[end] ^ key
        end += 1
        if plain == 0:
            break
        if not 32 <= plain < 127:
            return data
        key = (key + plain) & 0xFF
    else:
        return data
    if end >= len(data) or data[end] != 0x78:
        return data
    end += 1
    if end - pos <= 2:
        return data
    return data[:pos] + b"\x78\x78" + data[end:]


_COM_XOR = 0x4F
_COM_PATHS_OFFSET_IN_TAIL = 130   # 10-byte magic-path vector (F,A,W,E,S,D,N,G,B,H)


def _zero_com_magic_paths(data: bytearray) -> None:
    """Zero every commander record's 10-byte magic-path tail field.

    A pretender file carries the chosen magic paths inside each com record's
    181-byte tail.  The engine validates that those paths are legal for the
    nation that owns the god file — Asphodel's placeholder has e.g. Astral 7,
    which no other nation can pick.  Zeroing them is safe because the arena's
    real design is transplanted later (Phase 2/3 in :mod:`arena_build`).
    """
    pos = 0
    while pos < len(data) - 6:
        idx = data.find(b"\x4f", pos)
        if idx < 0:
            break
        if idx + 5 > len(data):
            break
        uid = struct.unpack_from("<I", data, idx + 1)[0]
        if not (0 < uid < 10_000_000):
            pos = idx + 1
            continue
        # Walk back to find a printable XOR-encoded name (2+ chars).
        name_end = idx
        name_start = name_end
        while name_start > 0:
            c = data[name_start - 1] ^ _COM_XOR
            if 32 <= c < 127:
                name_start -= 1
            else:
                break
        if name_end - name_start < 2:
            pos = idx + 1
            continue
        # Locate and zero the 10-byte path vector inside the 181-byte tail.
        paths_pos = idx + 5 + 24 + _COM_PATHS_OFFSET_IN_TAIL
        if paths_pos + 10 > len(data):
            pos = idx + 1
            continue
        data[paths_pos:paths_pos + 10] = b"\x00" * 10
        pos = idx + 1


def forge_god_file(source: Path, nation: int, out: Path) -> None:
    """Relabel a stored god file as ``nation`` and strip its password.

    The nation id sits at ``+26`` and again right before an ``ff ff ff ff``
    marker in the mid-file record.  Every com record's magic-path vector is
    also zeroed so the engine does not reject the design as nation-illegal
    (the arena's real paths are written later).  The trailing checksum is
    left stale; the ``create`` retry loop repairs it from the value the engine
    logs."""
    data = bytearray(_strip_god_password(source.read_bytes()))
    # Zero magic paths BEFORE editing: _strip_god_password may have shifted
    # bytes, so do it once here before any further mutation.
    _zero_com_magic_paths(data)
    old = struct.pack("<H", struct.unpack_from("<H", data, 26)[0])
    struct.pack_into("<H", data, 26, nation)
    pos = 0
    while True:
        pos = data.find(old + b"\xff\xff\xff\xff", pos)
        if pos < 0:
            break
        struct.pack_into("<H", data, pos, nation)
        pos += 2

    # The placeholder's chassis is mod-only: without that mod the engine sees
    # a god whose monster number it does not know and aborts game creation
    # with "king has bad mnr".  Retarget every chassis reference to a
    # pretender the target nation may legally take from the base data; the
    # real design replaces this placeholder after creation anyway.
    legal = sorted(gamedata.pretenders().get(nation, set()) & set(gamedata.units()))
    if legal:
        needle = struct.pack("<H", PLACEHOLDER_CHASSIS)
        pos = data.find(needle)
        while pos >= 0:
            struct.pack_into("<H", data, pos, legal[0])
            pos = data.find(needle, pos + 2)

    out.write_bytes(bytes(data))


def _repair_god_crc(log: str, sources: dict[str, Path]) -> bool:
    """Fix the trailing checksum of ``.2h`` files the engine rejected.

    The last two bytes of a pretender file are a checksum over everything
    before them, so any edit of the design (e.g. patching the nation id)
    invalidates it and the engine reports the god file as corrupted.  The
    engine logs the value it computed, so we take it from there and rewrite
    the file it was copied from (the save copy is recreated on the retry).
    """
    lines = log.splitlines()
    repaired = False
    for index, line in enumerate(lines):
        match = CRC_LINE.search(line)
        if not match or match.group(1) == match.group(2):
            continue
        name = None
        for back in range(index - 1, max(-1, index - 5), -1):
            if lines[back].strip().startswith("checkcrc:"):
                name = Path(lines[back].split(":", 1)[1].strip()).name
                break
        if name is None:
            continue
        source = sources.get(name)
        if source is None or not source.exists():
            continue
        data = bytearray(source.read_bytes())
        struct.pack_into("<H", data, len(data) - 2, int(match.group(1)))
        source.write_bytes(bytes(data))
        repaired = True
    return repaired


def create(game: str, era: int, sides: list[tuple[gamedata.Nation, Path]],
           timeout: float = 300.0, extra_flags: list[str] | None = None,
           mods: list[str] | None = None, indepstr: int = 0) -> str:
    """Create the two human player game, trying each available pretender slot.

    ``sides`` is a list of ``(nation, pretender file)`` pairs; the file is only
    used as the preferred slot, other slots are tried when a god is rejected
    by the legality check. ``extra_flags`` are appended to the ``--newgame``
    command line (e.g. ``--eventrarity 2`` to keep random events rare).
    ``--conqall`` is always passed, so every created game uses the
    conquer-all victory condition.
    ``mods`` enables mods (``dir/file.dm`` entries) instead of ``--nomods``.
    ``indepstr`` sets the independent strength: a higher value means larger
    garrisons and thus a larger unit table in ftherlnd.
    """
    choices = []
    newlords = config.saved_games_dir() / "newlords"
    for nation, preferred in sides:
        if preferred.exists() and preferred.parent != newlords:
            # An explicit god file (e.g. the arena's project placeholder) is
            # used on its own: it is not a design from savedgames/newlords,
            # so the folder is not even listed and there are no other slots
            # to fall back to.
            candidates = [preferred]
        else:
            candidates = pretender_candidates(nation, era)
            if preferred in candidates:
                candidates.remove(preferred)
                candidates.insert(0, preferred)
        if not candidates:
            raise NewGameError(
                f"{nation.name} has no pretender file: pass one explicitly or "
                f"store {ERA_PREFIX[era]}_{nation.file_name_base}_*.2h in "
                f"savedgames/newlords"
            )
        choices.append(candidates)

    combinations = list(itertools.product(*choices))[:8]
    last_log = ""
    for combo in combinations:
        sources = {f"{nation.file_name_base}.2h": source
                   for (nation, _), source in zip(sides, combo)}
        # Pre-strip every source so CRC repair targets the password-stripped
        # bytes (the engine computes its checksum after password stripping,
        # not on the raw file we forge_god_file produces).
        for name, source in sources.items():
            stripped = _strip_god_password(source.read_bytes())
            source.write_bytes(stripped)

        # Try up to one attempt per god file + 2 extra rounds.  Each engine
        # run reports at most one corrupted .2h (it aborts on the first bad
        # file it finds), so a 2-nation game needs up to 2 repair cycles.
        max_attempts = max(len(sources) + 1, 3)
        for attempt in range(max_attempts):
            save = config.save_dir(game)
            if save.exists():
                shutil.rmtree(save)
            save.mkdir(parents=True)
            for name, source in sources.items():
                (save / name).write_bytes(source.read_bytes())

            args = [
                _exe(), "--newgame", game, "--mapfile", f"{game}.map",
                "--era", str(era), "--startprov", "1", "--indepstr", str(indepstr),
                "--magicsites", "0", "--conqall", *NEWGAME_FLAGS, "-d",
                *config.mod_flags(mods), *(extra_flags or []), "-d",
            ]
            log = _run(args, timeout)
            last_log = log
            if (save / "ftherlnd").exists():
                return log
            # A patched god file fails its checksum; the engine logs the
            # correct value so repair and retry.  Keep looping until no more
            # CRC mismatches are found — the engine only ever reports one
            # corrupted file per run.
            if _repair_god_crc(log, sources):
                print(f"  repaired .2h checksum, retrying (attempt {attempt + 2})")
                continue
            break
        if not any(marker in log for marker in CHEAT_MARKERS):
            break

    raise NewGameError(
        "the game could not be created (no ftherlnd written)\n" + _excerpt(last_log)
    )


def apply_armies(game: str, arena: scenario.ResolvedArena,
                 starts: tuple[int, int]) -> list[dict]:
    """Write both sides' configured armies into the start provinces."""
    changes = []
    for side, province in zip((arena.attacker, arena.defender), starts):
        squads = [(count, unit.id) for count, unit in side.squads]
        changes.append(
            saveedit.inject_province_army(
                game, province, side.commander.id, squads
            )
        )
    return changes


def host_once(game: str, timeout: float = 180.0,
              mods: list[str] | None = None) -> tuple[str, bool]:
    """Host one turn so the engine regenerates every player's .trn."""
    from . import runner

    return runner.host_turn(game, timeout=timeout, mods=mods)


def trn_squads(game: str, nation: gamedata.Nation, era: int,
               province: int) -> list[tuple[int, int]]:
    """Read back the squad blocks of ``province`` from a player's .trn."""
    path = config.save_dir(game) / f"{nation.file_name_base}.trn"
    if not path.exists():
        return []
    raw = path.read_bytes()
    squads = []
    pos = 0
    while True:
        idx = raw.find(saveedit.SQUAD_PREFIX, pos)
        if idx < 0 or idx + 12 > len(raw):
            break
        unit_type, hp, p1, p2 = struct.unpack_from("<HHHH", raw, idx + 4)
        if 0 < unit_type < saveedit.MAX_UNIT_TYPE and p1 == p2 == province:
            squads.append((unit_type, hp))
        pos = idx + 1
    return squads


def random_scenario(era: int = 1, seed: int | None = None,
                    game: str = "Dom6Arena") -> scenario.Arena:
    """Build a random two human player scenario from stored pretenders."""
    rng = random.Random(seed)
    nations = nations_with_pretenders(era)
    if len(nations) < 2:
        raise NewGameError(
            f"need two nations with pretender files in era {era}, "
            f"found {[n.name for n in nations]}"
        )
    attacker, defender = rng.sample(nations, 2)
    troops = [
        unit for unit in gamedata.units().values()
        if unit.gold > 0 and 1 <= unit.id < 4000 and unit.resources > 0
        and "Pretender" not in unit.name
    ]
    if len(troops) < 4:
        raise NewGameError("not enough unit types to build a random army")

    def army() -> scenario.Army:
        picks = rng.sample(troops, rng.randint(1, 2))
        squads = [scenario.Squad(rng.randint(5, 20), unit.id) for unit in picks]
        commander = rng.choice(troops)
        return scenario.Army(commander=commander.id, squads=squads)

    return scenario.Arena(
        game=game,
        attacker=scenario.Side(nation=attacker.id, army=army()),
        defender=scenario.Side(nation=defender.id, army=army()),
        era=era,
    )


def write_scenario(arena: scenario.Arena, path: Path) -> Path:
    """Serialise an Arena to the JSON config format (generated configs)."""
    def ident(value):
        """Accept either a resolved object or a plain id."""
        return getattr(value, "id", value)

    def side(side_obj: scenario.Side) -> dict:
        return {
            "nation": ident(side_obj.nation),
            "army": {
                "commander": ident(side_obj.army.commander),
                "squads": [
                    {"count": squad.count, "unit": ident(squad.unit)}
                    for squad in side_obj.army.squads
                ],
            },
        }

    data = {
        "game": arena.game,
        "era": arena.era,
        "turns": arena.turns,
        "attacker": side(arena.attacker),
        "defender": side(arena.defender),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
