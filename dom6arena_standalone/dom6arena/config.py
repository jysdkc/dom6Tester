"""Filesystem locations of the Dominions 6 installation and this project."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
SCENARIO_DIR = PROJECT_ROOT / "scenarios"
OUTPUT_DIR = PROJECT_ROOT / "output"

EXE_NAME = "dominions6.exe"

_GAME_DIR: Path | None = None


def set_game_dir(path: str | Path | None) -> None:
    """Point the engine lookup at ``path`` (a Dominions 6 folder or the exe).

    ``arena_config.json`` uses this so a non-Steam-standard install (e.g.
    ``D:\\Steam\\...``) needs no ``DOM6_DIR`` environment variable.  Relative
    paths are resolved against the project root, which lets the project live
    inside the install folder and refer to it as ``../Dominions6.exe``.
    Passing ``None`` clears the override and falls back to the environment
    variable and the default install locations.
    """
    global _GAME_DIR
    _GAME_DIR = None
    if path:
        p = Path(str(path)).expanduser()
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        p = p.resolve()
        folder = p.parent if p.suffix.lower() == ".exe" else p
        if not (folder / EXE_NAME).is_file():
            raise FileNotFoundError(
                f"game_dir {p} does not contain {EXE_NAME}"
            )
        _GAME_DIR = folder
    game_dir.cache_clear()


def _candidates() -> list[Path]:
    env = os.environ.get("DOM6_DIR")
    candidates = [Path(env)] if env else []
    if _GAME_DIR is not None:
        candidates.insert(0, _GAME_DIR)
    candidates += [
        PROJECT_ROOT,
        PROJECT_ROOT.parent,
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


def mod_flags(mods: list[str] | None) -> list[str]:
    """CLI arguments that enable ``mods`` (``dir/file.dm`` entries), else --nomods."""
    if not mods:
        return ["--nomods"]
    flags: list[str] = []
    for mod in mods:
        flags += ["-M", mod]
    return flags
