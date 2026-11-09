"""Create, clone and host Dominions 6 games, capturing log.txt for each turn."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import battlelog, config
from .scenario import ResolvedArena

# --textonly is required: without it the host opens a window and blocks forever
# on modal screens (e.g. "Game Over!") instead of exiting after the turn.
HOST_FLAGS = ["--nosteam", "--nopopups", "--textonly"]
GAME_OVER = "Game Over!"


class RunnerError(RuntimeError):
    pass


@dataclass
class TurnLog:
    turn: int
    text: str
    battles: list[battlelog.Battle]
    game_over: bool


@dataclass
class RunResult:
    run: int
    game: str
    turns: list[TurnLog] = field(default_factory=list)
    error: str | None = None

    @property
    def battles(self) -> list[battlelog.Battle]:
        return [battle for turn in self.turns for battle in turn.battles]


def _exe() -> str:
    return str(config.game_dir() / config.EXE_NAME)


def _read_log(settle: float = 0.4) -> str:
    path = config.log_path()
    if not path.exists():
        return ""
    size = -1
    text = ""
    for _ in range(10):
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) == size:
            break
        size = len(text)
        time.sleep(settle / 4)
    return text


def _ftherlnd(game: str) -> Path:
    return config.save_dir(game) / "ftherlnd"


def host_turn(game: str, timeout: float = 180.0,
              mods: list[str] | None = None) -> tuple[str, bool]:
    """Host one turn of ``game``; returns (log text, game_over)."""
    ftherlnd = _ftherlnd(game)
    if not ftherlnd.exists():
        raise RunnerError(f"{game}: no ftherlnd in {config.save_dir(game)}")
    before = ftherlnd.stat().st_mtime

    log_file = config.log_path()
    if log_file.exists():
        log_file.unlink()

    process = subprocess.Popen(
        [_exe(), "-g", game, "-d", *HOST_FLAGS, *config.mod_flags(mods)],
        cwd=str(config.game_dir())
    )
    deadline = time.time() + timeout
    advanced = False
    try:
        # Wait for the host to finish on its own: it rewrites ftherlnd
        # progressively, so killing it as soon as the mtime changes leaves a
        # truncated save behind.
        while time.time() < deadline and process.poll() is None:
            time.sleep(0.25)
        advanced = (process.poll() is not None and ftherlnd.exists()
                    and ftherlnd.stat().st_mtime != before)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()

    text = _read_log()
    return text, (GAME_OVER in text and not advanced)


def clone_game(template: str, target: str, overwrite: bool = True) -> Path:
    source = config.save_dir(template)
    destination = config.save_dir(target)
    if not source.is_dir():
        raise RunnerError(f"template game {template!r} does not exist at {source}")
    if destination.exists():
        if not overwrite:
            raise RunnerError(f"{destination} already exists")
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return destination


def wait_for_game(game: str, timeout: float = 0.0) -> bool:
    """Wait until a save directory exists (the GUI creates it)."""
    path = config.save_dir(game)
    deadline = time.time() + timeout
    while True:
        if (path / "ftherlnd").exists():
            return True
        if timeout and time.time() > deadline:
            return False
        time.sleep(1.0)


def create_game(arena: ResolvedArena, extra_flags: list[str] | None = None,
                timeout: float = 240.0) -> tuple[bool, str]:
    """Try the scripted ``--newgame`` route.

    Dominions 6 needs a human player slot with a pretender for a game to keep
    running, so this route usually only produces a game that ends immediately.
    It is kept for the cases where it does work and to inspect the failure.
    """
    save = config.save_dir(arena.game)
    if save.exists():
        shutil.rmtree(save)
    log_file = config.log_path()
    if log_file.exists():
        log_file.unlink()

    args = [
        _exe(), "--newgame", arena.game, "--mapfile", f"{arena.game}.map",
        "--era", str(arena.era), "--startprov", "1", "--indepstr", "0",
        "--magicsites", "0", "--conqall", *HOST_FLAGS, "-d",
    ] + (extra_flags or [])
    process = subprocess.Popen(args, cwd=str(config.game_dir()))
    deadline = time.time() + timeout
    while time.time() < deadline and process.poll() is None:
        time.sleep(0.25)
    if process.poll() is None:
        process.kill()
    process.wait()

    text = _read_log()
    ok = (save / "ftherlnd").exists()
    return ok, text


def simulate(arena: ResolvedArena, template: str, runs: int, max_turns: int,
             verbose: bool = True) -> list[RunResult]:
    """Clone ``template`` ``runs`` times and host until a battle happens."""
    results: list[RunResult] = []
    for index in range(1, runs + 1):
        game = f"{template}_{index}"
        result = RunResult(run=index, game=game)
        try:
            clone_game(template, game)
            for turn in range(1, max_turns + 1):
                text, game_over = host_turn(game)
                scan = battlelog.scan(text)
                result.turns.append(
                    TurnLog(turn=turn, text=text, battles=scan.battles, game_over=game_over)
                )
                if verbose:
                    status = f"{len(scan.battles)} battle(s)" if scan.battles else "no battle"
                    extra = " | GAME OVER" if game_over else ""
                    print(f"  {game} turn {turn}: {status}{extra}", flush=True)
                if scan.battles or game_over:
                    break
        except (RunnerError, OSError) as error:
            result.error = str(error)
            if verbose:
                print(f"  {game}: {error}", flush=True)
        results.append(result)

    _dump_logs(results)
    return results


def _dump_logs(results: list[RunResult]) -> None:
    logs = config.ensure_output_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    for result in results:
        for turn in result.turns:
            path = logs / f"{result.game}_turn{turn.turn}.txt"
            with path.open("w", encoding="utf-8", errors="replace") as handle:
                handle.write(turn.text)


def clean(game_prefix: str) -> int:
    """Delete cloned simulation games (keeps the template)."""
    removed = 0
    for path in config.saved_games_dir().iterdir():
        if path.is_dir() and path.name.startswith(game_prefix + "_"):
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
    return removed
