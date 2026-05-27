"""MCTSBot — UCT Monte Carlo Tree Search for Pokemon battles.

Adapter pattern:
  * `PokemonGame` wraps `LocalSim` so it satisfies the duck-typed Game
    protocol expected by `_mcts_core.MCTS`.
  * `MCTSBot` is a poke_env `Player` that builds a `PokemonGame` per turn
    and asks the search for the best `BattleOrder`.

Limitations (consciously chosen for v1):
  * Depth-limited rollouts (default 3 plies, ~1.5 turns) — full battles
    are too expensive for >100 LocalSim deep-copies per move.
  * Opponent action sampled uniformly from their *visible* moves. A future
    version should plug in `pokechamp/bayesian/` for proper opponent move
    prediction.
  * Reward = clamp(HP differential at leaf, -1, 1). Faint of opponent
    contributes +1, our faint contributes -1.
  * No stochastic outcome modelling (accuracy / crit / damage roll). Each
    `LocalSim.step` uses point estimates.

These limits are documented in tests/ and called out in commit messages
so they're easy to lift later.
"""

from __future__ import annotations

import math
import random
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional, Union

from poke_env.environment.battle import Battle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.player.battle_order import BattleOrder
from poke_env.player.local_simulation import LocalSim
from poke_env.player.player import Player

from ._mcts_core import MCTS

Action = Union[Move, Pokemon]


@dataclass
class _GameState:
    sim: LocalSim
    depth: int


class PokemonGame:
    """Adapter that lets MCTS treat a `LocalSim` as a two-player game.

    Player 1 = us. After each of our moves the adapter also commits an
    opponent move (sampled), so the game alternates "we move + they move"
    inside a single `apply()` call — the search tree is effectively a
    sequence of our decisions with opponent stochasticity baked in.
    """

    def __init__(
        self,
        sim: LocalSim,
        rng: Optional[random.Random] = None,
        max_depth: int = 3,
    ) -> None:
        self._initial = _GameState(sim=sim, depth=0)
        self.rng = rng or random.Random()
        self.max_depth = max_depth
        self._initial_hp_diff = _hp_differential(sim.battle)

    # ----- Game protocol -----

    def initial_state(self) -> _GameState:
        return self._initial

    def current_player(self, state: _GameState) -> int:
        # We absorb opponent moves into `apply`, so from MCTS's view it's
        # always us choosing. Returning a constant +1 is fine.
        return 1

    def legal_actions(self, state: _GameState) -> List[Action]:
        battle = state.sim.battle
        actions: List[Action] = []
        actions.extend(battle.available_moves)
        actions.extend(battle.available_switches)
        return actions

    def apply(self, state: _GameState, action: Action) -> _GameState:
        next_sim = deepcopy(state.sim)
        our_order = BattleOrder(order=action)
        their_order = self._sample_opponent_action(next_sim.battle)
        try:
            next_sim.step(our_order, their_order)
        except Exception:
            # LocalSim has a lot of edge cases (status moves, switches into
            # fainted mons, etc.). If a step blows up, treat the line as
            # terminal so the search just doesn't pick it.
            pass
        return _GameState(sim=next_sim, depth=state.depth + 1)

    def is_terminal(self, state: _GameState) -> bool:
        return state.depth >= self.max_depth or state.sim.is_terminal()

    def reward(self, state: _GameState) -> float:
        delta = _hp_differential(state.sim.battle) - self._initial_hp_diff
        return max(-1.0, min(1.0, delta))

    # ----- Internals -----

    def _sample_opponent_action(self, battle: Battle) -> Optional[BattleOrder]:
        opp = battle.opponent_active_pokemon
        if opp is None or opp.fainted:
            return None
        candidate_moves = list(opp.moves.values())
        if not candidate_moves:
            return None
        return BattleOrder(order=self.rng.choice(candidate_moves))


def _hp_differential(battle: Battle) -> float:
    """Sum of our HP fractions minus opponent's, normalized roughly to [-1, 1].

    Six mons on each side, fractions in [0, 1], so the raw delta is in
    [-6, 6]. Dividing by 6 puts a full sweep at ±1.0 and a one-mon swing
    at ±~0.17 — empirically a good shape for MCTS reward.
    """
    ours = sum(m.current_hp_fraction for m in battle.team.values())
    theirs = sum(m.current_hp_fraction for m in battle.opponent_team.values())
    return (ours - theirs) / 6.0


class MCTSBot(Player):
    """Player that picks moves via UCT MCTS over LocalSim rollouts."""

    def __init__(
        self,
        *args,
        n_iterations: int = 100,
        max_depth: int = 3,
        time_budget_s: float = 10.0,
        rng_seed: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.n_iterations = n_iterations
        self.max_depth = max_depth
        self.time_budget_s = time_budget_s
        self._rng = random.Random(rng_seed)

        # LocalSim's static data (move effects, ability effects, etc.) is
        # cached project-wide. Load lazily so importing this module doesn't
        # require all the cache files to exist.
        self._localsim_kwargs: Optional[dict] = None

    def _ensure_localsim_kwargs(self) -> dict:
        if self._localsim_kwargs is not None:
            return self._localsim_kwargs

        from pokechamp.data_cache import (
            get_cached_ability_effect,
            get_cached_item_effect,
            get_cached_move_effect,
            get_cached_pokemon_ability_dict,
            get_cached_pokemon_item_dict,
            get_cached_pokemon_move_dict,
        )
        from poke_env.data.gen_data import GenData

        self._localsim_kwargs = dict(
            move_effect=get_cached_move_effect(),
            pokemon_move_dict=get_cached_pokemon_move_dict(),
            ability_effect=get_cached_ability_effect(),
            pokemon_ability_dict=get_cached_pokemon_ability_dict(),
            item_effect=get_cached_item_effect(),
            pokemon_item_dict=get_cached_pokemon_item_dict(),
            gen=GenData.from_format(self.format),
            _dynamax_disable=True,
            format=self.format,
        )
        return self._localsim_kwargs

    def choose_move(self, battle: Battle) -> BattleOrder:
        # Forced moves: skip the search.
        if not battle.available_moves and battle.available_switches:
            return self.create_order(battle.available_switches[0])
        if not battle.available_moves and not battle.available_switches:
            return self.choose_random_move(battle)

        sim = LocalSim(battle=deepcopy(battle), **self._ensure_localsim_kwargs())
        game = PokemonGame(sim=sim, rng=self._rng, max_depth=self.max_depth)
        search = MCTS(
            game=game,
            n_iterations=self.n_iterations,
            rng=self._rng,
            time_budget_s=self.time_budget_s,
        )
        action = search.choose(game.initial_state())
        if action is None:
            return self.choose_random_move(battle)
        return self.create_order(action)
