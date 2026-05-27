"""Sanity tests for the MCTS bot.

These tests focus on the parts we can exercise without a Showdown server:
  * The vendored MCTS core still solves tic-tac-toe correctly.
  * MCTSBot imports, instantiates, and exposes the right Player interface.
  * The PokemonGame adapter handles "no opponent visible moves" without
    crashing (the empty-rollout corner case that matters in early-game).

A full battle test requires Pokemon Showdown and lives in the project's
integration suite, not here.

Run with: python -m bots.test_mcts_bot
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ._mcts_core import MCTS


# ---------- MCTS core sanity (vendored from cs221-crash-course) ----------

@dataclass(frozen=True)
class _TTTState:
    board: tuple  # 9 cells: 0 empty, +1 X, -1 O

    @property
    def player(self) -> int:
        return 1 if self.board.count(0) % 2 == 1 else -1


_WINS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


class _TicTacToe:
    def initial_state(self):
        return _TTTState(board=(0,) * 9)

    def current_player(self, s):
        return s.player

    def legal_actions(self, s):
        if self._winner(s.board):
            return []
        return [i for i, v in enumerate(s.board) if v == 0]

    def apply(self, s, a):
        b = list(s.board)
        b[a] = s.player
        return _TTTState(board=tuple(b))

    def is_terminal(self, s):
        return self._winner(s.board) != 0 or 0 not in s.board

    def reward(self, s):
        return float(self._winner(s.board))

    @staticmethod
    def _winner(board):
        for a, b, c in _WINS:
            tot = board[a] + board[b] + board[c]
            if tot == 3:
                return 1
            if tot == -3:
                return -1
        return 0


def test_vendored_mcts_takes_immediate_win():
    game = _TicTacToe()
    # X plays index 2 to complete row 0
    board = ( 1,  1, 0,
              0,  0, 0,
             -1, -1, 0)
    state = _TTTState(board=board)
    mcts = MCTS(game, n_iterations=1000, rng=random.Random(0))
    action = mcts.choose(state)
    assert action == 2, f"expected 2, got {action}"
    print("PASS: vendored MCTS takes immediate win")


def test_vendored_mcts_vs_random_winrate():
    game = _TicTacToe()
    rng = random.Random(42)
    mcts = MCTS(game, n_iterations=200, rng=random.Random(0))

    wins = draws = losses = 0
    for _ in range(30):
        state = game.initial_state()
        while not game.is_terminal(state):
            if state.player == 1:
                action = mcts.choose(state)
            else:
                action = rng.choice(game.legal_actions(state))
            state = game.apply(state, action)
        r = game.reward(state)
        if r > 0:
            wins += 1
        elif r < 0:
            losses += 1
        else:
            draws += 1

    print(f"vendored MCTS as X vs random: {wins} W / {draws} D / {losses} L (of 30)")
    assert wins + draws >= 28, "vendored MCTS shouldn't lose >2/30 to random"
    print("PASS: vendored MCTS beats random")


# ---------- MCTSBot structural sanity ----------

def test_mcts_bot_imports_and_has_player_interface():
    from .mcts_bot import MCTSBot

    # Don't construct a real Player (needs poke-env Showdown account). Just
    # verify the class is a Player subclass with the right methods.
    from poke_env.player.player import Player

    assert issubclass(MCTSBot, Player), "MCTSBot must extend Player"
    assert hasattr(MCTSBot, "choose_move"), "MCTSBot must override choose_move"
    print("PASS: MCTSBot has the right Player interface")


def test_pokemon_game_handles_no_legal_actions():
    """Edge case: legal_actions on a state with no available moves and
    no available switches should return an empty list, not crash."""
    from poke_env.environment.battle import Battle  # noqa: F401  (forced import to verify availability)
    from .mcts_bot import PokemonGame

    class _DummyBattle:
        available_moves: list = []
        available_switches: list = []
        opponent_active_pokemon = None
        team: dict = {}
        opponent_team: dict = {}

        def is_terminal(self):
            return True

    class _DummySim:
        def __init__(self):
            self.battle = _DummyBattle()

        def is_terminal(self):
            return True

    game = PokemonGame(sim=_DummySim(), rng=random.Random(0), max_depth=1)
    state = game.initial_state()
    assert game.legal_actions(state) == []
    assert game.is_terminal(state) is True
    assert game.reward(state) == 0.0
    print("PASS: PokemonGame handles empty-action edge case")


if __name__ == "__main__":
    test_vendored_mcts_takes_immediate_win()
    test_vendored_mcts_vs_random_winrate()
    test_mcts_bot_imports_and_has_player_interface()
    test_pokemon_game_handles_no_legal_actions()
    print("\nAll tests passed.")
