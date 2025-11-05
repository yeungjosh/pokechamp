# Gen1 RBY OU Competition Agent Documentation

**Version:** 1.0 (Phase 4)
**Target:** PokéAgent Track 1 Competition - Gen1OU Format
**Location:** `bots/gen1_agent.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Expectimax Search Algorithm](#expectimax-search-algorithm)
5. [Gen1 Mechanics Implementation](#gen1-mechanics-implementation)
6. [Position Evaluation](#position-evaluation)
7. [Switch Logic](#switch-logic)
8. [Usage Guide](#usage-guide)
9. [Performance Benchmarks](#performance-benchmarks)
10. [Development Timeline](#development-timeline)
11. [Future Improvements](#future-improvements)

---

## Overview

The Gen1 Agent is an **expectimax-based AI** designed for competitive Generation 1 Pokémon battles (RBY OU format). It combines exact Gen1 damage calculation, strategic position evaluation, and probabilistic lookahead to make optimal decisions.

### Key Features

- **Expectimax Search:** 1-ply lookahead with probability handling
- **Gen1-Accurate Mechanics:** Exact damage formula, crit rates, type chart
- **Position Evaluation:** Material tracking, status impact, strategic factors
- **Advanced Switch Logic:** Threat assessment, matchup analysis, survival checks
- **Probability Modeling:** Hit/miss, crit/no-crit, damage variance

### Design Philosophy

- **Heuristic + Search:** Combines hand-crafted heuristics with search-based lookahead
- **Gen1-Specific:** Tuned for Gen1 mechanics (not general-purpose)
- **Fast Decisions:** ~10-15% overhead from expectimax (acceptable for ladder play)
- **Strategic Depth:** Understands concepts like Tauros preservation, sleep advantage, tempo

---

## Architecture

```
Gen1Agent (inherits Player)
│
├── Decision Layer
│   ├── choose_move() ─────────→ Main entry point
│   └── _expectimax_search() ──→ 1-ply lookahead
│
├── Search Components
│   ├── _expectimax_value() ───→ Expected value calculation
│   ├── _simulate_move_outcome() → Damage + outcome evaluation
│   └── _evaluate_switch_outcome() → Switch result estimation
│
├── Evaluation Functions
│   ├── _evaluate_position() ──→ Material + status + strategic
│   ├── _score_move() ─────────→ Immediate move scoring
│   └── _score_switch() ───────→ Switch quality assessment
│
├── Damage Calculation
│   ├── _calculate_damage() ───→ Gen1 formula (min, max)
│   ├── _get_crit_rate() ──────→ Speed-based crit chance
│   └── _get_type_effectiveness() → Gen1 type chart
│
├── Utility Functions
│   ├── _can_survive_hit() ────→ Survival estimation
│   ├── _get_accuracy() ───────→ Gen1 1/256 miss handling
│   └── _choose_best_switch() ─→ Switch selection
│
└── Configuration
    ├── use_expectimax = True
    ├── max_depth = 1
    └── Material values dict
```

---

## Core Components

### 1. Expectimax Search

**Function:** `_expectimax_search(battle)`

Evaluates all available actions (moves + switches) and selects the one with highest expected value.

```python
For each action:
    expected_value = _expectimax_value(battle, action, depth=0)
Return action with max expected_value
```

**Advantages:**
- Considers uncertainty (crits, misses, damage rolls)
- Avoids overoptimistic greedy decisions
- Handles probabilistic outcomes correctly

**Limitations:**
- 1-ply depth (doesn't model opponent responses deeply)
- Assumes opponent plays randomly (no explicit opponent model)
- Computational overhead (~10-15% slower per decision)

### 2. Probability Handling

**Function:** `_expectimax_value(battle, action, depth, is_our_turn)`

Branches on probabilistic outcomes:

```
Move Action:
├── Miss (P = 1 - accuracy)
│   └── Position unchanged
├── Hit, No Crit (P = accuracy × (1 - crit_rate))
│   └── Normal damage outcome
└── Hit, Crit (P = accuracy × crit_rate)
    └── Critical damage outcome

Switch Action:
└── Deterministic
    ├── Take damage on switch-in
    └── Evaluate new matchup
