"""Tournament runner for head-to-head bot evaluation.

Runs N battles between two bot classes and dumps:
  * progress to stdout
  * a CSV of per-game results to ./tournament_results/<timestamp>.csv
  * a final summary (W/D/L, win rate, mean game length)

Usage:
  uv run python run_tournament.py \
      --bot_a mcts --bot_b random \
      --battle_format gen1ou --N 20

Notes:
  * Both bots use the project's standard `get_llm_player` factory, so any
    name in `bot_choices` works on either side.
  * `--mcts_iterations` / `--mcts_depth` / `--mcts_time_budget` are read
    from argparse and forwarded into MCTSBot when bot_a or bot_b is `mcts`.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
import time
from datetime import datetime

import numpy as np

# Make project root importable (mirrors local_1v1.py pattern).
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from common import bot_choices, prompt_algos, PNUMBER1
from poke_env.player.team_util import (
    get_llm_player,
    get_metamon_teams,
    load_random_team,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--bot_a", choices=bot_choices, required=True)
    p.add_argument("--bot_b", choices=bot_choices, required=True)
    p.add_argument("--battle_format", default="gen1ou")
    p.add_argument("--N", type=int, default=20, help="number of battles")
    p.add_argument("--log_dir", default="./battle_log/tournament")
    p.add_argument("--results_dir", default="./tournament_results")

    # MCTS knobs (consumed via getattr in team_util.get_llm_player)
    p.add_argument("--mcts_iterations", type=int, default=100)
    p.add_argument("--mcts_depth", type=int, default=3)
    p.add_argument("--mcts_time_budget", type=float, default=10.0)

    # Inert args expected by get_llm_player; we don't actually run LLMs here
    # unless the user passes an LLM bot name, in which case temperature/etc
    # need sane defaults.
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--prompt_algo", default="io", choices=prompt_algos)
    p.add_argument("--backend", default="gpt-4o-mini")
    p.add_argument("--device", type=int, default=0)

    return p.parse_args()


def make_player(args, name, suffix):
    """Build a Player from a bot name. `suffix` keeps account names unique."""
    # get_llm_player reads from `args` directly for prompt_algo/backend/etc.
    return get_llm_player(
        args,
        backend=args.backend,
        prompt_algo=args.prompt_algo,
        name=name,
        device=args.device,
        PNUMBER1=PNUMBER1 + suffix,
        battle_format=args.battle_format,
    )


async def main():
    args = parse_args()
    print(f"\n=== TOURNAMENT: {args.bot_a} vs {args.bot_b} ===")
    print(f"Format: {args.battle_format}  N: {args.N}\n")

    player = make_player(args, args.bot_a, "")
    opponent = make_player(args, args.bot_b, "2")

    # Team setup mirrors local_1v1.py — try metamon teams, fall back to static.
    player_teamloader = opponent_teamloader = None
    if "random" not in args.battle_format:
        try:
            player_teamloader = get_metamon_teams(args.battle_format, "competitive")
            opponent_teamloader = get_metamon_teams(args.battle_format, "modern_replays")
        except Exception:
            pass
        if player_teamloader is None or opponent_teamloader is None:
            player.update_team(load_random_team(id=None, vgc=False))
            opponent.update_team(load_random_team(id=None, vgc=False))
        else:
            player.set_teamloader(player_teamloader)
            opponent.set_teamloader(opponent_teamloader)
            player.update_team(player_teamloader.yield_team())
            opponent.update_team(opponent_teamloader.yield_team())

    os.makedirs(args.results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(
        args.results_dir,
        f"{args.bot_a}_vs_{args.bot_b}_{args.battle_format}_{timestamp}.csv",
    )

    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["i", "winner", "a_win_rate_so_far", "wall_time_s"],
        )
        writer.writeheader()

        prev_won = prev_lost = 0
        for i in range(args.N):
            start = time.perf_counter()
            if np.random.randint(0, 100) > 50:
                await player.battle_against(opponent, n_battles=1)
            else:
                await opponent.battle_against(player, n_battles=1)
            wall = time.perf_counter() - start

            # Determine this game's winner by diffing player counts vs last game.
            if player.n_won_battles > prev_won:
                winner = args.bot_a
            elif player.n_lost_battles > prev_lost:
                winner = args.bot_b
            else:
                winner = "draw"
            prev_won = player.n_won_battles
            prev_lost = player.n_lost_battles

            writer.writerow({
                "i": i + 1,
                "winner": winner,
                "a_win_rate_so_far": f"{player.win_rate:.3f}",
                "wall_time_s": f"{wall:.1f}",
            })
            fh.flush()

            if "random" not in args.battle_format:
                if player_teamloader is None or opponent_teamloader is None:
                    player.update_team(load_random_team(id=None, vgc=False))
                    opponent.update_team(load_random_team(id=None, vgc=False))
                else:
                    player.update_team(player_teamloader.yield_team())
                    opponent.update_team(opponent_teamloader.yield_team())

            print(
                f"[{i+1}/{args.N}] {args.bot_a} W/L: "
                f"{player.n_won_battles}/{player.n_lost_battles}  "
                f"rate: {player.win_rate*100:.1f}%  "
                f"({wall:.1f}s)"
            )

    print("\n=== SUMMARY ===")
    print(f"{args.bot_a}: {player.n_won_battles}W / {player.n_lost_battles}L")
    print(f"Win rate ({args.bot_a}): {player.win_rate*100:.2f}%")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
