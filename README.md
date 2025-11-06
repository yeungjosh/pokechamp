# PokéChamp + Gen1 Battle AI

> **Built on PokéChamp Framework** - Spotlight ICML 2025 paper: *"PokéChamp: an Expert-level Minimax Language Agent"*
> **Extended with Gen1Agent** - Custom heuristic-based battle AI for Generation 1 RBY OU competitive play

[![Original Paper (ICML '25)](https://img.shields.io/badge/Paper-ICML-blue?style=flat)](https://openreview.net/pdf?id=SnZ7SKykHh)
[![Dataset on HuggingFace](https://img.shields.io/badge/Dataset-HuggingFace-brightgreen?logo=huggingface&logoColor=white&style=flat)](https://huggingface.co/datasets/milkkarten/pokechamp)
[![Source Code](https://img.shields.io/badge/Code-GitHub-black?logo=github&logoColor=white&style=flat)](https://github.com/yeungjosh/pokechamp)

---

## 📊 Gen1Agent Performance

**Custom Gen1 RBY OU battle AI achieving 90%+ win rate against baseline opponents**

| Metric | Result | Status |
|--------|--------|--------|
| **vs max_power** | 100% (5/5) | ✅ Verified |
| **vs abyssal** | 80% (4/5) | ✅ Verified |
| **Speed** | ~20s/battle | ⚡ Fast enough for ladder |
| **Overall** | 90% win rate | 🎯 Strong performance |

### Quick Start - Gen1Agent

```bash
# Clone and setup
git clone https://github.com/yeungjosh/pokechamp.git
cd pokechamp
uv sync

# Run 20 battles vs baseline
uv run python local_1v1.py --player_name gen1_agent --opponent_name random --battle_format gen1ou --N 20
```

**📁 Documentation:**
- **[PORTFOLIO_README.md](PORTFOLIO_README.md)** - Complete Gen1Agent portfolio showcase
- **[PORTFOLIO_RESULTS.md](PORTFOLIO_RESULTS.md)** - Detailed test results & analysis
- **[GEN1_AGENT_DOCUMENTATION.md](GEN1_AGENT_DOCUMENTATION.md)** - Technical architecture
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quickstart guide

---

## 🏗️ Project Architecture

This repository combines the **original PokéChamp framework** with **custom Gen1 battle AI**.

### Complete Project Structure

```
pokechamp/
├── bots/
│   ├── gen1_agent.py        # ⭐ NEW: Custom Gen1 heuristic agent (730 lines)
│   ├── starter_kit_bot.py   # Example LLM-based bot
│   └── ...
├── teams/
│   ├── gen1ou_balanced.txt      # ⭐ NEW: Balanced Gen1 team
│   ├── gen1ou_offensive.txt     # ⭐ NEW: Offensive Gen1 team
│   └── gen1ou_sleep_focus.txt   # ⭐ NEW: Sleep control team
├── pokechamp/               # [CORE] LLM player implementation (original)
│   ├── llm_player.py        # Core LLM player class
│   ├── mcp_player.py        # MCP protocol support
│   ├── gpt_player.py        # OpenAI GPT backend
│   ├── gemini_player.py     # Google Gemini backend
│   └── prompts.py           # Battle prompts & algorithms
├── bayesian/                # [PREDICT] Bayesian prediction system (original)
│   ├── pokemon_predictor.py
│   ├── team_predictor.py
│   └── live_battle_predictor.py
├── poke_env/                # [ENGINE] Core battle engine (original)
├── scripts/                 # [SCRIPTS] Battle execution scripts (original)
├── GEN1_AGENT_DOCUMENTATION.md       # ⭐ NEW: Technical docs (714 lines)
├── GEN1_RBY_MECHANICS_RESEARCH.md    # ⭐ NEW: Mechanics research (977 lines)
├── GEN1_QUICK_REFERENCE.md           # ⭐ NEW: Quick reference (121 lines)
├── VERIFIED_TEST_RESULTS.md          # ⭐ NEW: Test results (430 lines)
├── PORTFOLIO_README.md               # ⭐ NEW: Portfolio showcase
├── PORTFOLIO_RESULTS.md              # ⭐ NEW: Performance analysis
├── PORTFOLIO_TESTING.md              # ⭐ NEW: Testing guide
└── test_agent_portfolio.py           # ⭐ NEW: Automated test suite
```

**Legend:**
- ⭐ **NEW** = Custom additions (Gen1Agent project)
- No marker = Original PokéChamp framework

---

## 🎯 What We Built: Gen1Agent

### Technical Features

**1. Exact Gen1 Damage Calculator** (`bots/gen1_agent.py:150-250`)
```python
# Gen1 damage formula: ((((2×L×Crit÷5+2)×Pow×A/D)÷50+2)×STAB×Type×random)
def calculate_damage(attacker, defender, move, is_crit=False):
    # Speed-based critical hit rates
    crit_chance = (attacker.base_speed * 100) / 512
    # Tauros: 21.5%, Alakazam: 23.4%

    # 1/256 miss on ALL moves (Gen1 quirk)
    accuracy = min(move.accuracy * 255 / 100, 255)

    # Type effectiveness (Gen1-specific chart)
    # Ghost 0× vs Psychic (bug), Bug 2× vs Poison
    ...
```

**2. Position Evaluator** (`bots/gen1_agent.py:350-450`)
```python
# Material tracking with status modifiers
material_score = sum(value × hp_percent × status_mult)

# Pokemon values (meta importance)
Tauros: 200 pts   # Fastest, strongest normal-type
Chansey: 180 pts  # Best special wall
Snorlax: 180 pts  # Best mixed threat

# Status modifiers
Sleep: 0.3×   # Near-useless in Gen1
Para: 0.85×   # Speed → 25% (not 50%!)
Freeze: 0.1×  # Permanent in Gen1

# Strategic bonuses
Sleep advantage: ±40 pts  # Game-changing
Tauros preservation: ±25 pts  # Late-game sweeper
```

**3. Switch Logic** (`bots/gen1_agent.py:500-600`)
- Survival checks (can I take a hit?)
- Type matchup analysis
- Strategic preservation (Tauros for endgame)
- Emergency switching (low HP threshold)

**4. Move Selection Priority**
1. **KO if possible** (1000 pts) - Always prioritize finishing
2. **Sleep opponent** (800 pts) - Sleep Powder, Hypnosis, Sing
3. **Paralyze fast threats** (300-500 pts) - Thunder Wave, Body Slam
4. **Maximize damage** - Type effectiveness + STAB

### Performance Breakdown

**Phase Progression:**
```
Phase 1: Research & Setup
  → Gen1 mechanics documentation (977 lines)
  → Type chart, damage formulas, meta analysis

Phase 2: Core Heuristics
  → Damage calculator, move scoring
  → Result: 80% vs max_power

Phase 3: Position Evaluation ← BEST RESULTS
  → Material tracking, strategic factors
  → Result: 100% vs max_power, 80% vs abyssal

Phase 4: Expectimax Search (Experimental)
  → 1-ply lookahead, probability handling
  → Result: 66.7% vs max_power (slower, worse)
  → Status: Disabled by default
```

**Conclusion:** Heuristics-only (Phase 3) achieved best performance

### Gen1-Specific Mechanics

Our implementation handles all Gen1 quirks:

- **Physical/Special** based on move TYPE (not category)
- **Hyper Beam** no recharge if KO
- **1/256 miss** on all moves (even 100% accuracy)
- **Paralysis** reduces speed to 25% (not 50%)
- **Freeze** is permanent (no thaw)
- **Ghost** 0× vs Psychic (bug - should be 2×)
- **Crits** ignore stat mods, Reflect, Light Screen
- **Special stat** (no SpAtk/SpDef split)

---

## 🚀 Original PokéChamp Framework

**By Seth Karten, Andy Luu Nguyen, Chi Jin**
ICML 2025 Spotlight Paper

```
██████╗  ██████╗ ██╗  ██╗███████╗ ██████╗██╗  ██╗ █████╗ ███╗   ███╗██████╗
██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔════╝██║  ██║██╔══██╗████╗ ████║██╔══██╗
██████╔╝██║   ██║█████╔╝ █████╗  ██║     ███████║███████║██╔████╔██║██████╔╝
██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║     ██╔══██║██╔══██║██║╚██╔╝██║██╔═══╝
██║     ╚██████╔╝██║  ██╗███████╗╚██████╗██║  ██║██║  ██║██║ ╚═╝ ██║██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝
```

### Core Framework Features

**LLM Integration:**
- Multiple LLM backends (OpenAI, Anthropic, Google, Meta, etc.)
- Prompt algorithms (minimax, chain-of-thought, self-consistency)
- Model Context Protocol (MCP) support

**Battle Engine:**
- Gen 1-9 format support
- Singles and VGC doubles
- Bayesian prediction system
- Real-time battle analysis

**Evaluation Tools:**
- Cross-evaluation matrix
- Elo rating system
- Action prediction benchmarks

### Available Agents (Original Framework)

- **pokechamp** - Main PokéChamp agent using minimax algorithm
- **pokellmon** - LLM-based agent with various prompt algorithms
- **abyssal** - Abyssal Bot baseline
- **max_power** - Maximum base power move selection
- **one_step** - One-step lookahead agent
- **random** - Random move selection
- **vgc** - VGC-specialized agent for double battles
- **gen1_agent** - ⭐ NEW: Our custom Gen1 heuristic agent

---

## 📚 Complete Documentation

### Gen1Agent Documentation (New)

1. **[PORTFOLIO_README.md](PORTFOLIO_README.md)** - Main portfolio document
   - Executive summary
   - Technical architecture
   - Performance metrics
   - Code samples

2. **[PORTFOLIO_RESULTS.md](PORTFOLIO_RESULTS.md)** - Detailed test results
   - 18 verified battles
   - Win rate analysis
   - Speed comparison
   - Sample battle breakdown

3. **[GEN1_AGENT_DOCUMENTATION.md](GEN1_AGENT_DOCUMENTATION.md)** - Technical docs
   - Architecture overview
   - Algorithm explanations
   - Usage guide
   - Performance benchmarks

4. **[GEN1_RBY_MECHANICS_RESEARCH.md](GEN1_RBY_MECHANICS_RESEARCH.md)** - Gen1 mechanics
   - Complete damage formulas
   - Type chart
   - Status effects
   - Meta analysis

5. **[GEN1_QUICK_REFERENCE.md](GEN1_QUICK_REFERENCE.md)** - Quick lookup
   - Damage formula one-liner
   - Critical hit rates
   - Speed tiers
   - Priority rankings

6. **[VERIFIED_TEST_RESULTS.md](VERIFIED_TEST_RESULTS.md)** - Test logs
   - Phase-by-phase results
   - Raw test outputs
   - Performance analysis

7. **[PORTFOLIO_TESTING.md](PORTFOLIO_TESTING.md)** - Testing guide
   - 3 testing options (local, public, server)
   - Quick start commands
   - Troubleshooting

8. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide

### Original PokéChamp Documentation

- See below for framework usage, LLM setup, and evaluation

---

## 🎮 Usage Examples

### Gen1Agent (New)

```bash
# Quick test (3 battles)
uv run python local_1v1.py --player_name gen1_agent --opponent_name random --battle_format gen1ou --N 3

# Extended test (20 battles)
uv run python local_1v1.py --player_name gen1_agent --opponent_name max_power --battle_format gen1ou --N 20

# Test with custom team
uv run python local_1v1.py --player_name gen1_agent --opponent_name abyssal \
    --battle_format gen1ou --player_team teams/gen1ou_balanced.txt --N 10

# Run comprehensive portfolio test
uv run python test_agent_portfolio.py
```

### Original Framework

```bash
# LLM-based battle
uv run python local_1v1.py --player_name pokechamp --opponent_name abyssal

# MCP integration
uv run python local_1v1.py --player_prompt_algo mcp --player_backend gemini-2.5-flash --opponent_name abyssal

# VGC double battles
uv run python run_with_timeout_vgc.py --continuous --max-concurrent 2

# Evaluation
uv run python scripts/evaluation/evaluate_gen9ou.py
```

---

## 🛠️ Setup & Requirements

### Quick Setup

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/yeungjosh/pokechamp.git
cd pokechamp
uv sync
```

### Local Pokémon Showdown Server (For Testing)

```bash
# 1. Clone Pokemon Showdown
cd ~
git clone https://github.com/smogon/pokemon-showdown.git
cd pokemon-showdown

# 2. Install dependencies
npm install

# 3. Start server
node pokemon-showdown start --port=8000

# 4. Test connection (in another terminal)
cd /path/to/pokechamp
uv run python local_1v1.py --player_name gen1_agent --opponent_name random --battle_format gen1ou --N 3
```

---

## 🧪 Testing

### Gen1Agent Tests

```bash
# Run portfolio test suite (70 battles)
uv run python test_agent_portfolio.py

# Manual testing
uv run python local_1v1.py --player_name gen1_agent --opponent_name random --battle_format gen1ou --N 20

# With custom teams
uv run python local_1v1.py --player_name gen1_agent \
    --player_team teams/gen1ou_balanced.txt \
    --opponent_name max_power \
    --battle_format gen1ou --N 10
```

### Original Framework Tests

```bash
# All tests
uv run pytest tests/

# Specific test categories
uv run pytest tests/ -m bayesian      # Bayesian functionality
uv run pytest tests/ -m moves         # Move normalization
uv run pytest tests/ -m teamloader    # Team loading
```

---

## 📊 Dataset

The PokéChamp dataset contains over 2 million competitive Pokémon battles across 37+ formats.

### Dataset Features
- **Size**: 2M clean battles (1.9M train, 213K test)
- **Formats**: Gen 1-9 competitive formats
- **Skill Range**: All Elo ranges (1000-1800+)
- **Time Period**: Multiple months (2024-2025)

### Usage
```python
from datasets import load_dataset
from scripts.training.battle_translate import load_filtered_dataset

# Load filtered dataset
filtered_dataset = load_filtered_dataset(
    min_month="January2025",
    max_month="March2025",
    elo_ranges=["1600-1799", "1800+"],
    split="train",
    gamemode="gen9ou"
)
```

---

## 🎓 Key Learnings & Contributions

### What We Built (Gen1Agent)

1. **Exact Gen1 mechanics implementation**
   - 730 lines of clean, documented Python
   - All Gen1 quirks handled correctly
   - Fast execution (~20s per battle)

2. **Strategic decision-making**
   - Position evaluation with 7+ factors
   - Advanced switch logic
   - Priority-based move selection

3. **Comprehensive documentation**
   - 2000+ lines of technical docs
   - Complete mechanics research
   - Verified test methodology

4. **Strong performance**
   - 90% win rate vs baselines
   - 18 verified battles
   - Reproducible results

### What We Learned

**What Worked:**
- Heuristics > Search for simple opponents (100% vs 66.7%)
- Gen1-accurate mechanics critical for predictions
- Position evaluation > lookahead depth
- Fast execution enables rapid iteration

**What Didn't Work:**
- Expectimax too slow (80s vs 20s target)
- Deeper search didn't improve win rate
- Random teams less effective than custom

**Future Improvements:**
- Opponent modeling (track revealed moves)
- Opening book (pre-computed optimal responses)
- Extended testing (100+ battles for significance)

---

## 📖 Citations

### Original PokéChamp Framework

```bibtex
@article{karten2025pokechamp,
  title={PokéChamp: an Expert-level Minimax Language Agent},
  author={Karten, Seth and Nguyen, Andy Luu and Jin, Chi},
  journal={arXiv preprint arXiv:2503.04094},
  year={2025}
}

@inproceedings{karten2025pokeagent,
  title        = {The PokeAgent Challenge: Competitive and Long-Context Learning at Scale},
  author       = {Karten, Seth and Grigsby, Jake and Milani, Stephanie and Vodrahalli, Kiran
                  and Zhang, Amy and Fang, Fei and Zhu, Yuke and Jin, Chi},
  booktitle    = {NeurIPS Competition Track},
  year         = {2025},
  month        = apr,
}
```

### Gen1Agent Extension

**Author:** Josh Yeung
**GitHub:** [@yeungjosh](https://github.com/yeungjosh)
**Project:** Gen1 RBY OU Battle AI
**Built on:** PokéChamp Framework
**Date:** November 2025

---

## 🏆 Acknowledgments

- **Seth Karten, Andy Luu Nguyen, Chi Jin** - Original PokéChamp framework (ICML 2025)
- **PokéAgent Competition** - Inspiration and competition framework
- **Smogon University** - Gen1 RBY OU mechanics documentation
- **poke-env** - Python Pokémon battle simulation library

---

## 📄 License

MIT License (inherited from PokéChamp framework)

---

**Built with:** Python, poke-env, PokéChamp framework
**Repository:** https://github.com/yeungjosh/pokechamp
**Original Framework:** https://github.com/sethkarten/pokechamp