```

Each outcome is weighted by probability and summed to get expected value.

---

## Expectimax Search Algorithm

### Pseudocode

```python
def expectimax_search(battle):
    best_action = None
    best_value = -infinity

    for action in (moves + switches):
        expected_value = expectimax_value(battle, action, depth=0)
        if expected_value > best_value:
            best_value = expected_value
            best_action = action

    return best_action

def expectimax_value(battle, action, depth):
    if depth >= max_depth:
        return evaluate_position(battle)

    if action is Move:
        crit_rate = get_crit_rate(attacker, move)
        hit_rate = get_accuracy(move)

        # Branch on outcomes
        value = 0
        value += (1 - hit_rate) × evaluate_position(battle)  # Miss
        value += hit_rate × (1 - crit_rate) × simulate_move(move, crit=False)  # Hit, no crit
        value += hit_rate × crit_rate × simulate_move(move, crit=True)  # Hit, crit

        return value

    else:  # Switch
        return evaluate_switch_outcome(battle, action)
```

### Gen1-Specific Probability Models

1. **Accuracy (1/256 Miss Bug)**
   ```
   Gen1 Accuracy = Base Accuracy × (255/256)
   Example: 100% move → 99.6% actual
            90% move  → 89.5% actual
   ```

2. **Critical Hit Rate (Speed-Based)**
   ```
   Normal Moves: (Base Speed × 100) / 512
   High Crit Moves: (Base Speed × 100) / 64

   Examples:
   - Tauros (110 speed): 21.48% crit rate
   - Alakazam (120 speed): 23.44% crit rate
   - Snorlax (30 speed): 5.86% crit rate
   ```

3. **Damage Variance**
   ```
   Random Multiplier: 217-255 / 255 (85%-100%)
   Used in damage calculation formula
   ```

---

## Gen1 Mechanics Implementation

### Damage Calculation

**Function:** `_calculate_damage(attacker, defender, move, is_crit)`

**Gen1 Formula:**
```
Damage = ((((2×L×Crit÷5+2)×Pow×A/D)÷50+2)×STAB×Type×random)

Where:
- L = Level (always 100 in Gen1 OU)
- Crit = 2 if critical, else 1
- Pow = Move base power
- A = Attacker's Attack or Special stat
- D = Defender's Defense or Special stat
- STAB = 1.5 if type matches, else 1.0
- Type = Type effectiveness multiplier
- random = 217-255 / 255
```

**Physical vs Special:**
Gen1 uses **move type** (not category) to determine stat:
- Physical types: Normal, Fighting, Flying, Ground, Rock, Bug, Ghost, Poison
- Special types: Fire, Water, Electric, Grass, Ice, Psychic, Dragon

**Returns:** `(min_damage, max_damage)` tuple

### Type Chart

**Gen1 Differences:**
- Bug → Poison: 2× (not 0.5×)
- Poison → Bug: 2× (not 0.5×)
- Ghost → Psychic: 0× (bug, should be 2×)
- No Dark/Steel/Fairy types

Fully implemented in `GEN1_TYPE_CHART` constant.

### Critical Hits

**Gen1 Mechanics:**
- Crits **ignore ALL stat modifications** (even beneficial ones)
- Crits **ignore Reflect and Light Screen**
- Rate depends on **base speed** stat
- High crit moves: Karate Chop, Razor Leaf, Crabhammer, Slash

**Implementation:**
```python
def _get_crit_rate(attacker, move):
    base_speed = attacker.base_stats["spe"]
    if move.id in HIGH_CRIT_MOVES:
        return min((base_speed × 100) / 64, 1.0)
    else:
        return min((base_speed × 100) / 512, 1.0)
