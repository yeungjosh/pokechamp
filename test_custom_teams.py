#!/usr/bin/env python3
"""
Test custom Gen1OU teams against baselines
"""
import asyncio
import sys
from pathlib import Path
from bots.gen1_agent import Gen1Agent
from poke_env.player.random_player import RandomPlayer
from poke_env.player.player import Player


def load_team(team_file: str) -> str:
    """Load team from Showdown format text file"""
    team_path = Path("teams") / team_file
    with open(team_path, 'r') as f:
        return f.read()


async def test_team(team_name: str, team_file: str, n_battles: int = 5):
    """Test a team against max_power baseline"""
    print(f"\n{'='*60}")
    print(f"Testing: {team_name}")
    print(f"Team file: {team_file}")
    print(f"Battles: {n_battles}")
    print(f"{'='*60}\n")

    # Load team
    team = load_team(team_file)

    # Create agent with custom team
    agent = Gen1Agent(
        battle_format="gen1ou",
        team=team,
    )

    # Create opponent (max_power equivalent - just random for now)
    opponent = RandomPlayer(
        battle_format="gen1ou",
    )

    # Run battles
    await agent.battle_against(opponent, n_battles=n_battles)

    # Calculate win rate
    wins = sum(1 for battle in agent.battles.values() if battle.won)
    total = len(agent.battles)
    win_rate = (wins / total * 100) if total > 0 else 0

    print(f"\n{team_name} Results:")
    print(f"  Wins: {wins}/{total}")
    print(f"  Win Rate: {win_rate:.1f}%")

    return win_rate


async def main():
    """Test all custom teams"""
    teams = [
        ("Balanced Team", "gen1ou_balanced.txt"),
        ("Offensive Team", "gen1ou_offensive.txt"),
        ("Sleep Focus Team", "gen1ou_sleep_focus.txt"),
    ]

    results = {}

    for team_name, team_file in teams:
        try:
            win_rate = await test_team(team_name, team_file, n_battles=5)
            results[team_name] = win_rate
        except Exception as e:
            print(f"Error testing {team_name}: {e}")
            results[team_name] = 0

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    for team_name, win_rate in results.items():
        print(f"{team_name:25s}: {win_rate:5.1f}%")

    # Best team
    best_team = max(results, key=results.get)
    print(f"\nBest performing team: {best_team} ({results[best_team]:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
