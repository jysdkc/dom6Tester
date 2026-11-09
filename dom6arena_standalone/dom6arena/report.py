"""Aggregate hosted battles into win rates and unit loss statistics."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field

from . import battlelog, config, gamedata
from .runner import RunResult
from .scenario import ResolvedArena, ResolvedSide

ATTACKER = "attacker"
DEFENDER = "defender"
UNKNOWN = "unknown"


@dataclass
class BattleOutcome:
    run: int
    turn: int
    province: int | None
    winner: str
    detailed: bool = False
    losses: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def loser(self) -> str:
        if self.winner == ATTACKER:
            return DEFENDER
        if self.winner == DEFENDER:
            return ATTACKER
        return UNKNOWN


def _winner(arena: ResolvedArena, battle: battlelog.Battle) -> str:
    # Host log player numbers are the nation ids (0 = independents).
    if battle.winner_id == arena.attacker.nation.id:
        return ATTACKER
    if battle.winner_id == arena.defender.nation.id:
        return DEFENDER
    if battle.has_unit_data:
        attack_left = sum(battle.counts(ATTACKER, "after").values())
        defend_left = sum(battle.counts(DEFENDER, "after").values())
        if attack_left and not defend_left:
            return ATTACKER
        if defend_left and not attack_left:
            return DEFENDER
    return UNKNOWN


def collect(arena: ResolvedArena, results: list[RunResult]) -> list[BattleOutcome]:
    outcomes: list[BattleOutcome] = []
    for result in results:
        for turn in result.turns:
            for battle in turn.battles:
                outcomes.append(
                    BattleOutcome(
                        run=result.run,
                        turn=turn.turn,
                        province=battle.province,
                        winner=_winner(arena, battle),
                        detailed=battle.has_unit_data,
                        losses={
                            ATTACKER: battle.losses(ATTACKER),
                            DEFENDER: battle.losses(DEFENDER),
                        },
                    )
                )
    return outcomes


def _side_label(side: ResolvedSide) -> str:
    kind = "AI" if side.ai is not None else "human"
    return f"{side.nation.name} ({kind})"


def _unit_costs(side: ResolvedSide) -> dict[str, tuple[int, int]]:
    costs = {
        unit.name: (unit.gold, unit.resources) for _, unit in side.squads
    }
    costs.setdefault(side.commander.name, (side.commander.gold, side.commander.resources))
    return costs


def _average_losses(arena: ResolvedArena, outcomes: list[BattleOutcome]) -> dict[str, dict]:
    sides = {ATTACKER: arena.attacker, DEFENDER: arena.defender}
    totals: dict[str, dict[str, int]] = {}
    for kind, side in sides.items():
        costs = _unit_costs(side)
        merged: dict[str, int] = {}
        for outcome in outcomes:
            for unit, lost in outcome.losses.get(kind, {}).items():
                merged[unit] = merged.get(unit, 0) + lost
        totals[kind] = {
            unit: {
                "deaths": lost,
                "gold": lost * costs.get(unit, (0, 0))[0],
                "resources": lost * costs.get(unit, (0, 0))[1],
            }
            for unit, lost in sorted(merged.items())
        }
    return totals


def summarise(arena: ResolvedArena, results: list[RunResult]) -> dict:
    outcomes = collect(arena, results)
    wins = {ATTACKER: 0, DEFENDER: 0, UNKNOWN: 0}
    for outcome in outcomes:
        wins[outcome.winner] = wins.get(outcome.winner, 0) + 1

    total = len(outcomes)
    detailed = [outcome for outcome in outcomes if outcome.detailed]
    return {
        "game": arena.game,
        "attacker": _side_label(arena.attacker),
        "defender": _side_label(arena.defender),
        "runs": len(results),
        "failed_runs": [result.game for result in results if result.error],
        "no_battle_runs": [result.game for result in results if not result.battles and not result.error],
        "battles": total,
        "wins": wins,
        "win_rate": {
            ATTACKER: round(wins[ATTACKER] / total, 3) if total else 0.0,
            DEFENDER: round(wins[DEFENDER] / total, 3) if total else 0.0,
        },
        "losses": _average_losses(arena, detailed) if detailed else {},
        "outcomes": [
            {
                "run": outcome.run,
                "turn": outcome.turn,
                "province": outcome.province,
                "winner": outcome.winner,
                "detailed": outcome.detailed,
                "losses": outcome.losses,
            }
            for outcome in outcomes
        ],
    }


def write_files(arena: ResolvedArena, summary: dict) -> list[str]:
    output = config.ensure_output_dir()
    json_path = output / f"report_{arena.game}.json"
    with json_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, indent=2, ensure_ascii=False))

    csv_path = output / f"report_{arena.game}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run", "turn", "province", "winner", "loser", "detailed", "side", "unit", "deaths"])
        for outcome in summary["outcomes"]:
            for side, units in outcome["losses"].items():
                if not units:
                    writer.writerow([outcome["run"], outcome["turn"], outcome["province"],
                                     outcome["winner"], "unknown" if outcome["winner"] == UNKNOWN else
                                     (DEFENDER if outcome["winner"] == ATTACKER else ATTACKER),
                                     outcome["detailed"], side, "", 0])
                for unit, deaths in units.items():
                    writer.writerow([outcome["run"], outcome["turn"], outcome["province"],
                                     outcome["winner"], "unknown", outcome["detailed"], side, unit, deaths])
    return [str(json_path), str(csv_path)]


def print_summary(summary: dict) -> None:
    print()
    print(f"=== {summary['game']} ===")
    print(f"attacker: {summary['attacker']}")
    print(f"defender: {summary['defender']}")
    print(f"runs: {summary['runs']}, battles: {summary['battles']}")
    if summary["failed_runs"]:
        print(f"failed runs: {', '.join(summary['failed_runs'])}")
    if summary["no_battle_runs"]:
        print(f"runs without a battle: {', '.join(summary['no_battle_runs'])}")

    wins = summary["wins"]
    if summary["battles"]:
        print()
        print(f"{'result':10} {'count':>5} {'rate':>7}")
        for key in (ATTACKER, DEFENDER, UNKNOWN):
            count = wins.get(key, 0)
            rate = count / summary["battles"]
            print(f"{key:10} {count:5d} {rate:6.0%}")
        print()
        print("per battle:")
        for outcome in summary["outcomes"]:
            province = outcome["province"] if outcome["province"] is not None else "?"
            detail = "with unit losses" if outcome["detailed"] else "winner only"
            print(f"  run {outcome['run']} turn {outcome['turn']} province {province}: "
                  f"{outcome['winner']} wins ({detail})")

    if summary["losses"]:
        print()
        for side, units in summary["losses"].items():
            if not units:
                continue
            print(f"{side} losses (total over {len([o for o in summary['outcomes'] if o['detailed']])} logged battles):")
            for unit, stats in units.items():
                print(f"  {unit:32} {stats['deaths']:5d} dead  {stats['gold']:6d}g  {stats['resources']:6d}r")
    elif summary["battles"]:
        print()
        print("no per unit loss data: Dominions only writes unit arrays when a battle")
        print("replay is opened in the client. Run `python -m dom6arena view <game>` for")
        print("instructions, then re-run `python -m dom6arena report --game <name>`.")