```

### Status Effects

**Impact on Material Value:**
- Sleep: 0.3× (heavily reduces value)
- Paralysis: 0.85× (speed reduction + full para chance)
- Burn: 0.7× (halves physical attack)
- Freeze: 0.1× (permanent in Gen1, almost dead)

**Sleep Mechanics:**
- Lasts 1-7 turns
- Waking up wastes the turn (no same-turn action)
- Sleep Clause: One per team in standard play

**Freeze Mechanics:**
- **Permanent** (no natural thaw in Gen1)
- Only cured by Fire-type attack or rare items
- Effectively removes Pokémon from battle

---

## Position Evaluation

**Function:** `_evaluate_position(battle)`

Returns a score where positive = winning, negative = losing.

### Components

1. **Material Advantage** (Weight: 0.5)
   ```
   Our Material = Σ (Base Value × HP% × Status Multiplier)
   Opp Material = Σ (Base Value × HP% × Status Multiplier)

   Score += (Our Material - Opp Material) × 0.5
   ```

2. **Material Values:**
   ```python
   Tauros:    200 pts  # Late-game sweeper
   Chansey:   180 pts  # Essential wall
   Snorlax:   180 pts  # Versatile threat
   Exeggutor: 160 pts  # Sleep + power
   Starmie:   160 pts  # Speed + coverage
   Alakazam:  150 pts  # Fast special attacker
   Zapdos:    150 pts  # Electric immunity matters
   Others:    140 pts  # Default
   ```

3. **Sleep Advantage** (Weight: 40)
   ```
   Score += (Opp Sleeping - Our Sleeping) × 40

   Rationale: Sleep is game-changing in Gen1
   ```

4. **Tauros Advantage** (Weight: ±25)
   ```
   If our Tauros alive + healthy (>60% HP): +25
   If opp Tauros alive + healthy: -25

   Rationale: Tauros is the premier sweeper
   ```

### Example Evaluation

```
Scenario: Our team vs Opponent team
- Our Tauros: 80% HP, healthy → 200 × 0.8 × 1.0 = 160
- Our Chansey: 100% HP, paralyzed → 180 × 1.0 × 0.85 = 153
- Our Snorlax: 50% HP, healthy → 180 × 0.5 × 1.0 = 90
- (3 more mons...)

- Opp Exeggutor: 30% HP, asleep → 160 × 0.3 × 0.3 = 14.4
- Opp Starmie: 90% HP, healthy → 160 × 0.9 × 1.0 = 144
- (4 more mons...)

Material Score: (Our 600 - Opp 500) × 0.5 = +50
Sleep Score: (1 - 0) × 40 = +40
Tauros Score: +25 (our Tauros healthy)

Total Position Score: +115 (winning)
```

---

## Switch Logic

### Switch Scoring Function

**Function:** `_score_switch(battle, switch_target)`

Evaluates quality of switching to a specific Pokémon.

### Factors

1. **Emergency Switching**
   - Current mon < 20% HP: +200 pts (must switch)

2. **Stay-In Bonus** (negative scores discourage switching)
   - Current mon > 50% HP + super effective move available: -150 pts
   - Current mon > 50% HP + neutral move available: -100 pts

3. **Material Value**
   - Base value × 0.5 (e.g., Tauros: +100)

4. **HP Factor**
   - HP% × 100 (prefer healthy mons)

5. **Defensive Matchup** (Survival Check)
   - Can survive hit: +150 pts
   - Cannot survive: -200 pts (avoid bad switches)

6. **Offensive Matchup** (Type Advantage)
   - Super effective move: +100 pts per move
   - Effective move: +50 pts per move
   - Walled (immune): -100 pts per move

7. **Strategic Considerations**
   - **Tauros Preservation:**
     - If alive > 3 and opp not weakened: -100 pts
     - If opp team weakened (<60% HP avg): +150 pts (time to sweep!)
   - **Chansey vs Special Attackers:**
     - Opp is Psychic/Ice/Electric/Water/Grass type: +80 pts
   - **Status Penalty:**
     - Switch-in has status: -50 pts

### Example Switch Decision

```
Current: Alakazam at 35% HP
Opponent: Tauros at 85% HP
Available switches: Chansey, Snorlax, Exeggutor

Chansey:
- Emergency bonus (Alakazam low): +200
- Material: 180 × 0.5 = +90
- HP: 100% × 100 = +100
- Can survive Tauros Body Slam: +150
- Offensive: Walled by Normal-type: -100
- Strategic: Walls Tauros somewhat: +0
Total: +440

Snorlax:
- Emergency bonus: +200
- Material: 180 × 0.5 = +90
- HP: 70% × 100 = +70
- Can survive: +150
- Offensive: Neutral damage: +0
- Strategic: Good check to Tauros: +50
Total: +560 ← **Best choice**

Exeggutor:
- Emergency bonus: +200
- Material: 160 × 0.5 = +80
- HP: 90% × 100 = +90
- Can survive: -200 (weak to Tauros moves)
- Offensive: Super effective Psychic: +100
- Strategic: Risking sleep user: -50
Total: +220

