#!/usr/bin/env python3
"""
Portfolio Test Suite - No Server Required

Tests gen1_agent extensively vs multiple baselines locally.
Generates detailed performance reports for portfolio.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly to avoid circular imports
from poke_env.player.random_player import RandomPlayer
from poke_env.player.max_damage_player import MaxDamagePlayer

# Import Gen1Agent after poke_env
import importlib.util
spec = importlib.util.spec_from_file_location("gen1_agent", "bots/gen1_agent.py")
gen1_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen1_module)
Gen1Agent = gen1_module.Gen1Agent


async def test_matchup(agent_name, agent, opponent_name, opponent, n_battles=20):
    """Test agent vs opponent and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {agent_name} vs {opponent_name}")
    print(f"Battles: {n_battles}")
    print(f"{'='*60}\n")

    # Reset battle stats
    agent.reset_battles()
    opponent.reset_battles()

    # Run battles
    await agent.battle_against(opponent, n_battles=n_battles)

    # Calculate stats
    wins = sum(1 for battle in agent.battles.values() if battle.won)
    losses = n_battles - wins
    win_rate = (wins / n_battles * 100) if n_battles > 0 else 0

    result = {
        "agent": agent_name,
        "opponent": opponent_name,
        "battles": n_battles,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "timestamp": datetime.now().isoformat()
    }

    print(f"\nResults:")
    print(f"  Record: {wins}-{losses}")
    print(f"  Win Rate: {win_rate:.1f}%")

    return result


async def run_full_test_suite():
    """Run comprehensive test suite"""
    print("="*60)
    print("GEN1 AGENT PORTFOLIO TEST SUITE")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # Test 1: vs Random (20 battles)
    print("\n📊 Test 1: vs Random Player")
    agent1 = Gen1Agent(battle_format="gen1ou")
    opponent1 = RandomPlayer(battle_format="gen1ou")
    result1 = await test_matchup("gen1_agent", agent1, "random", opponent1, n_battles=20)
    results.append(result1)

    # Test 2: vs MaxDamage (20 battles)
    print("\n📊 Test 2: vs Max Damage Player")
    agent2 = Gen1Agent(battle_format="gen1ou")
    opponent2 = MaxDamagePlayer(battle_format="gen1ou")
    result2 = await test_matchup("gen1_agent", agent2, "max_damage", opponent2, n_battles=20)
    results.append(result2)

    # Test 3: vs Random with custom team (10 battles)
    print("\n📊 Test 3: Custom Balanced Team vs Random")
    with open("teams/gen1ou_balanced.txt", 'r') as f:
        balanced_team = f.read()
    agent3 = Gen1Agent(battle_format="gen1ou", team=balanced_team)
    opponent3 = RandomPlayer(battle_format="gen1ou")
    result3 = await test_matchup("gen1_agent_balanced", agent3, "random", opponent3, n_battles=10)
    results.append(result3)

    # Test 4: vs Random with offensive team (10 battles)
    print("\n📊 Test 4: Custom Offensive Team vs Random")
    with open("teams/gen1ou_offensive.txt", 'r') as f:
        offensive_team = f.read()
    agent4 = Gen1Agent(battle_format="gen1ou", team=offensive_team)
    opponent4 = RandomPlayer(battle_format="gen1ou")
    result4 = await test_matchup("gen1_agent_offensive", agent4, "random", opponent4, n_battles=10)
    results.append(result4)

    # Test 5: vs Random with sleep team (10 battles)
    print("\n📊 Test 5: Custom Sleep Focus Team vs Random")
    with open("teams/gen1ou_sleep_focus.txt", 'r') as f:
        sleep_team = f.read()
    agent5 = Gen1Agent(battle_format="gen1ou", team=sleep_team)
    opponent5 = RandomPlayer(battle_format="gen1ou")
    result5 = await test_matchup("gen1_agent_sleep", agent5, "random", opponent5, n_battles=10)
    results.append(result5)

    # Summary
    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)

    total_battles = sum(r["battles"] for r in results)
    total_wins = sum(r["wins"] for r in results)
    overall_win_rate = (total_wins / total_battles * 100) if total_battles > 0 else 0

    print(f"\nOverall Performance:")
    print(f"  Total battles: {total_battles}")
    print(f"  Total wins: {total_wins}")
    print(f"  Overall win rate: {overall_win_rate:.1f}%")

    print(f"\nBreakdown by Matchup:")
    for result in results:
        print(f"  {result['agent']:25s} vs {result['opponent']:15s}: "
              f"{result['wins']:2d}-{result['losses']:2d} ({result['win_rate']:5.1f}%)")

    # Save results
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"portfolio_test_{timestamp}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_battles": total_battles,
        "total_wins": total_wins,
        "overall_win_rate": overall_win_rate,
        "results": results
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📁 Results saved to: {output_file}")

    # Create markdown report
    md_file = output_dir / f"portfolio_test_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# Gen1 Agent Portfolio Test Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Overall Performance\n\n")
        f.write(f"- **Total Battles:** {total_battles}\n")
        f.write(f"- **Total Wins:** {total_wins}\n")
        f.write(f"- **Overall Win Rate:** {overall_win_rate:.1f}%\n\n")
        f.write("## Detailed Results\n\n")
        f.write("| Configuration | Opponent | Battles | Record | Win Rate |\n")
        f.write("|--------------|----------|---------|---------|----------|\n")
        for r in results:
            f.write(f"| {r['agent']} | {r['opponent']} | {r['battles']} | "
                   f"{r['wins']}-{r['losses']} | {r['win_rate']:.1f}% |\n")

    print(f"📄 Markdown report: {md_file}")

    print("\n✅ Portfolio test suite complete!")


if __name__ == "__main__":
    asyncio.run(run_full_test_suite())
