"""Command line interface: build maps, run battles, report results."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from . import config, gamedata, mapgen, newgame, report, runner, saveedit, scenario


def load_scenario(path: str) -> scenario.Arena:
    file = Path(path)
    if not file.is_file():
        raise SystemExit(f"scenario file not found: {path}")
    if file.suffix.lower() == ".json":
        import json

        with file.open(encoding="utf-8-sig") as handle:
            return scenario.from_dict(json.load(handle))
    spec = importlib.util.spec_from_file_location(f"scenario_{file.stem}", file)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    arena = getattr(module, "ARENA", None)
    if arena is None and hasattr(module, "build"):
        arena = module.build()
    if not isinstance(arena, scenario.Arena):
        raise SystemExit(f"{path} must define ARENA = Arena(...) or a build() function")
    return arena


def cmd_build(args: argparse.Namespace) -> int:
    arena = scenario.resolve(load_scenario(args.scenario))
    map_path, tga_path = mapgen.write_map(arena)
    print(f"map written: {map_path}")
    print(f"image copied: {tga_path}")
    print()
    print("Create the game without the GUI, then host it:")
    print(f"  1. python -m dom6arena newgame {args.scenario}")
    print(f"  2. python -m dom6arena run {args.scenario} --runs {args.runs}")
    return 0


def cmd_newgame(args: argparse.Namespace) -> int:
    """Create a two human player game on a river-free map and set both armies."""
    attempts = 1 if args.scenario else 3
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return _newgame_once(args, attempt)
        except newgame.NewGameError as error:
            last = error
            print(f"attempt {attempt + 1} failed: {error}")
    raise last  # type: ignore[misc]


def _newgame_once(args: argparse.Namespace, attempt: int) -> int:
    if args.scenario:
        arena = scenario.resolve(load_scenario(args.scenario))
    else:
        seed = None if args.seed is None else args.seed + attempt * 1000
        raw = newgame.random_scenario(
            era=args.era, seed=seed, game=args.game or "Dom6ArenaRandom"
        )
        path = newgame.write_scenario(
            raw, config.ensure_output_dir() / f"{raw.game}_scenario.json"
        )
        print(f"generated scenario config: {path}")
        arena = scenario.resolve(raw)

    game = arena.game
    print(f"map: generating '{game}' with {args.provinces} land provinces, no rivers ...")
    map_path = newgame.generate_map(game, provinces=args.provinces, timeout=args.timeout)
    starts = newgame.scenarize(
        map_path, arena.attacker.nation.id, arena.defender.nation.id
    )
    print(f"map written: {map_path}")
    print(
        f"starts: {arena.attacker.nation.name} -> province {starts[0]}, "
        f"{arena.defender.nation.name} -> province {starts[1]}"
    )

    sides = []
    for side in arena.sides:
        candidates = newgame.pretender_candidates(side.nation, arena.era)
        if not candidates:
            print(
                f"no pretender file for {side.nation.name}: run the client once and "
                f"save a god for that nation (savedgames/newlords)"
            )
            return 1
        sides.append((side.nation, candidates[0]))

    print(f"creating two human players ({', '.join(n.name for n, _ in sides)}) ...")
    newgame.create(game, arena.era, sides, timeout=args.timeout)
    save = config.save_dir(game)
    turns = sorted(path.name for path in save.glob("*.trn"))
    print(f"game created: {save}")
    print(f"turn files: {', '.join(turns) or 'none'}")

    print("writing configured armies ...")
    changes = newgame.apply_armies(game, arena, starts)
    for side, change in zip(arena.sides, changes):
        print(
            f"  {side.nation.name} (province {change['province']}): "
            f"commander {change['commander_type']}, "
            f"{change['applied']}/{change['requested']} configured unit(s) written "
            f"across {change['unit_records']} unit record(s), "
            f"composition {change['composition']}"
        )

    if not args.no_host:
        print("hosting one turn to regenerate every .trn ...")
        text, game_over = newgame.host_once(game, timeout=args.timeout)
        ok = "hostack 1" in text or "put turn data" in text
        print(f"  host {'advanced' if ok else 'finished'}"
              f"{' (game over)' if game_over else ''}")
        for side, province in zip(arena.sides, starts):
            squads = newgame.trn_squads(game, side.nation, arena.era, province)
            print(
                f"  {side.nation.name} .trn squads in province {province}: "
                f"{[(unit_type, hp) for unit_type, hp in squads]}"
            )

    if not args.scenario:
        print(f"config file: {config.OUTPUT_DIR / f'{game}_scenario.json'}")
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    arena = scenario.resolve(load_scenario(args.scenario))
    mapgen.write_map(arena)
    print(f"trying scripted --newgame for {arena.game} ...")
    ok, log = runner.create_game(arena, extra_flags=args.extra, timeout=args.timeout)
    print(f"save created: {ok}")
    if not ok:
        print("the game did not create a save; use the GUI flow described by `build`")
        return 1
    print("note: a scripted game normally ends immediately because Dominions 6 needs a")
    print("human player who owns a pretender; check `run` output before trusting it")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    raw = load_scenario(args.scenario)
    if args.game:
        raw.game = args.game
    arena = scenario.resolve(raw)
    game = arena.game

    save_path = config.save_dir(game)
    if not (save_path / "ftherlnd").exists():
        print(f"no game save at {save_path}")
        print(f"create it with the map '{game}.map' first (see `python -m dom6arena build ...`)")
        return 1

    runs = args.runs
    turns = args.turns or arena.turns
    print(f"hosting {game}: {runs} run(s), up to {turns} turn(s) each")
    results = runner.simulate(arena, game, runs=runs, max_turns=turns)
    summary = report.summarise(arena, results)
    report.print_summary(summary)
    files = report.write_files(arena, summary)
    print()
    print("written:", ", ".join(files))
    return 0


def cmd_inject(args: argparse.Namespace) -> int:
    """Inject army compositions from a scenario into a save's ftherlnd."""
    arena = scenario.resolve(load_scenario(args.scenario))
    game = args.game or arena.game

    save_path = config.save_dir(game)
    if not (save_path / "ftherlnd").exists():
        print(f"no game save at {save_path}")
        return 1

    print(f"injecting armies into {game} ...")
    results = saveedit.inject_scenario(game, arena)
    for r in results:
        side = "attacker" if r["nation"] == arena.attacker.nation.name else "defender"
        print(
            f"  {side} {r['nation']}: commander->{r['commander_type']} "
            f"({'ok' if r['commander_set'] else 'not found'}), "
            f"{r['troops']} troop(s) written "
            f"(capacity {r['capacity']})"
        )

    if args.host:
        print(f"hosting {game} ...")
        text, game_over = runner.host_turn(game)
        print(f"host advanced: {not game_over}")
        if game_over:
            print("warning: game over reported")

    if args.verify:
        for side in (arena.attacker, arena.defender):
            squads = saveedit.read_squads(game, side.nation.name)
            print(f"  {side.nation.name} roster: {squads}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    arena = scenario.resolve(load_scenario(args.scenario))
    game = args.game or arena.game
    results = []
    logs = config.OUTPUT_DIR / "logs"
    if not logs.is_dir():
        print(f"no captured logs in {logs}; run `python -m dom6arena run ...` first")
        return 1
    from . import battlelog

    index = 0
    for path in sorted(logs.glob(f"{game}_turn*.txt")):
        index += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        scan = battlelog.scan(text)
        turn = int(path.stem.rsplit("turn", 1)[-1])
        results.append(
            runner.RunResult(
                run=index,
                game=path.stem.rsplit("_turn", 1)[0],
                turns=[runner.TurnLog(turn=turn, text=text, battles=scan.battles, game_over=False)],
            )
        )
    summary = report.summarise(arena, results)
    report.print_summary(summary)
    files = report.write_files(arena, summary)
    print()
    print("written:", ", ".join(files))
    return 0


def cmd_view(args: argparse.Namespace) -> int:
    print("Dominions writes per unit battle arrays to log.txt only when a battle")
    print("replay is opened in the client, so:")
    print(f"  1. start dominions6.exe and open the game '{args.game}'")
    print("  2. click the province where the battle happened and choose View Battle")
    print("  3. quit the client")
    print(f"  4. run: python -m dom6arena report <scenario> --game {args.game}")
    return 0


def cmd_nations(args: argparse.Namespace) -> int:
    for nation in sorted(gamedata.nations().values(), key=lambda n: n.id):
        if args.era is not None and nation.era != args.era:
            continue
        if args.search and args.search.lower() not in nation.name.lower():
            continue
        print(f"{nation.id:5d}  era {nation.era}  {nation.name:24} {nation.epithet}")
    return 0


def cmd_units(args: argparse.Namespace) -> int:
    for unit in sorted(gamedata.units().values(), key=lambda u: u.id):
        if args.search and args.search.lower() not in unit.name.lower():
            continue
        print(f"{unit.id:6d}  {unit.gold:5d}g {unit.resources:5d}r  {unit.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dom6arena",
        description="Scripted Dominions 6 battles on a small arena map.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="write the arena map for a scenario")
    build.add_argument("scenario")
    build.add_argument("--runs", type=int, default=5, help="runs suggested in the printed steps")
    build.set_defaults(func=cmd_build)

    ng = sub.add_parser(
        "newgame",
        help="create a two human player game on a river-free map and set both armies",
    )
    ng.add_argument("scenario", nargs="?", help="JSON/Python scenario (omit with --seed for a random one)")
    ng.add_argument("--game", default=None, help="game name for a generated scenario")
    ng.add_argument("--era", type=int, default=1)
    ng.add_argument("--seed", type=int, default=None)
    ng.add_argument("--provinces", type=int, default=40)
    ng.add_argument("--timeout", type=float, default=300.0)
    ng.add_argument("--no-host", action="store_true", help="skip the first host")
    ng.set_defaults(func=cmd_newgame)

    prepare = sub.add_parser("prepare", help="try the scripted --newgame route")
    prepare.add_argument("scenario")
    prepare.add_argument("--timeout", type=float, default=240.0)
    prepare.add_argument("--extra", nargs=argparse.REMAINDER, default=[])
    prepare.set_defaults(func=cmd_prepare)

    run = sub.add_parser("run", help="clone the game and host battles")
    run.add_argument("scenario")
    run.add_argument("--game", help="save name to clone (default: scenario game)")
    run.add_argument("--runs", type=int, default=5)
    run.add_argument("--turns", type=int, default=None)
    run.set_defaults(func=cmd_run)

    inject = sub.add_parser("inject", help="patch a save's ftherlnd with scenario armies")
    inject.add_argument("scenario")
    inject.add_argument("--game", default=None, help="save name to patch (default: scenario game)")
    inject.add_argument("--host", action="store_true", help="host one turn after injecting")
    inject.add_argument("--verify", action="store_true", help="print nation rosters after injection")
    inject.set_defaults(func=cmd_inject)

    rep = sub.add_parser("report", help="re-parse already captured logs")
    rep.add_argument("scenario")
    rep.add_argument("--game", default=None)
    rep.set_defaults(func=cmd_report)

    view = sub.add_parser("view", help="how to dump per unit battle data")
    view.add_argument("game")
    view.set_defaults(func=cmd_view)

    nations = sub.add_parser("nations", help="list nations")
    nations.add_argument("--era", type=int, default=None)
    nations.add_argument("--search", default=None)
    nations.set_defaults(func=cmd_nations)

    units = sub.add_parser("units", help="list units")
    units.add_argument("--search", default=None)
    units.set_defaults(func=cmd_units)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (
        scenario.ScenarioError,
        runner.RunnerError,
        newgame.NewGameError,
        FileNotFoundError,
        ValueError,
        KeyError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
