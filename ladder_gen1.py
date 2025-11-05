#!/usr/bin/env python3
"""
Gen1 Agent Ladder Script

Simple script to run gen1_agent on the PokéAgent Challenge ladder.

Usage:
    # Test 1 battle
    uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" --N 1

    # Run 10 battles with balanced team
    uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" \
        --team "teams/gen1ou_balanced.txt" --N 10

    # Run 50 battles with random teams
    uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" --N 50
"""

import asyncio
import argparse
import sys
from pathlib import Path
from time import sleep
import random
from tqdm import tqdm

from bots.gen1_agent import Gen1Agent
from poke_env.player.account_configuration import AccountConfiguration
from poke_env.ps_client.server_configuration import ShowdownServerConfiguration


def load_team(team_file: str) -> str:
    """Load team from Showdown format text file"""
    if not team_file:
        return None

    team_path = Path(team_file)
    if not team_path.exists():
        print(f"Error: Team file not found: {team_file}")
        sys.exit(1)

    with open(team_path, 'r') as f:
        team = f.read()

    print(f"Loaded team from {team_file}")
    return team


async def main():
    parser = argparse.ArgumentParser(description='Run Gen1 Agent on ladder')
    parser.add_argument('--USERNAME', type=str, required=True,
                       help='Showdown username (must start with "PAC")')
    parser.add_argument('--PASSWORD', type=str, required=True,
                       help='Showdown password')
    parser.add_argument('--team', type=str, default='',
                       help='Path to team file (e.g., teams/gen1ou_balanced.txt). Leave empty for random Metamon teams.')
    parser.add_argument('--N', type=int, default=10,
                       help='Number of ladder battles to play')
    parser.add_argument('--delay', type=int, default=30,
                       help='Random delay between battles (max seconds)')
    args = parser.parse_args()

    # Validate username
    if not args.USERNAME.startswith('PAC'):
        print("Warning: Username should start with 'PAC' for competition")
        print(f"Current username: {args.USERNAME}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Load team if specified
    team = load_team(args.team) if args.team else None

    # Create agent
    print(f"\nCreating Gen1 agent...")
    print(f"  Username: {args.USERNAME}")
    print(f"  Server: pokeagentshowdown.com")
    print(f"  Format: gen1ou")
    print(f"  Team: {'Custom' if team else 'Random (Metamon)'}")
    print(f"  Battles: {args.N}")
    print()

    agent = Gen1Agent(
        battle_format="gen1ou",
        team=team,
        account_configuration=AccountConfiguration(args.USERNAME, args.PASSWORD),
        server_configuration=ShowdownServerConfiguration,
    )

    # Connect and play ladder battles
    print("Connecting to ladder...")

    wins = 0
    losses = 0
    pbar = tqdm(total=args.N, desc="Ladder Progress")

    for i in range(args.N):
        # Random delay between battles to avoid rate limiting
        if i > 0:
            delay = random.randint(10, args.delay)
            sleep(delay)

        print(f"\nStarting ladder battle {i+1}/{args.N}...")

        try:
            # Play one ladder battle
            await agent.ladder(1)

            # Check result
            if agent.n_won_battles > wins:
                wins += 1
                result = "Won"
            else:
                losses += 1
                result = "Lost"

            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

            print(f"Battle {i+1}: {result}")
            print(f"Record: {wins}-{losses} ({win_rate:.1f}%)")

            pbar.set_description(f"W: {wins} L: {losses} ({win_rate:.1f}%)")
            pbar.update(1)

            # Reset battle state
            agent.reset_battles()

        except Exception as e:
            print(f"Error in battle {i+1}: {e}")
            pbar.update(1)
            continue

    pbar.close()

    # Final statistics
    print(f"\n{'='*60}")
    print("LADDER RESULTS")
    print(f"{'='*60}")
    print(f"Total battles: {wins + losses}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    print(f"Win rate: {win_rate:.1f}%")
    print(f"{'='*60}\n")

    print("Ladder run complete!")
    print(f"Check your ranking at: https://pokeagentshowdown.com")


if __name__ == "__main__":
    asyncio.run(main())
