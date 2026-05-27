# pokemon-data MCP

A small **Model Context Protocol** server that exposes [pokechamp](https://github.com/yeungjosh/pokechamp)'s team files and portfolio test results as tools any MCP client can call — Claude Code, Cursor, Codex, Gemini CLI, OpenClaw, etc.

Once registered, asking Claude *"what teams does pokechamp have?"* makes a structured tool call (`list_teams()`) instead of shelling out to `ls`, which is more reliable and works across sessions without re-explaining the repo layout.

---

## What is MCP?

**Model Context Protocol** is a JSON-RPC schema (over stdio or HTTP) that standardises how LLM clients call external tools. An MCP server advertises a set of typed tools; the client (Claude, Cursor, …) decides when to call them based on the user's message.

```
┌──────────────┐   tool call (JSON-RPC)    ┌───────────────────────┐
│  Claude Code │ ───────────────────────▶  │  pokemon-data server  │
│              │                            │  (this repo)          │
│              │ ◀───────────────────────  │   ↓ reads from disk   │
└──────────────┘     result (JSON)          └───────────────────────┘
                                                     │
                                                     ▼
                                            pokechamp/teams/*.txt
                                            pokechamp/test_results/*.json
```

Compared to letting the model shell out (`ls`, `cat`):

- **Typed inputs/outputs** — the model can't fat-finger a path
- **Cross-session** — the schema is the same every conversation
- **Cross-client** — same server works in Claude, Cursor, Codex
- **Auditable** — every call shows up in the client's tool log

---

## Tools

All five tools are stateless reads — no writes, no network. Safe to expose.

### `list_teams() → list[str]`
List Gen 1 OU team filenames in `pokechamp/teams/`.

```python
>>> list_teams()
['gen1ou_balanced.txt', 'gen1ou_offensive.txt', 'gen1ou_sleep_focus.txt']
```

### `get_team(name: str) → str`
Return the raw contents of a team file. Errors if `name` is outside `teams/`.

```python
>>> get_team("gen1ou_balanced.txt")
"Tauros\nAbility: ...\n\nSnorlax\n..."
```

### `list_test_results(limit: int = 20) → list[str]`
Most recent portfolio test result files, newest first.

```python
>>> list_test_results(limit=5)
['portfolio_test_20260527_103045.json',
 'portfolio_test_20260527_103045.md',
 'portfolio_test_20260526_180100.json',
 ...]
```

### `get_test_result(filename: str) → dict | str`
JSON files are parsed; `.md` / `.txt` are returned as strings.

```python
>>> get_test_result("portfolio_test_20260527_103045.json")
{'matchups': [{'opponent': 'random', 'wins': 17, 'n': 20, ...}, ...]}
```

### `summarize_latest_run() → dict`
Convenience: latest JSON result + its filename, or `{"error": ...}` if none exist.

```python
>>> summarize_latest_run()
{'file': 'portfolio_test_20260527_103045.json', 'data': {...}}
```

---

## Install

This MCP lives inside the pokechamp repo at `pokechamp/mcp/`. From the pokechamp root:

```bash
cd mcp
uv venv                                  # one-time
uv pip install 'mcp[cli]>=1.2.0'         # one-time
```

Verify the tools work standalone:

```bash
uv run python -c "from server import list_teams; print(list_teams())"
# → ['gen1ou_balanced.txt', 'gen1ou_offensive.txt', 'gen1ou_sleep_focus.txt']
```

---

## Register with Claude Code

**Option A — CLI** (recommended):

```bash
claude mcp add pokemon-data -- \
    uv run --directory <path-to-pokechamp>/mcp \
    python server.py
```

**Option B — settings.json**:

```json
{
  "mcpServers": {
    "pokemon-data": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "<path-to-pokechamp>/mcp",
        "python", "server.py"
      ]
    }
  }
}
```

Restart the Claude session. Confirm with `claude mcp list` — should show `pokemon-data: connected`.

### Register with other clients

- **Cursor**: same JSON shape, in Cursor settings under MCP servers
- **Codex CLI**: `codex mcp add pokemon-data -- uv run --directory <path> python server.py`
- **Gemini CLI**: see your client's docs; same `command` + `args` shape

---

## Usage examples

Once registered, the server fires automatically when the model judges it relevant. Sample prompts:

| You ask | Claude calls | What you get back |
|---|---|---|
| *"What teams does pokechamp have?"* | `list_teams()` | All 3 team filenames |
| *"Show me the balanced team."* | `get_team("gen1ou_balanced.txt")` | Full team contents |
| *"What's in the latest portfolio run?"* | `summarize_latest_run()` | Newest JSON + summary |
| *"How did gen1_agent do vs random last run?"* | `summarize_latest_run()` + filter | Win-rate for the random matchup |
| *"Compare the last two test runs."* | `list_test_results(2)` + 2× `get_test_result()` | Side-by-side comparison |
| *"What teams produced >80% win rate?"* | Multiple tool calls, joined | Filtered list |

The model picks the right tool from the description text — you don't name them in your prompt.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `claude mcp list` shows `disconnected` | Server crashed on start | Run `uv run python server.py` standalone, read the traceback |
| `ModuleNotFoundError: No module named 'mcp'` | Skipped `uv pip install` | `cd` to repo, `uv pip install 'mcp[cli]>=1.2.0'` |
| Tools return `[]` for results | `pokechamp/test_results/` is empty | Run `./run_portfolio_tests.sh` in the pokechamp repo first |
| `ValueError: Team file not found` | Wrong filename | Use `list_teams()` first to get exact filenames |
| Path errors in tool output | This file was moved outside `pokechamp/mcp/` | `POKECHAMP_ROOT` resolves relative to `server.py`; restore the directory layout or hard-code the path |

---

## How to extend

Add a tool by writing a new function decorated with `@mcp.tool()`:

```python
@mcp.tool()
def get_team_pokemon(name: str) -> list[str]:
    """Return just the Pokémon species names from a team file."""
    text = get_team(name)
    return [
        line.split()[0]
        for line in text.splitlines()
        if line and not line.startswith((" ", "-", "EV", "IV"))
    ]
```

Restart the MCP (kill the process; Claude reconnects). The tool's docstring becomes its description — the LLM uses that to decide when to call it, so write descriptions that signal *when to use the tool*, not just *what it does*.

---

## Project layout

```
pokechamp/
├── mcp/
│   ├── server.py        # All tool definitions (single file)
│   ├── pyproject.toml   # mcp[cli] dependency
│   ├── README.md        # this file
│   ├── uv.lock          # locked deps
│   └── .venv/           # uv-managed virtualenv (gitignored)
├── teams/               # ← read by list_teams() / get_team()
├── test_results/        # ← read by list_test_results() / get_test_result()
└── ...
```

Paths in `server.py` are resolved relative to the file (`Path(__file__).parent.parent`), so the server works out of the box as long as it stays inside `pokechamp/mcp/`.

---

## Why this exists

The benchmark commands (run the portfolio suite, swap opponents, change formats) are documented in the main `PORTFOLIO_TESTING.md`. This MCP exposes the *data* those commands produce — teams and results — as typed tools any LLM client can query.

Useful when an agent needs to compare runs, filter results, or feed team contents into another step (e.g., a damage calculator) without re-reading directory listings every session.
