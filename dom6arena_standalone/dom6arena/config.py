"""Filesystem locations of the Dominions 6 installation and this project.

Two roots are kept apart so a frozen (PyInstaller) build behaves like the
source checkout:

``BUNDLE_DIR``  read-only assets shipped with the program (``data``,
                ``resources``).  Inside a one-file exe this is the temporary
                extraction folder, so nothing may be written there.
``APP_DIR``     where the user's files live: ``arena_config.json`` and
                ``output``.  This is the folder holding the exe when frozen,
                and the source checkout otherwise.
"""

from __future__ import annotations

import os
import shutil
import sys
from functools import lru_cache
from pathlib import Path

FROZEN = bool(getattr(sys, 'frozen', False))

BUNDLE_DIR = (Path(sys._MEIPASS) if FROZEN else Path(__file__).resolve().parent.parent)
APP_DIR = (Path(sys.executable).resolve().parent if FROZEN else BUNDLE_DIR)

# Kept under the old name: it is the read-only asset root in both modes.
PROJECT_ROOT = BUNDLE_DIR
ASSETS_DIR = BUNDLE_DIR / "assets"
DATA_DIR = BUNDLE_DIR / "data"
OUTPUT_DIR = APP_DIR / "output"
CONFIG_PATH = APP_DIR / "arena_config.json"
RESOURCES_DIR = BUNDLE_DIR / "resources"

EXE_NAME = "dominions6.exe"

_GAME_DIR: Path | None = None


def set_game_dir(path: str | Path | None) -> None:
    """Point the engine lookup at ``path`` (a Dominions 6 folder or the exe).

    ``arena_config.json`` uses this so a non-Steam-standard install (e.g.
    ``D:\\Steam\\...``) needs no ``DOM6_DIR`` environment variable.  Relative
    paths are resolved against ``APP_DIR``: the folder holding the exe when
    frozen, the source checkout otherwise.  A path that does not contain
    ``dominions6.exe`` is reported and then ignored, so a config copied
    between layouts still falls back to auto-detection instead of failing.
    """
    global _GAME_DIR
    _GAME_DIR = None
    if path:
        p = Path(str(path)).expanduser()
        if not p.is_absolute():
            p = APP_DIR / p
        p = p.resolve()
        folder = p.parent if p.suffix.lower() == ".exe" else p
        if (folder / EXE_NAME).is_file():
            _GAME_DIR = folder
        else:
            print(f"warning: game_dir {p} has no {EXE_NAME}; "
                  f"searching the usual install locations instead",
                  file=sys.stderr)
    game_dir.cache_clear()


def _candidates() -> list[Path]:
    env = os.environ.get("DOM6_DIR")
    candidates = [Path(env)] if env else []
    if _GAME_DIR is not None:
        candidates.insert(0, _GAME_DIR)
    # Walking up from the exe covers a build run from a dist/ subfolder as
    # well as the project-inside-the-install layout.
    here = APP_DIR
    for _ in range(4):
        candidates.append(here)
        if here.parent == here:
            break
        here = here.parent
    candidates += [
        Path(r"C:\Steam\steamapps\common\Dominions6"),
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Dominions6"),
        Path(r"C:\Program Files\Steam\steamapps\common\Dominions6"),
    ]
    return candidates


@lru_cache(maxsize=1)
def game_dir() -> Path:
    """Directory that holds dominions6.exe (also the cwd used when hosting)."""
    for candidate in _candidates():
        if (candidate / EXE_NAME).is_file():
            return candidate
    raise FileNotFoundError(
        "Could not find dominions6.exe. Set the DOM6_DIR environment "
        "variable or the game_dir entry of arena_config.json."
    )


@lru_cache(maxsize=1)
def appdata_dir() -> Path:
    """Dominions 6 user directory that contains savedgames/ and maps/."""
    env = os.environ.get("DOM6_APPDATA")
    if env:
        return Path(env)
    roaming = os.environ.get("APPDATA")
    if roaming:
        return Path(roaming) / "Dominions6"
    return Path.home() / ".dominions6"


def saved_games_dir() -> Path:
    return appdata_dir() / "savedgames"


def maps_dir() -> Path:
    return appdata_dir() / "maps"


def save_dir(game: str) -> Path:
    return saved_games_dir() / game


def log_path() -> Path:
    """log.txt is rewritten in the install directory on every host."""
    return game_dir() / "log.txt"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def mods_dir() -> Path:
    return appdata_dir() / "mods"


def workshop_dir() -> Path:
    """Steam workshop content folder for Dominions 6 (may not exist).

    The engine loads subscribed mods from here directly, so a save that names
    one is reproducible as long as the subscription is present.
    """
    return game_dir().resolve().parents[1] / "workshop" / "content" / "2511500"


def mod_flags(mods: list[str] | None) -> list[str]:
    """CLI arguments that enable ``mods`` (``dir/file.dm`` entries), else --nomods."""
    if not mods:
        return ["--nomods"]
    flags: list[str] = []
    for mod in mods:
        flags += ["-M", mod]
    return flags


def ensure_runtime_assets() -> None:
    """First-run setup for the frozen exe.

    The engine loads maps and mods from the user's Dominions 6 folder, not
    from the program, so the copies shipped inside the exe are staged there
    when they are missing.  An existing file is never overwritten -- a user
    edited map or mod stays as it is.  ``arena_config.json`` is copied out
    of the bundle on first run so it can be edited and kept across rebuilds.
    """
    if not FROZEN:
        return
    for kind, target in (("maps", maps_dir()), ("mods", mods_dir())):
        source = RESOURCES_DIR / kind
        if not source.is_dir():
            continue
        target.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            destination = target / item.name
            if destination.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, destination)
            else:
                shutil.copyfile(item, destination)
    if not CONFIG_PATH.exists():
        template = BUNDLE_DIR / "arena_config.json"
        if template.is_file():
            shutil.copyfile(template, CONFIG_PATH)
