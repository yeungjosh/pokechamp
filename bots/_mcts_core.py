"""Generic UCT MCTS for two-player zero-sum games.

Vendored from cs221-crash-course/assignments/mcts/. Kept dependency-free
(stdlib only) so it works inside pokechamp without adding any imports.

The Pokemon-specific adapter lives in mcts_bot.py.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Callable, List


@dataclass
class _Node:
    state: Any
    parent: "_Node | None" = None
    action_from_parent: Any = None
    children: "dict[Any, _Node]" = field(default_factory=dict)
    untried_actions: List[Any] = field(default_factory=list)
    visits: int = 0
    total_reward: float = 0.0

    @property
    def is_fully_expanded(self) -> bool:
        return not self.untried_actions


class MCTS:
    """UCT-based MCTS.

    Game protocol expected (duck-typed):
      - initial_state() -> state
      - current_player(state) -> int          (+1 or -1)
      - legal_actions(state) -> list[action]
      - apply(state, action) -> next_state
      - is_terminal(state) -> bool
      - reward(state) -> float                (in [-1, 1], from player 1's view)
    """

    def __init__(
        self,
        game,
        n_iterations: int = 200,
        c: float = math.sqrt(2),
        rng: "random.Random | None" = None,
        rollout_policy: "Callable[[Any], Any] | None" = None,
        time_budget_s: "float | None" = None,
    ) -> None:
        self.game = game
        self.n_iterations = n_iterations
        self.c = c
        self.rng = rng or random.Random()
        self.rollout_policy = rollout_policy
        self.time_budget_s = time_budget_s

    def choose(self, state) -> Any:
        root = _Node(state=state)
        root.untried_actions = list(self.game.legal_actions(state))

        import time
        deadline = (time.monotonic() + self.time_budget_s) if self.time_budget_s else None

        for i in range(self.n_iterations):
            if deadline is not None and time.monotonic() > deadline:
                break
            leaf = self._select(root)
            child = self._expand(leaf) if not self.game.is_terminal(leaf.state) else leaf
            reward = self._rollout(child.state)
            self._backprop(child, reward)

        if not root.children:
            # All actions terminal (or no iterations ran). Fall back.
            return root.untried_actions[0] if root.untried_actions else None

        best_action, _ = max(root.children.items(), key=lambda kv: kv[1].visits)
        return best_action

    def _select(self, node: _Node) -> _Node:
        while node.is_fully_expanded and not self.game.is_terminal(node.state) and node.children:
            node = self._best_uct_child(node)
        return node

    def _expand(self, node: _Node) -> _Node:
        action = node.untried_actions.pop()
        next_state = self.game.apply(node.state, action)
        child = _Node(state=next_state, parent=node, action_from_parent=action)
        child.untried_actions = list(self.game.legal_actions(next_state))
        node.children[action] = child
        return child

    def _rollout(self, state) -> float:
        if self.rollout_policy is not None:
            return self.rollout_policy(state)
        # Default: uniform random until terminal.
        while not self.game.is_terminal(state):
            actions = self.game.legal_actions(state)
            if not actions:
                break
            state = self.game.apply(state, self.rng.choice(actions))
        return self.game.reward(state)

    def _backprop(self, node: _Node, reward: float) -> None:
        while node is not None:
            node.visits += 1
            mover = -self.game.current_player(node.state)
            node.total_reward += reward * mover
            node = node.parent

    def _best_uct_child(self, node: _Node) -> _Node:
        log_parent = math.log(node.visits)
        return max(
            node.children.values(),
            key=lambda ch: (ch.total_reward / ch.visits)
            + self.c * math.sqrt(log_parent / ch.visits),
        )