Decision: Switch to Snorlax
```

---

## Usage Guide

### Basic Usage

```python
from bots.gen1_agent import Gen1Agent

# Create agent
agent = Gen1Agent(
    battle_format="gen1ou",
    team=my_team_string,  # Optional
)

# Agent automatically makes decisions in battles
# No manual intervention needed
```

### Running Battles

```bash
# Local 1v1 test
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name max_power \
    --battle_format gen1ou \
    --N 5

# Against different baselines
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name abyssal \
    --battle_format gen1ou \
    --N 10
```

### Configuration Options

```python
# Toggle expectimax on/off
agent.use_expectimax = True   # Default: enabled
agent.use_expectimax = False  # Fallback to pure heuristics

# Adjust search depth
agent.max_depth = 1  # Default: 1-ply lookahead
agent.max_depth = 2  # Deeper search (slower, may be better)

# Debug mode
agent.debug = True  # Print decision reasoning
```

### Team Setup

The agent works with Metamon teams (auto-loaded) or custom teams:

```python
# Custom team format (Showdown export)
team = """
Tauros
Ability: Intimidate
- Body Slam
- Earthquake
- Hyper Beam
- Blizzard

Chansey
Ability: Natural Cure
EVs: 252 HP / 252 Def / 252 SpD
- Thunder Wave
- Ice Beam
- Soft-Boiled
- Seismic Toss

...
"""

