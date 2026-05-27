"""
Bots package for PokéChamp framework.

This package contains all custom bot implementations that can be used
for testing and battling in the PokéChamp framework.
"""

from .mcts_bot import MCTSBot
from .starter_kit_bot import StarterKitBot

__all__ = ['MCTSBot', 'StarterKitBot']
