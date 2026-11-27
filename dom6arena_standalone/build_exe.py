"""Build the standalone Windows exe: ``python build_exe.py``.

Produces ``dist/Dom6Arena.exe`` -- a single file that runs without Python
installed.  It is a console build on purpose: the arena build asks about
battle reports on stdin, and the config window passes that console on to the
build it starts.

Assets are bundled read-only (``data``, ``resources``).  On first run the exe
copies ``arena_config.json``, the arena map and the shipped mods next to
itself / into the Dominions 6 user folder, so the config stays a plain file
the user can edit.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "Dom6Arena"

ARGS = [
    str(ROOT / "dom6arena_exe.py"),
    "--name", NAME,
    "--onefile",
    "--console",
    "--noconfirm",
    "--clean",
    "--distpath", str(ROOT / "dist"),
    "--workpath", str(ROOT / "build"),
    "--specpath", str(ROOT / "build"),
    "--add-data", f"{ROOT / 'data'};data",
    "--add-data", f"{ROOT / 'resources'};resources",
    "--add-data", f"{ROOT / 'arena_config.json'};.",
    "--exclude-module", "pytest",
]


def main() -> int:
    deploy = "--deploy" in sys.argv[1:]
    code = subprocess.call([sys.executable, "-m", "PyInstaller", *ARGS])
    if code:
        return code
    exe = ROOT / "dist" / f"{NAME}.exe"
    if not exe.is_file():
        print(f"build finished but {exe} is missing", file=sys.stderr)
        return 1
    # The config lives next to the exe so it survives rebuilds and is edited
    # by hand or by the GUI; the copy inside the exe is only a template.
    config = ROOT / "dist" / "arena_config.json"
    write_config(config)
    print(f"built {exe} ({exe.stat().st_size // 1024} KB)")
    print(f"config {config}")
    if deploy:
        return deploy_beside_game(exe)
    return 0


def game_folder() -> Path | None:
    """The Dominions 6 install this checkout belongs to, if any."""
    return next((folder for folder in (ROOT.parent, ROOT, ROOT.parent.parent)
                 if (folder / "dominions6.exe").is_file()), None)


def deploy_beside_game(exe: Path) -> int:
    """Copy the exe and its config next to ``dominions6.exe``.

    Run from the game folder the config needs no ``game_dir`` at all: the exe
    is found by the program's own upward search starting at its own folder,
    which also survives the install being moved or copied to another drive.
    """
    game = game_folder()
    if game is None:
        print("--deploy: no dominions6.exe found above this folder", file=sys.stderr)
        return 1
    target_exe = game / f"{NAME}.exe"
    shutil.copyfile(exe, target_exe)
    target_cfg = game / "arena_config.json"
    write_config(target_cfg, bare=True)
    print(f"deployed {target_exe}")
    print(f"deployed {target_cfg} (no game_dir: auto-detected)")
    return 0


def write_config(target: Path, bare: bool = False) -> None:
    """Copy the project config and retarget ``game_dir`` at this layout.

    The project config says ``../Dominions6.exe`` because the checkout sits
    inside the install; ``dist/`` is one level deeper, so the same relative
    path would miss.  ``bare`` drops the key entirely for a config that sits
    beside ``dominions6.exe``, where auto-detection is exact.
    """
    shutil.copyfile(ROOT / "arena_config.json", target)
    game = game_folder()
    cfg = json.loads(target.read_text(encoding="utf-8"))
    if bare or game is None:
        cfg.pop("game_dir", None)
    else:
        rel = os.path.relpath(game / "dominions6.exe", target.parent)
        cfg["game_dir"] = rel.replace(os.sep, "/")
    target.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
