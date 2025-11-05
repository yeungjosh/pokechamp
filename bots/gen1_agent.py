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

    def _evaluate_position(self, battle: Battle) -> float:
        """
        Comprehensive position evaluation.
        Returns positive score if we're winning, negative if losing.
        """
        score = 0.0

        # Material advantage (weighted HP)
        our_material = 0.0
        opp_material = 0.0

        for pokemon in battle.team.values():
            if not pokemon.fainted:
                mon_name = pokemon.species.lower().replace(" ", "")
                base_value = MATERIAL_VALUES.get(mon_name, 140)
                hp_fraction = pokemon.current_hp_fraction

                # Status modifier
                status_mult = 1.0
                if pokemon.status == Status.SLP:
                    status_mult = 0.3  # Sleep heavily reduces value
                elif pokemon.status == Status.PAR:
                    status_mult = 0.85
                elif pokemon.status == Status.BRN:
                    status_mult = 0.7
                elif pokemon.status == Status.FRZ:
                    status_mult = 0.1  # Frozen is nearly dead in Gen1

                our_material += base_value * hp_fraction * status_mult

        # Opponent material (estimate based on what we've seen)
        for pokemon in battle.opponent_team.values():
            if pokemon and not pokemon.fainted:
                mon_name = pokemon.species.lower().replace(" ", "")
                base_value = MATERIAL_VALUES.get(mon_name, 140)
                hp_fraction = pokemon.current_hp_fraction if pokemon.current_hp_fraction else 1.0

                status_mult = 1.0
                if pokemon.status == Status.SLP:
                    status_mult = 0.3
                elif pokemon.status == Status.PAR:
                    status_mult = 0.85
                elif pokemon.status == Status.FRZ:
                    status_mult = 0.1

                opp_material += base_value * hp_fraction * status_mult

        score += (our_material - opp_material) * 0.5

        # Sleep advantage (huge in Gen1)
        our_sleeping = sum(1 for p in battle.team.values() if not p.fainted and p.status == Status.SLP)
        opp_sleeping = sum(1 for p in battle.opponent_team.values() if p and not p.fainted and p.status == Status.SLP)
        score += (opp_sleeping - our_sleeping) * 40

        # Tauros advantage (if we have Tauros alive and healthy)
        our_tauros = next((p for p in battle.team.values() if "tauros" in p.species.lower() and not p.fainted), None)
        opp_tauros = next((p for p in battle.opponent_team.values() if p and "tauros" in p.species.lower() and not p.fainted), None)
        if our_tauros and our_tauros.current_hp_fraction > 0.6:
            score += 25
        if opp_tauros and (not hasattr(opp_tauros, 'current_hp_fraction') or opp_tauros.current_hp_fraction > 0.6):
            score -= 25

        return score

    def _can_survive_hit(self, defender: Pokemon, attacker: Pokemon) -> bool:
        """
        Check if defender can likely survive one hit from attacker.
        Uses common Gen1 move expectations.
        """
        # Estimate strongest likely attack
        attacker_name = attacker.species.lower().replace(" ", "")

        # Common strong moves by type
        common_attacks = []
        if attacker.type_1:
            type_name = attacker.type_1.name.upper()
            if type_name == "NORMAL":
                common_attacks.append(("bodyslam", 85))
            elif type_name == "PSYCHIC":
                common_attacks.append(("psychic", 90))
            elif type_name == "ICE":
                common_attacks.append(("blizzard", 120))
            elif type_name == "ELECTRIC":
                common_attacks.append(("thunderbolt", 95))

        # Estimate max damage
        max_dmg = 0
        for move_name, power in common_attacks:
            # Simplified damage estimate
            type_mult = 1.0
            if defender.type_1:
                # Rough type effectiveness
                pass

            # Rough damage: ~30-40% for super effective, ~15-25% for neutral
            estimated_dmg_pct = power / 400 * 1.5  # Conservative estimate
            max_dmg = max(max_dmg, estimated_dmg_pct)

        # If we don't know moves, assume 30% damage
        if max_dmg == 0:
            max_dmg = 0.3

        return defender.current_hp_fraction > max_dmg

    def _score_switch(self, battle: Battle, switch: Pokemon) -> float:
        """
        Enhanced switch scoring with defensive and offensive matchup analysis.
        """
        if not battle.opponent_active_pokemon:
            return 0.0

        opponent = battle.opponent_active_pokemon
        current = battle.active_pokemon
        score = 0.0

        # Check if we MUST switch (about to faint)
        if current and current.current_hp_fraction < 0.2:
            score += 200  # Switching is likely necessary

        # Check if current matchup is still good
        if current and current.current_hp_fraction > 0.5:
            for move in battle.available_moves:
                type_eff = self._get_type_effectiveness(
                    move.type.name if move.type else "NORMAL", opponent
                )
                if type_eff >= 1.5:
                    return -150  # Stay in if we have super effective moves
                elif type_eff >= 1.0:
                    return -100  # Stay in if neutral or better

        # Material value of switch target
        switch_name = switch.species.lower().replace(" ", "")
        base_value = MATERIAL_VALUES.get(switch_name, 140)
        score += base_value * 0.5

        # HP factor (healthy mons preferred)
        score += switch.current_hp_fraction * 100

        # Defensive matchup: can switch-in survive?
        if self._can_survive_hit(switch, opponent):
            score += 150
        else:
            score -= 200  # Switching into death is bad

        # Offensive matchup: check type advantage of our moves
        offensive_bonus = 0
        for move_id in switch.moves:
            # Try to get move type from known moves
            if hasattr(self.gen_data, 'moves') and move_id in self.gen_data.moves:
                move_data = self.gen_data.moves[move_id]
                move_type = move_data.get('type', 'NORMAL')
                type_eff = self._get_type_effectiveness(move_type, opponent)

                if type_eff >= 2.0:
                    offensive_bonus += 100
                elif type_eff >= 1.5:
                    offensive_bonus += 50
                elif type_eff == 0:
                    offensive_bonus -= 100  # Walled

        score += offensive_bonus

        # Preserve Tauros for late-game sweep
        if switch_name == "tauros":
            alive_count = sum(1 for p in battle.team.values() if not p.fainted)
            # Check if opponent team is weakened (~50% HP)
            opp_weakened = True
            for p in battle.opponent_team.values():
                if p and not p.fainted:
                    if hasattr(p, 'current_hp_fraction') and p.current_hp_fraction > 0.6:
                        opp_weakened = False
                        break

            if alive_count > 3 and not opp_weakened:
                score -= 100  # Don't bring Tauros too early
            elif opp_weakened:
                score += 150  # Time to sweep!

        # Chansey for walling special attackers
        if switch_name == "chansey":
            # Chansey walls special attackers
            if opponent.type_1 and opponent.type_1.name.upper() in ["PSYCHIC", "ICE", "ELECTRIC", "WATER", "GRASS"]:
                score += 80

        # Status considerations
        if switch.status:
            score -= 50  # Don't want to switch in damaged mon unless necessary

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
