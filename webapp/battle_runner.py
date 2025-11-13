"""
Battle Runner Module

Executes Pokemon battles and streams results via WebSocket
"""

import asyncio
import sys
import os
from datetime import datetime
import traceback

# Add parent directory to import pokechamp modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poke_env.player import RandomPlayer
from poke_env.player.baselines import AbyssalPlayer, MaxPowerPlayer, OneStepPlayer
from pokechamp.llm_player import LLMPlayer

# Try to import custom bots
try:
    from bots.gen1_agent import Gen1Agent
    GEN1_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import Gen1Agent: {e}")
    GEN1_AVAILABLE = False

try:
    from bots.starter_kit_bot import StarterKitBot
    STARTER_KIT_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import StarterKitBot: {e}")
    STARTER_KIT_AVAILABLE = False


class BattleRunner:
    """Manages battle execution and streaming"""

    def __init__(self, socketio):
        self.socketio = socketio
        self.active_battles = {}
        self.update_stats = None
        self.record_battle = None

    def create_player(self, agent_name, battle_format="gen1ou"):
        """Create a player instance based on agent name"""
        try:
            if agent_name == 'gen1_agent' and GEN1_AVAILABLE:
                return Gen1Agent(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'abyssal':
                return AbyssalPlayer(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'max_power':
                return MaxPowerPlayer(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'one_step':
                return OneStepPlayer(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'random':
                return RandomPlayer(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'pokechamp':
                # For demo purposes, use a heuristic or simple player
                # LLM players require API keys which may not be configured
                return AbyssalPlayer(battle_format=battle_format, max_concurrent_battles=1)
            elif agent_name == 'starter_kit' and STARTER_KIT_AVAILABLE:
                return StarterKitBot(battle_format=battle_format, max_concurrent_battles=1)
            else:
                # Default to random player
                return RandomPlayer(battle_format=battle_format, max_concurrent_battles=1)
        except Exception as e:
            print(f"Error creating player {agent_name}: {e}")
            # Fallback to random player
            return RandomPlayer(battle_format=battle_format, max_concurrent_battles=1)

    def emit_battle_event(self, battle_id, event_type, data):
        """Emit battle event via WebSocket"""
        try:
            self.socketio.emit('battle_event', {
                'battle_id': battle_id,
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error emitting event: {e}")

    def get_battle_state(self, battle):
        """Extract battle state for visualization"""
        try:
            state = {
                'turn': battle.turn,
                'player': self.get_pokemon_state(battle.active_pokemon),
                'opponent': self.get_pokemon_state(battle.opponent_active_pokemon),
                'player_team': [self.get_pokemon_state(p) for p in battle.team.values()],
                'opponent_team': [self.get_pokemon_state(p) for p in battle.opponent_team.values()],
                'weather': str(battle.weather) if battle.weather else None,
                'fields': [str(f) for f in battle.fields],
            }
            return state
        except Exception as e:
            print(f"Error getting battle state: {e}")
            return {'error': str(e)}

    def get_pokemon_state(self, pokemon):
        """Extract Pokemon state"""
        if not pokemon:
            return None

        try:
            return {
                'species': pokemon.species,
                'level': pokemon.level,
                'hp': pokemon.current_hp,
                'max_hp': pokemon.max_hp,
                'hp_fraction': pokemon.current_hp_fraction,
                'status': str(pokemon.status) if pokemon.status else None,
                'types': [str(t) for t in pokemon.types],
                'active': pokemon.active,
                'fainted': pokemon.fainted,
                'stats': {
                    'atk': pokemon.base_stats.get('atk', 0),
                    'def': pokemon.base_stats.get('def', 0),
                    'spa': pokemon.base_stats.get('spa', 0),
                    'spd': pokemon.base_stats.get('spd', 0),
                    'spe': pokemon.base_stats.get('spe', 0),
                },
                'moves': [m.id for m in pokemon.moves.values()] if pokemon.moves else []
            }
        except Exception as e:
            print(f"Error getting pokemon state: {e}")
            return {'species': 'Unknown', 'error': str(e)}

    def run_battle(self, battle_id, player1_name, player2_name, battle_format="gen1ou"):
        """Run a battle and stream results"""
        try:
            print(f"Starting battle: {battle_id}")
            print(f"  Player 1: {player1_name}")
            print(f"  Player 2: {player2_name}")
            print(f"  Format: {battle_format}")

            # Emit battle start
            self.emit_battle_event(battle_id, 'battle_start', {
                'player1': player1_name,
                'player2': player2_name,
                'format': battle_format
            })

            # Create players
            player1 = self.create_player(player1_name, battle_format)
            player2 = self.create_player(player2_name, battle_format)

            # Run the battle using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Start the battle
                result = loop.run_until_complete(
                    self._run_battle_async(battle_id, player1, player2, player1_name, player2_name)
                )

                # Emit battle end
                winner = player1_name if result['winner'] == 1 else player2_name
                loser = player2_name if result['winner'] == 1 else player1_name

                self.emit_battle_event(battle_id, 'battle_end', {
                    'winner': winner,
                    'loser': loser,
                    'turns': result.get('turns', 0),
                    'player1_final': result.get('player1_final'),
                    'player2_final': result.get('player2_final')
                })

                # Update stats
                if self.update_stats:
                    self.update_stats(winner, loser)

                # Record battle
                if self.record_battle:
                    self.record_battle({
                        'battle_id': battle_id,
                        'player1': player1_name,
                        'player2': player2_name,
                        'winner': winner,
                        'turns': result.get('turns', 0),
                        'format': battle_format,
                        'timestamp': datetime.now().isoformat()
                    })

                print(f"Battle {battle_id} completed: {winner} wins!")

            finally:
                loop.close()

        except Exception as e:
            print(f"Error running battle {battle_id}: {e}")
            traceback.print_exc()
            self.emit_battle_event(battle_id, 'battle_error', {
                'error': str(e)
            })

    async def _run_battle_async(self, battle_id, player1, player2, player1_name, player2_name):
        """Run battle asynchronously"""
        try:
            # Challenge player2
            await player1.battle_against(player2, n_battles=1)

            # Get the battle result
            battles_player1 = list(player1._battles.values())
            if battles_player1:
                battle = battles_player1[0]

                # Determine winner
                if battle.won:
                    winner = 1
                elif battle.lost:
                    winner = 2
                else:
                    winner = 0  # Tie/Unknown

                return {
                    'winner': winner,
                    'turns': battle.turn,
                    'player1_final': self.get_battle_state(battle),
                    'player2_final': None  # Would need opponent's battle object
                }
            else:
                return {'winner': 0, 'turns': 0}

        except Exception as e:
            print(f"Error in async battle: {e}")
            traceback.print_exc()
            return {'winner': 0, 'turns': 0, 'error': str(e)}