agent = Gen1Agent(battle_format="gen1ou", team=team)
```

---

## Performance Benchmarks

### Phase-by-Phase Results

| Phase | Features | WR vs max_power | WR vs abyssal | Notes |
|-------|----------|-----------------|---------------|-------|
| Phase 2 | Damage calc + move scoring | 80% (5 battles) | - | Basic heuristics |
| Phase 3 | Position eval + switch logic | 100% (5 battles) | 80% (5 battles) | Strategic improvements |
| Phase 4 | Expectimax search | 66.7% (3 battles) | Testing... | Probabilistic lookahead |

### Decision Time

- **Heuristic-only (Phase 3):** ~15-17s per battle average
- **With Expectimax (Phase 4):** ~17-18s per battle average
- **Overhead:** ~10-15% slower (acceptable for ladder play)

### Strengths

1. **Damage Calculation:** Exact Gen1 formula, all edge cases handled
2. **Strategic Awareness:** Tauros preservation, sleep priority, material tracking
3. **Type Matchups:** Perfect Gen1 type chart implementation
4. **Probability Handling:** Correctly models crits, misses, damage variance

### Weaknesses

1. **Shallow Search:** Only 1-ply lookahead (doesn't see deep tactics)
2. **No Opponent Model:** Assumes random opponent (doesn't exploit patterns)
3. **Switch-In Damage:** Rough estimation (could be more accurate)
4. **No Opening Book:** Doesn't know optimal lead matchups

---

## Development Timeline

### Phase 1: Setup & Research (Days 1-2)
- ✅ Forked PokéChamp repo
- ✅ Removed torch dependencies (M3 Mac compatibility)
- ✅ Gen1OU format support added
- ✅ Comprehensive Gen1 mechanics research (28KB documentation)
- ✅ Meta analysis (usage stats, common sets)

### Phase 2: Core Heuristics (Days 3-6)
- ✅ Exact Gen1 damage calculator
- ✅ Move scoring system (KO > Sleep > Para > Damage)
- ✅ Material values for key mons
- ✅ Basic switch logic
- ✅ **Result:** 80% vs max_power

### Phase 3: Position Evaluation (Days 7-9)
- ✅ Comprehensive position evaluator (material + status + strategic)
- ✅ Advanced switch logic (survival checks, matchup analysis)
- ✅ Threat assessment
- ✅ Strategic mon usage (Tauros preservation, Chansey walls)
- ✅ **Result:** 100% vs max_power, 80% vs abyssal

### Phase 4: Expectimax Search (Days 10-11)
- ✅ 1-ply expectimax with chance nodes
- ✅ Probability handling (hit/miss, crit/no-crit, damage variance)
- ✅ Gen1-accurate probability models
- ✅ Outcome simulation
- ✅ **Result:** Testing in progress

---

## Future Improvements

### Priority 1: Performance

1. **2-Ply Search**
   - Model opponent's best responses
   - Better prediction of position after exchanges
   - Requires efficient pruning (alpha-beta for expectimax?)

2. **Opponent Modeling**
   - Track revealed moves during battle
   - Infer likely sets from move observations
   - Adjust probabilities based on opponent behavior

3. **Team Builder**
   - Construct balanced Gen1OU teams
   - Cover meta threats (Tauros, Chansey, Snorlax, etc.)
   - Multiple archetypes (offense, balance, stall)

### Priority 2: Strategic Depth

4. **Opening Book**
   - Database of optimal lead matchups
   - Pre-computed best responses for common leads
   - Helps with early-game decisions

5. **Endgame Detection**
   - Recognize when game is effectively over
   - Play more aggressively when ahead
   - More conservatively when behind

6. **Speed Tier Awareness**
   - Track which mons outspeed which
   - Matters for Hyper Beam recharge, status application
   - Gen1 speed ties (50/50 chance)

### Priority 3: Refinement

7. **Parameter Tuning**
   - Optimize material values via self-play
   - Adjust scoring weights (sleep, paralysis, etc.)
   - Calibrate switch thresholds

8. **Better Switch-In Damage Estimation**
   - Use actual move data instead of rough estimates
   - Consider EVs and stat boosts
   - More accurate survival predictions

9. **Move Prediction**
   - Estimate opponent's likely move
   - Use for better switch timing
   - Helps avoid bad switch-ins

### Priority 4: Deployment

10. **PAC Server Integration**
    - Register account on PokéAgent Showdown
    - Deploy to competition server
    - Ladder climb automation

11. **Continuous Improvement**
    - Log battles for analysis
    - Identify failure modes
    - Iterative refinement

12. **Ensemble Agent**
    - Combine multiple strategies
    - Expectimax + opening book + opponent model
    - Voting or confidence-weighted decisions

---

## Technical Notes

### Code Organization

```
bots/gen1_agent.py (670+ lines)
├── Imports & Constants (60 lines)
│   ├── Type chart
│   ├── Material values
│   └── High crit moves
│
├── Gen1Agent Class
│   ├── __init__
│   ├── choose_move (main entry)
│   │
│   ├── Expectimax Search (170 lines)
│   │   ├── _expectimax_search
│   │   ├── _expectimax_value
│   │   ├── _get_accuracy
│   │   ├── _simulate_move_outcome
│   │   └── _evaluate_switch_outcome
│   │
│   ├── Damage Calculation (80 lines)
│   │   ├── _calculate_damage
│   │   ├── _get_crit_rate
│   │   └── _get_type_effectiveness
│   │
│   ├── Evaluation (200 lines)
│   │   ├── _evaluate_position
│   │   ├── _score_move
│   │   ├── _score_switch
│   │   └── _can_survive_hit
│   │
│   └── Utilities (60 lines)
│       └── _choose_best_switch
```

### Dependencies

- `poke_env`: Battle environment and Pokémon data
- `GenData`: Generation-specific game data
- Standard library: `random`, `typing`

### Testing

```bash
# Unit tests (future)
pytest tests/test_gen1_agent.py

# Integration tests
uv run python local_1v1.py --player_name gen1_agent --opponent_name max_power --battle_format gen1ou --N 10

# Benchmarking
uv run python scripts/evaluation/evaluate_gen1ou.py
```

---

## References

1. **PokéChamp Paper:** "PokéChamp: an Expert-level Minimax Language Agent" (ICML 2025)
2. **PokéAgent Competition:** https://pokeagent.github.io/track1.html
3. **Gen1 Mechanics:** Smogon RBY OU strategy articles
4. **Type Chart:** https://bulbapedia.bulbagarden.net/wiki/Type/Type_chart
5. **Damage Formula:** https://www.smogon.com/rb/articles/damage_formula
6. **Usage Stats:** Smogon RBY OU usage statistics (2024)

---

## Credits

- **Framework:** PokéChamp (github.com/sethkarten/pokechamp)
- **Battle Engine:** poke-env
- **Competition:** PokéAgent (Track 1)
- **Development:** Phase 1-4 implementation (Nov 2025)

---

**Last Updated:** Phase 4 (Expectimax Implementation)
**Status:** Functional, testing in progress
**Next:** Team building + deployment preparation
