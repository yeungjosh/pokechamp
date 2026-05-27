# Running a Tournament

`run_tournament.py` plays N battles between two bots (any names from `bot_choices`) and dumps per-game CSV results.

```bash
uv run python run_tournament.py \
    --bot_a mcts \
    --bot_b random \
    --battle_format gen1ou \
    --N 20
```

CSV lands in `./tournament_results/<bot_a>_vs_<bot_b>_<format>_<timestamp>.csv` with columns: `i, winner, a_win_rate_so_far, wall_time_s`.

## MCTS knobs

```bash
--mcts_iterations 100   # default; how many UCT iterations per move
--mcts_depth 3          # default; rollout depth in plies (each ply = both players move)
--mcts_time_budget 10   # default; seconds cap per move (whichever limit hits first)
```

## Prerequisite: a Pokemon Showdown server

`battle_against` needs a running Showdown WebSocket on `localhost:8000`. Two options:

### Option A — Local Showdown (recommended)

```bash
git clone https://github.com/smogon/pokemon-showdown ~/tools/pokemon-showdown
cd ~/tools/pokemon-showdown
npm install
```

**Before starting, harden the bind address** — by default Showdown listens on `0.0.0.0` (all network interfaces), which exposes it to anyone on your LAN.

1. Edit `~/tools/pokemon-showdown/config/config.js`:
   ```js
   exports.bindaddress = '127.0.0.1';  // local-only
   ```
2. The worker subprocess may still pick up `0.0.0.0` from a cached/compiled config. Belt-and-suspenders: also pass `PSBINDADDR`:
   ```bash
   PSBINDADDR=127.0.0.1 ./pokemon-showdown start --no-security
   ```
3. Verify before connecting any bot:
   ```bash
   lsof -i :8000 -P -n | grep LISTEN
   # MUST show 127.0.0.1:8000, NOT *:8000
   ```
4. **Enable the macOS firewall as a safety net** in case Showdown ignores the bind setting:
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
   ```
   This blocks unsolicited inbound by default; loopback traffic is unaffected.

### Option B — Public Showdown server

Use `pokeagentshowdown.com` (or `play.pokemonshowdown.com`) with a real account. Add `--USERNAME` and `--PASSWORD` flags (see `local_1v1.py` for the parameter names). Rate limited, broadcasts battles, requires registration.

## What `--no-security` does on the Showdown side

It disables features designed for public deployment: external account auth, rate limits, chat moderation, CAPTCHA. **It does not** open additional ports, change the bind address, or grant shell/file access. The simulator stays sandboxed in Node. Safe for *local* use; not safe to combine with `0.0.0.0` binding.

## Why not just run live in CI?

- Each Pokemon battle takes 30s–5min wall time.
- `LocalSim.deepcopy` (inside MCTSBot) is the cost driver, so MCTSBot games are toward the long end.
- A 100-game tournament can take 2–8 hours depending on bot mix.
- Run on a dedicated machine, not the laptop you're using for other work.

## Bots currently wired in

`gen1_agent`, `mcts`, `random`, `max_power`, `abyssal`, `one_step`, plus the LLM-backed `pokechamp`, `pokellmon`, and `vgc`.

## Reading the results

```python
import pandas as pd
df = pd.read_csv("tournament_results/mcts_vs_random_gen1ou_20260527_120000.csv")
df["winner"].value_counts()
df["wall_time_s"].describe()
```

Aggregate W/D/L is printed at the end of the run; the CSV is for per-game analysis (e.g., does MCTS get better as it sees more team archetypes? Does win rate drift with random seed?).
