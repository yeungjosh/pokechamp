"""Pokemon-data MCP server.

Exposes pokechamp teams and portfolio test results as MCP tools so multiple
LLM clients (Claude Code, Cursor, Codex, ...) can query them as structured
tools instead of shelling out.

Lives under pokechamp/mcp/, so paths are resolved relative to this file.
"""

from pathlib import Path
import json

from mcp.server.fastmcp import FastMCP

POKECHAMP_ROOT = Path(__file__).resolve().parent.parent
TEAMS_DIR = POKECHAMP_ROOT / "teams"
RESULTS_DIR = POKECHAMP_ROOT / "test_results"

mcp = FastMCP("pokemon-data")


@mcp.tool()
def list_teams() -> list[str]:
    """List all available Gen 1 OU team files in pokechamp/teams/."""
    if not TEAMS_DIR.exists():
        return []
    return sorted(p.name for p in TEAMS_DIR.glob("*.txt"))


@mcp.tool()
def get_team(name: str) -> str:
    """Return the contents of a team file. `name` is the filename (e.g. 'gen1ou_balanced.txt')."""
    path = TEAMS_DIR / name
    if not path.is_file() or path.parent != TEAMS_DIR:
        raise ValueError(f"Team file not found: {name}")
    return path.read_text()


@mcp.tool()
def list_test_results(limit: int = 20) -> list[str]:
    """List the most recent portfolio test result files (newest first)."""
    if not RESULTS_DIR.exists():
        return []
    files = sorted(
        RESULTS_DIR.glob("portfolio_test_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [p.name for p in files[:limit]]


@mcp.tool()
def get_test_result(filename: str) -> dict | str:
    """Return a portfolio test result. JSON files are parsed; .md/.txt returned as text."""
    path = RESULTS_DIR / filename
    if not path.is_file() or path.parent != RESULTS_DIR:
        raise ValueError(f"Result file not found: {filename}")
    if path.suffix == ".json":
        return json.loads(path.read_text())
    return path.read_text()


@mcp.tool()
def summarize_latest_run() -> dict:
    """Return win-rate summary for the most recent JSON portfolio result, if any."""
    results = list_test_results(limit=50)
    json_files = [r for r in results if r.endswith(".json")]
    if not json_files:
        return {"error": "no JSON results found"}
    latest = get_test_result(json_files[0])
    if isinstance(latest, str):
        return {"error": "latest result is not JSON"}
    return {"file": json_files[0], "data": latest}


if __name__ == "__main__":
    mcp.run()
