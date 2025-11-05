# Gen1OU Custom Teams

## Overview

Three balanced teams for Gen1 RBY OU competition, each with different strategic focuses.

## Core Philosophy

All teams include:
- **Tauros** (100% usage) - Late-game sweeper
- **Chansey** (100% usage) - Special wall, paralysis spreader
- **Snorlax** (96% usage) - Mixed wall/attacker

Plus 3 coverage mons optimized for different playstyles.

---

## Team 1: Balanced (gen1ou_balanced.txt)

**Core:** Tauros + Chansey + Snorlax + Starmie + Exeggutor + Alakazam

**Strategy:**
- Standard balanced team ("Lax-Tar-Egg" variation)
- Exeggutor for sleep control
- Starmie for speed + coverage
- Alakazam for psychic pressure

**Strengths:**
- Flexible gameplan
- Multiple sleep options (Exeggutor Sleep Powder, Exeggutor Stun Spore)
- Good special + physical balance
- Speed control (Alakazam, Starmie)

**Weaknesses:**
- Lacks explosive power compared to Rhydon/Zapdos
- Vulnerable to early sleep if Exeggutor loses lead

**Recommended vs:** Balanced opponents, testing baseline

---

## Team 2: Offensive (gen1ou_offensive.txt)

**Core:** Tauros + Chansey + Snorlax + Starmie + Rhydon + Zapdos

**Strategy:**
- "Mie-Don-Dos" core (Starmie + Rhydon + Zapdos)
- Offensive pressure throughout game
- Type coverage dominance
- Reflect Chansey for physical damage reduction

**Strengths:**
- Excellent type coverage
- Rhydon + Zapdos synergy (Electric immune + Rock resist)
- Physical + Special balance
- Reflect Chansey walls physical threats

**Weaknesses:**
- No sleep moves (must rely on Sing from Chansey - unreliable 55% accuracy)
- Weaker vs status-heavy teams
- Rhydon 4x weak to Grass/Water

**Recommended vs:** Offensive teams, speed-based opponents

---

## Team 3: Sleep Focus (gen1ou_sleep_focus.txt)

**Core:** Tauros + Chansey + Snorlax + Exeggutor + Starmie + Gengar

**Strategy:**
- Multiple sleep users (Exeggutor Sleep Powder, Gengar Hypnosis, Chansey Sing)
- Maximize sleep advantage
- Gengar lead for speed advantage (110 Speed)
- Explosive plays (Exeggutor + Gengar both have Explosion)

**Strengths:**
- Best sleep control of all teams
- Gengar fast sleep lead option
- Three explosion users for momentum
- High risk, high reward

**Weaknesses:**
- Gengar fragile (needs good lead matchup)
- Hypnosis only 60% accuracy
- Less defensive compared to other teams

**Recommended vs:** Slower teams, defensive opponents

---

## Usage

### With gen1_agent

```python
from bots.gen1_agent import Gen1Agent

# Load team
with open("teams/gen1ou_balanced.txt", "r") as f:
    team = f.read()

# Create agent
agent = Gen1Agent(
    battle_format="gen1ou",
    team=team,
)
```

### With local_1v1.py

```bash
# Test balanced team
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name max_power \
    --battle_format gen1ou \
    --N 10 \
    --player_team teams/gen1ou_balanced.txt
```

---

## Team Building Notes

### Mandatory Mons
- Tauros (100% usage) - Cannot build without
- Chansey (100% usage) - Best special wall
- Snorlax (96% usage) - Best mixed threat

### High Priority
- Starmie (79%) - Speed, recovery, versatility
- Exeggutor (63%) - Sleep control, explosion

### Situational
- Alakazam (38%) - Speed tier, psychic pressure
- Rhydon/Zapdos (25%) - Coverage, synergy
- Gengar (~15%) - Lead sleeper, rising usage

### Key Principles
1. **Sleep control** - At least 1 sleep user
2. **Speed tiers** - Cover 110+ (Tauros tier)
3. **Type coverage** - Water/Electric/Psychic/Ground
4. **Explosion** - 1-2 users for momentum
5. **Status spread** - Thunder Wave on Chansey mandatory

---

## Testing Results

Will be updated after testing vs baselines.

Expected performance:
- vs max_power: 90%+
- vs abyssal: 70-80%
- vs random: 95%+

Actual results: TBD
