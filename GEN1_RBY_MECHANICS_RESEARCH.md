# Generation 1 (RBY) Pokémon OU Mechanics - Comprehensive Research

## Table of Contents
1. [Critical Mechanics](#critical-mechanics)
2. [Strategic Elements](#strategic-elements)
3. [Meta Knowledge](#meta-knowledge)
4. [Agent Implementation Guidance](#agent-implementation-guidance)

---

## CRITICAL MECHANICS

### 1. Damage Calculation Formula

**Complete Gen 1 Formula:**
```
Damage = ((((2 × Level × Critical ÷ 5 + 2) × Power × A / D) ÷ 50 + 2) × STAB × Type1 × Type2 × random)
```

**Variables:**
- `Level`: Attacking Pokémon's level (typically 100 in OU)
- `Critical`: 2 for critical hit, 1 otherwise
- `Power`: Move's base power
- `A`: Effective Attack stat (physical) or Special stat (special moves)
- `D`: Effective Defense stat (physical) or Special stat (special moves)
- `STAB`: 1.5 if move type matches user's type, 1 otherwise
- `Type1`, `Type2`: Type effectiveness multipliers (0, 0.5, 1, or 2) for each target type
- `random`: Random integer 217-255, divided by 255 (range: ~0.85 to 1.00)

**Gen 1 Specific Quirks:**
- Critical hits ignore ALL stat modifications (both positive and negative)
- Critical hit damage at Level 100 ≈ 1.95× (not exactly 2×)
- If A or D > 255, both are divided by 4 and rounded down
- Stat modifications cap at 999 (overflow can cause glitches)
- Integer truncation occurs throughout calculation

---

### 2. Type Effectiveness (Gen 1 Type Chart)

**Key Differences from Later Generations:**
- Bug is super effective against Poison
- Poison is super effective against Bug
- Ghost is ineffective (0×) against Psychic (BUG - should be super effective)
- Psychic has no weaknesses except Bug
- No Dark or Steel types exist
- No Fairy type exists

**Immunity Rules:**
- Normal/Fighting: 0× damage to Ghost
- Ghost: 0× damage to Normal
- Ground: 0× damage to Flying
- Electric: 0× damage to Ground
- Poison/Toxic: 0× effect on Poison-type

---

### 3. Critical Hit Mechanics

**Base Formula:**
```
Crit Rate = (Base Speed × 100) / 512
```

**High Crit Moves (Slash, Razor Leaf, Crabhammer, Karate Chop):**
```
Crit Rate = (Base Speed × 100) / 64    # 8× multiplier
```

**Common OU Pokémon Crit Rates:**
- Electrode (140 Speed): 27.34%
- Alakazam (120 Speed): 23.44%
- Tauros (110 Speed): 21.48%
- Starmie (115 Speed): 22.46%
- Chansey (50 Speed): 9.77%
- Snorlax (30 Speed): 5.86%

**Critical Hit Properties:**
- Based on BASE Speed (not current Speed stat)
- Agility doesn't increase crit rate
- Paralysis doesn't decrease crit rate
- Crits ignore Reflect/Light Screen
- Crits ignore stat boosts AND drops
- Maximum crit chance capped at 99.6% (glitch)

**Focus Energy Bug:**
- Focus Energy DECREASES crit rate by 4× instead of increasing
- Formula becomes: `(Base Speed × 100) / 2048`
- Never use Focus Energy in Gen 1

---

### 4. Status Effects

#### Sleep
- Duration: 1-7 turns (determined when inflicted)
- ~1/7 (14.3%) chance to wake each turn
- **Waking uses the turn** - Pokémon cannot act on wake-up turn
- Sleep counter persists between battles
- Fast sleep users can perma-sleep slower Pokémon
- First to sleep opponent gains significant advantage

#### Freeze
- **Permanent until hit by Fire move or switched out**
- Ice-type moves can freeze
- Ice-type Pokémon are immune to freeze
- No chance to thaw naturally
- Extremely powerful status in Gen 1
- Frozen Pokémon cannot act at all

#### Paralysis
- **Speed reduced to 25%** (not 50% like later gens)
- 25% chance to be fully paralyzed each turn
- Electric-types immune to Thunder Wave (but not Body Slam)
- Normal-types immune to Body Slam paralysis
- Ground-types immune to Thunder Wave
- Agility temporarily cures Speed drop until stat reapplication

#### Burn
- Damage: 1/16 max HP per turn
- **Attack reduced by 50%**
- Fire-types immune to burn
- Burn damage doesn't trigger if Pokémon faints opponent
- Toxic counter bug: if previously Toxic'd then Rest'd, burn damage uses Toxic counter

#### Poison (Regular)
- Damage: 1/16 max HP per turn
- Poison-types immune
- Damage doesn't trigger if Pokémon faints opponent

#### Toxic (Badly Poisoned)
- Damage: (n/16) × max HP, where n = turns of Toxic
- Turn 1: 1/16, Turn 2: 2/16, Turn 3: 3/16, etc.
- Counter resets on switch
- Toxic accuracy: 216/256 = 84.4% (not 85%)
- Leech Seed + Toxic combo doubles damage each turn (1/8 → 1/4 → 1/2 → KO in ~5 turns)

---

### 5. Speed Ties and Turn Order

**Turn Order Rules:**
- Higher Speed stat moves first
- Equal Speed: 50/50 random determination each turn
- Same Pokémon in speed tie gets 50/50 each turn (no advantage to winning first tie)

**Speed Modifications:**
- Paralysis: Speed × 0.25
- Agility: Speed × 2 (temporary cure for paralysis)
- No other speed-modifying moves in Gen 1 except rarely-used String Shot, Bubble Beam

**Stat Reapplication Glitch:**
- When opponent uses stat-boosting move, paralysis Speed drop reapplies
- Can stack penalties across turns

---

### 6. Move Accuracy and 1/256 Miss Glitch

**True Accuracy Conversion:**
- Listed 100% = 255/256 = **99.6%** (all moves can miss!)
- Listed 90% = 229/256 = **89.5%**
- Listed 85% = 216/256 = **84.4%** (Toxic, Thunder)
- Listed 70% = 178/256 = **69.5%** (Hypnosis)

**Exceptions (Never Miss):**
- Swift
- Bide
- Transform
- (That's it)

**Effect Probability Quirk:**
- Secondary effects use INVERTED probability
- Body Slam paralysis: 77/256 (30.1%) instead of 76/256

---

### 7. Gen 1 Glitches/Bugs Affecting Competitive Play

#### Hyper Beam Glitch
- **If Hyper Beam KOs opponent, NO recharge needed**
- Makes Hyper Beam extremely powerful in Gen 1
- Also applies if Hyper Beam breaks Substitute
- Changed in later gens (always recharges)

#### Substitute Mechanics
- Substitute blocks most status in Gen 1
- **HP draining moves (Leech Seed, Absorb, etc.) hit through Substitute** (Western RBY only)
- Fixed in Stadium and later gens

#### Wrap/Bind Mechanics
- Binding moves (Wrap, Fire Spin, Clamp, Bind) prevent opponent action for 2-5 turns
- **If faster, can "Wrap lock" opponent indefinitely**
- Dig and Fly banned in most formats due to semi-invulnerability glitch
- Extremely powerful with speed advantage

#### Ghost-Type Bug
- Ghost is supposed to be super effective vs Psychic
- **Due to bug, Ghost is 0× effective vs Psychic**
- Makes Psychic types (especially Alakazam, Exeggutor) dominant
- Ghost moves also have no STAB users with good stats

#### Stat Overflow Glitch
- Stats cap at 999
- Moves fail when stats exceed cap
- Causes -1 deduction, can lead to overflow damage with debuffs
- Relevant for Mewtwo (banned in OU)

#### Recovery Move Failure (255/511 Glitch)
- Recovery moves fail when: `(Max HP - Current HP) = 255` or `511`
- Affects Chansey and Snorlax due to high HP stats
- Byte-overflow glitch

#### Counter Mechanics
- Counter is broken in Gen 1
- Only works against Normal and Fighting moves
- Timing issues make it unreliable

#### Mirror Move
- Copies opponent's last move
- Buggy implementation
- Rarely used competitively

---

### 8. Special Stat (Gen 1 Only)

**Gen 1 has no Special Attack/Special Defense split:**
- One "Special" stat handles both offense and defense
- Makes Pokémon like Chansey (high Special) wall special attackers perfectly
- Special-based attackers (Starmie, Alakazam) can't break each other easily
- Physical/Special split comes in Gen 2

**Implications:**
- Amnesia doubles BOTH Special Attack and Special Defense
- Makes Amnesia users (Slowbro, Snorlax) extremely powerful
- Special drops (from Psychic, Acid Armor) affect both offense and defense

---

## STRATEGIC ELEMENTS

### 1. Lead Matchups

**Top Sleep Leads (Priority Order):**
1. **Gengar** - Fastest sleeper (110 Speed), but fragile and weak otherwise
2. **Jynx** - Fast (95 Speed), moderate utility with Ice/Psychic coverage
3. **Exeggutor** - Slowest (55 Speed) but best support movepool, most utility

**Counter-Leads:**
- **Starmie** - Covers multiple threats, fast, can trade favorably
- **Alakazam** - Deters Gengar, can spread paralysis
- **Chansey** - Tanks sleep users, spreads paralysis

**Lead Principles:**
- First to sleep opponent gains significant advantage
- Sleep advantage > paralysis advantage
- Lead choice dictates early game tempo

---

### 2. Switching Strategy

**Core Switching Concepts:**

#### Chansey as Hub
- Chansey forces all decision-making around status spread
- Paralyzed Chansey can't spread paralysis
- Opponent must decide: accept paralysis or switch

#### Prediction Layers
1. **Level 1:** Stay or switch?
2. **Level 2:** If switch, to what?
3. **Level 3:** Opponent's prediction of your prediction

**Common Switches:**
- **Exeggutor → Chansey** (opponent brings Starmie/Alakazam)
- **Chansey → Snorlax/Tauros** (opponent brings physical attacker)
- **Rhydon/Golem → Zapdos** (opponent uses Earthquake)
- **Starmie → Exeggutor** (opponent uses Thunderbolt)

**Hard Switches vs. Soft Switches:**
- **Hard switch:** Guaranteed safe switch-in (e.g., Exeggutor into Starmie)
- **Soft switch:** Risky but maintains momentum (e.g., Tauros into predicted Chansey)

---

### 3. Speed Tiers (OU Pokémon)

**S-Tier (130+):**
- Electrode: 140 (rarely used)
- Jolteon: 130

**A-Tier (110-120):**
- Alakazam: 120
- Starmie: 115
- Tauros: 110
- Gengar: 110
- Exeggutor: 55 (misleading - sleep nullifies speed advantage)

**B-Tier (90-105):**
- Zapdos: 100
- Jynx: 95

**C-Tier (60-85):**
- Rhydon: 40
- Golem: 45
- Cloyster: 70

**D-Tier (Walls):**
- Chansey: 50
- Snorlax: 30
- Slowbro: 30
- Exeggutor: 55

**Speed Control:**
- Very limited in Gen 1
- Agility: Only viable speed boost
- Paralysis: Primary speed control
- Sleep: Ultimate speed control (opponent can't act)

---

### 4. Common Cores and Team Archetypes

**The "Seven Deadly Staples":**
1. **Tauros** - Physical sweeper/cleaner
2. **Chansey** - Special wall
3. **Snorlax** - Mixed tank/attacker
4. **Exeggutor** - Sleep + special attacker
5. **Starmie** - Fast special attacker/spinner
6. **Alakazam** - Fast special attacker/paralysis spreader
7. **Rhydon/Golem** - Ground-type/Zapdos check

**Common Team Cores:**

#### "Mie-Don-Dos" (Starmie + Rhydon + Zapdos)
- Starmie handles Ground-types
- Rhydon checks Zapdos
- Zapdos checks Fighting/Grass/Bug
- Synergistic coverage

#### "Lax-Tar-Egg" (Snorlax + Starmie + Exeggutor)
- Balanced special/physical core
- Sleep control via Exeggutor
- Snorlax handles physical threats
- Starmie provides speed

#### "Chansey + Physical Attackers"
- Chansey spreads paralysis
- Tauros/Snorlax capitalize on paralyzed foes
- Standard balance core

**Team Archetypes:**

#### Offensive (4+ attackers)
- Focuses on early sleep advantage
- Aggressive paralysis spreading
- Tauros as cleaner
- Less forgiving of mistakes

#### Balanced (3 attackers, 3 support)
- Mix of offense and defense
- Flexible game plan
- Most common archetype

#### Stall (5+ walls)
- Rare in Gen 1
- Relies on Toxic, freeze, sleep
- Very matchup dependent
- Chansey + Exeggutor + Slowbro core

---

## META KNOWLEDGE

### 1. Top Threats (2024-2025 Viability Rankings)

**S1 Tier:**
- **Tauros** - Undisputed king
  - Body Slam (30% paralysis, 21% crit rate)
  - Hyper Beam (no recharge on KO)
  - Earthquake (Rhydon, mirrors)
  - Blizzard (Exeggutor, Rhydon)
  - Role: Revenge killer, late-game cleaner

**S2 Tier:**
- **Snorlax** - #2 most essential
  - Body Slam / Earthquake / Self-Destruct / Hyper Beam
  - Alternative: Reflect / Rest / Body Slam / Self-Destruct
  - Role: Physical tank, status absorber, Explosion user

**A Tier:**
- **Chansey** - Mandatory on every team
  - Ice Beam / Soft-Boiled / Thunder Wave / Thunderbolt
  - Alternative: Reflect / Seismic Toss / Soft-Boiled / Thunder Wave
  - Role: Special wall, paralysis spreader, Starmie check

- **Exeggutor** - Best sleep user + utility
  - Sleep Powder / Psychic / Explosion / Stun Spore
  - Alternative: Sleep Powder / Psychic / Double-Edge / Mega Drain
  - Role: Sleep inducer, special attacker, mixed offense

- **Starmie** - Rising in meta (2024 update)
  - Thunderbolt / Blizzard / Recover / Thunder Wave
  - Alternative: Surf / Thunderbolt / Blizzard / Recover
  - Role: Fast special attacker, paralysis spreader, Chansey breaker

**B1 Tier:**
- **Alakazam** - Fastest paralysis spreader
  - Psychic / Recover / Reflect / Thunder Wave
  - Alternative: Psychic / Seismic Toss / Recover / Thunder Wave
  - Role: Special attacker, Chansey breaker (via PP stall or Special drops)

- **Zapdos** - Electric/Flying utility
  - Thunderbolt / Drill Peck / Thunder Wave / Agility
  - Alternative: Thunderbolt / Drill Peck / Thunder Wave / Rest
  - Role: Special attacker, Rhydon lure, paralysis spreader

- **Rhydon** - Best Ground-type
  - Earthquake / Rock Slide / Body Slam / Substitute
  - Role: Physical attacker, Zapdos check, electric immunity

**B2 Tier:**
- **Jynx** - Fast sleep user
- **Cloyster** - Physical wall, Explosion user
- **Gengar** - Fastest sleep user

**C Tier:**
- Golem (alternative to Rhydon with Explosion)
- Lapras (bulky water/ice)
- Slowbro (Amnesia sweeper)

---

### 2. Common Movesets (Standard Sets)

#### Tauros (100% Usage)
```
- Body Slam
- Hyper Beam
- Earthquake
- Blizzard
```

#### Chansey (100% Usage)
```
Set 1 (Standard):
- Ice Beam
- Soft-Boiled
- Thunder Wave
- Thunderbolt

Set 2 (Reflect):
- Reflect
- Seismic Toss
- Soft-Boiled
- Thunder Wave
```

#### Snorlax (~96% Usage)
```
Set 1 (Standard):
- Body Slam
- Earthquake
- Self-Destruct
- Hyper Beam

Set 2 (Reflect):
- Reflect
- Rest
- Body Slam
- Self-Destruct
```

#### Exeggutor (~63% Usage)
```
Set 1 (Standard):
- Sleep Powder
- Psychic
- Explosion
- Stun Spore

Set 2 (Offensive):
- Sleep Powder
- Psychic
- Double-Edge
- Mega Drain
```

#### Starmie (~79% Usage)
```
Set 1 (ParaSpam):
- Thunderbolt
- Blizzard
- Recover
- Thunder Wave

Set 2 (Offensive):
- Surf
- Thunderbolt
- Blizzard
- Recover
```

#### Alakazam (~38% Usage)
```
Set 1 (Standard):
- Psychic
- Recover
- Reflect
- Thunder Wave

Set 2 (Seismic Toss):
- Psychic
- Seismic Toss
- Recover
- Thunder Wave
```

#### Zapdos (~25% Usage)
```
- Thunderbolt
- Drill Peck
- Thunder Wave
- Agility/Rest
```

#### Rhydon (~25% Usage)
```
- Earthquake
- Rock Slide
- Body Slam
- Substitute
```

---

### 3. Usage Statistics

**Premier League Usage (Most Recent Data):**
- Chansey: 100%
- Tauros: 100%
- Snorlax: 95.83%
- Starmie: 79.17%
- Exeggutor: 62.50%
- Alakazam: 37.50%
- Rhydon: 25.00%
- Gengar: ~15% (rising)

**Key Trends:**
- Starmie rising in usage/viability (2024)
- Reflect Chansey increasingly common
- Gengar usage increasing
- Zapdos remains niche but powerful

---

## AGENT IMPLEMENTATION GUIDANCE

### 1. Move Scoring Factors (Priority Order)

#### Immediate Threats (Weight: 40%)
1. **Can this move KO opponent?**
   - ALWAYS prioritize if KO guaranteed
   - Consider Hyper Beam (no recharge on KO)
   - Factor in crit chance for near-KOs

2. **Does this prevent opponent's win condition?**
   - Prevent sleep if not slept yet
   - Prevent paralysis spread
   - Prevent opponent setup (Amnesia, Agility)

#### Status Warfare (Weight: 30%)
3. **Sleep advantage**
   - Sleep opponent ASAP if they haven't slept you
   - Sleep > Paralysis > Everything else

4. **Paralysis spread**
   - Target fastest unboosted threats (Alakazam, Starmie, Tauros)
   - Avoid paralyzed targets (wasted turn)
   - Normal-types immune to Body Slam paralysis

5. **Freeze chance**
   - Blizzard on Chansey (game-winning if freeze lands)
   - Ice Beam on key threats

#### Material Advantage (Weight: 20%)
6. **Expected damage**
   - Factor in type effectiveness
   - Account for STAB
   - Consider crit rate (speed-based)
   - Random damage range (217-255 / 255)

7. **HP conservation**
   - Preserve healthy Pokémon for late game
   - Sacrifice weakened Pokémon strategically
   - Tauros should be saved for cleaning (50% HP opponents)

#### Positioning (Weight: 10%)
8. **Switch advantage**
   - Force favorable switch (opponent brings Chansey → you bring Tauros)
   - Predict switch and hit incoming Pokémon
   - Maintain switch initiative

9. **Speed control**
   - Eliminate faster threats
   - Protect own speed advantage
   - Agility when ahead to lock opponent

---

### 2. Position Evaluation - "Winning" vs "Losing"

#### Winning Positions
- **Slept opponent's Pokémon, yours not slept** (+40 points)
- **3+ healthy Pokémon vs opponent's <2** (+30 points)
- **Tauros alive + opponent's team at ~50% HP** (+25 points)
- **Chansey alive + opponent has only special attackers** (+20 points)
- **Paralyzed 3+ opponent Pokémon** (+15 points per paralyzed)
- **Faster Pokémon alive vs slower opponent** (+10 points per speed tier)
- **Type advantage matchup active** (+10 points)

#### Losing Positions
- **Your Pokémon slept, opponent's not slept** (-40 points)
- **Fewer than 2 healthy Pokémon remaining** (-30 points)
- **Tauros/Snorlax fainted, opponent's alive** (-25 points)
- **Chansey paralyzed (can't spread paralysis)** (-15 points)
- **Opponent has speed advantage** (-10 points per tier)
- **Trapped in bad matchup (Rhydon vs Starmie)** (-20 points)

#### Neutral Indicators
- Both sides slept 1 Pokémon
- Equal HP distribution
- Equal paralysis count
- Balanced team compositions remaining

---

### 3. Material Advantage Calculation

**Pokémon Value (Base Points):**
- Tauros: 200 points (game-closer)
- Chansey: 180 points (mandatory special wall)
- Snorlax: 180 points (physical backbone)
- Starmie: 160 points (speed + power)
- Exeggutor: 160 points (sleep utility)
- Alakazam: 150 points (speed + Chansey breaker)
- Zapdos/Rhydon: 140 points (role players)

**HP Multipliers:**
- 100-75% HP: 1.0× value
- 75-50% HP: 0.75× value
- 50-25% HP: 0.5× value
- 25-1% HP: 0.25× value

**Status Multipliers:**
- Healthy: 1.0×
- Paralyzed: 0.85× (reduced for fast Pokémon, minimal for slow)
- Burned: 0.7× (physical attackers), 0.9× (special attackers)
- Poisoned: 0.8×
- Badly Poisoned: 0.6× (worsens over time)
- Asleep: 0.3× (essentially out of game for 1-7 turns)
- Frozen: 0.1× (nearly useless)

**Material Advantage Formula:**
```
Your Total = Σ(Pokémon Base Value × HP Multiplier × Status Multiplier)
Opponent Total = Σ(same calculation)

Material Advantage = Your Total - Opponent Total

If Material Advantage > 100: Winning
If Material Advantage < -100: Losing
If -100 ≤ Material Advantage ≤ 100: Even
```

---

### 4. Heuristics from Strong Gen 1 Players

#### Early Game (Turns 1-10)
1. **Sleep first** - Most important objective
2. **Preserve Tauros** - Don't bring in early
3. **Spread paralysis aggressively** - Use Chansey, Alakazam, Starmie
4. **Scout movesets** - Determine opponent's sets (Reflect Chansey? EQ Snorlax?)
5. **Accept calculated risk** - 30% paralysis chance often worth the risk

#### Mid Game (Turns 11-30)
6. **Target paralysis on fast threats** - Prioritize Alakazam, Starmie, Tauros
7. **Fish for freeze on Chansey** - Game-winning if successful
8. **Weaken bulky Pokémon to ~50% HP** - Set up for Tauros sweep
9. **Trade fainted Pokémon strategically** - Sacrifice weakened Pokémon for damage
10. **Maintain switch advantage** - Force opponent into bad matchups

#### Late Game (Turns 30+)
11. **Tauros cleaning time** - Bring in when opponents at ~50% HP
12. **Hyper Beam liberally** - No recharge on KO
13. **Don't go for 6-0** - Make safe plays for guaranteed win
14. **Count PP** - Recover has 32 PP, Soft-Boiled 32, can stall
15. **Play percentages** - Take 90% win over 95% win if safer

#### General Decision-Making
16. **Speed determines game pace** - Faster player controls tempo
17. **Every % matters** - 0.4% chance to miss (1/256) is real
18. **Crit fishing is viable** - Tauros 21% crit rate on Body Slam
19. **Status immunity is huge** - Normal-types vs Body Slam, Ground vs Thunder Wave
20. **Self-Destruct/Explosion are bombs** - 2-for-1 trades, momentum shifts

#### Prediction Heuristics
21. **Assume opponent is good** - Predict optimal plays
22. **Switching > Staying (usually)** - Most turns involve at least 1 switch
23. **Chansey attracts physical attackers** - Expect Tauros, Snorlax, Rhydon
24. **Rhydon/Golem attract Water/Ice** - Expect Starmie, Lapras
25. **Sleep users attract sleep checkers** - Expect Chansey, Starmie after Exeggutor lead

#### Matchup Knowledge
26. **Starmie always runs Recover** - Assume 4th move is Recover
27. **Tauros always has Body Slam + Blizzard** - Other 2 slots variable
28. **Chansey has 50% chance of Reflect** - Scout early
29. **Snorlax either has EQ or doesn't** - Changes Rhydon/Zapdos safety
30. **Alakazam beats Chansey 1v1** - Via Special drops (Psychic) or PP stall

---

### 5. Damage Calculation Implementation

**Required for Agent:**

```python
def calculate_damage(attacker, defender, move, critical=False):
    """
    Gen 1 damage calculation
    """
    level = 100  # OU is always Level 100
    crit_mult = 2 if critical else 1
    power = move.base_power
    
    # Determine A and D stats
    if move.category == "physical":
        A = attacker.attack_stat  # Use current stat
        D = defender.defense_stat
    else:  # special
        A = attacker.special_stat
        D = defender.special_stat
    
    # Critical hits ignore stat modifications
    if critical:
        A = attacker.base_attack  # Use unmodified stats
        D = defender.base_defense
    
    # Stat overflow handling
    if A > 255 or D > 255:
        A = A // 4
        D = D // 4
    
    # Base damage
    damage = ((2 * level * crit_mult // 5 + 2) * power * A // D) // 50 + 2
    
    # STAB
    stab = 1.5 if move.type in attacker.types else 1.0
    damage = int(damage * stab)
    
    # Type effectiveness
    type_mult = get_type_effectiveness(move.type, defender.types)
    damage = int(damage * type_mult)
    
    # Random factor (217-255 / 255)
    # For calculation, use average (236/255 ≈ 0.926)
    # For actual damage, randomize between range
    damage_min = int(damage * 217 / 255)
    damage_max = int(damage * 255 / 255)
    
    return (damage_min, damage_max)


def get_critical_hit_chance(pokemon, move):
    """
    Calculate crit chance based on Gen 1 mechanics
    """
    base_speed = pokemon.base_speed
    
    high_crit_moves = ["slash", "razorleaf", "crabhammer", "karatechop"]
    
    if move.name.lower() in high_crit_moves:
        crit_rate = (base_speed * 100) / 64
    else:
        crit_rate = (base_speed * 100) / 512
    
    # Cap at 99.6%
    return min(crit_rate, 99.6)


def get_type_effectiveness(move_type, defender_types):
    """
    Gen 1 type chart (different from later gens!)
    """
    # Use gen1typechart.json data
    # Key differences:
    # - Ghost is 0× vs Psychic (bug)
    # - Bug is 2× vs Poison
    # - Poison is 2× vs Bug
    pass


def calculate_expected_damage(attacker, defender, move):
    """
    Expected damage accounting for crit chance
    """
    crit_chance = get_critical_hit_chance(attacker, move) / 100
    
    non_crit_damage = calculate_damage(attacker, defender, move, critical=False)
    crit_damage = calculate_damage(attacker, defender, move, critical=True)
    
    # Expected value
    expected_min = (1 - crit_chance) * non_crit_damage[0] + crit_chance * crit_damage[0]
    expected_max = (1 - crit_chance) * non_crit_damage[1] + crit_chance * crit_damage[1]
    expected_avg = (expected_min + expected_max) / 2
    
    return expected_avg
```

---

### 6. Key Implementation Formulas

**Sleep Counter:**
```python
sleep_turns_remaining = random.randint(1, 7)  # Set when inflicted
# Decrement each turn Pokémon tries to move
# Wake-up turn is wasted (cannot act)
```

**Paralysis Check:**
```python
if status == "paralyzed":
    current_speed = base_speed * 0.25  # Speed reduced to 25%
    if random.randint(1, 4) == 1:  # 25% chance
        # Fully paralyzed this turn
        return "paralyzed_this_turn"
```

**Toxic Damage:**
```python
toxic_counter += 1  # Increments each turn
toxic_damage = (toxic_counter / 16) * max_hp
```

**Accuracy Check:**
```python
def move_hits(move_accuracy):
    """
    Gen 1 accuracy with 1/256 miss glitch
    """
    if move.name.lower() in ["swift", "bide"]:
        return True
    
    # Convert percentage to 0-255 scale
    acc = int(move_accuracy * 255 / 100)
    rng = random.randint(0, 255)
    
    return rng < acc  # Note: rng == 255 always misses even if acc == 255
```

**Body Slam Paralysis:**
```python
def body_slam_paralysis_check(target):
    if target.type1 == "normal" or target.type2 == "normal":
        return False  # Normal-types immune
    
    # 30% chance (77/256 due to inverted probability)
    return random.randint(0, 255) < 77
```

---

### 7. Priority Actions by Game State

**Opening (Turn 1):**
1. Lead with sleep user (Exeggutor, Jynx, Gengar)
2. If opponent leads sleep user: Chansey or Starmie
3. Predict opponent's lead based on team preview (if applicable)

**After You Sleep Opponent:**
1. Spread paralysis (Chansey, Alakazam, Starmie)
2. Set up (Amnesia Snorlax, Agility Zapdos - rare)
3. Apply offensive pressure (weaken Pokémon to ~50%)

**After Opponent Sleeps You:**
1. Sleep opponent ASAP (equalize sleep count)
2. Aggressive paralysis spread
3. Fish for freeze on Chansey

**Mid-Game Priorities:**
1. Weaken bulky targets (Snorlax, Chansey) to 40-60% HP
2. Paralyze 3+ opponent Pokémon
3. Preserve Tauros HP (keep above 50%)
4. Trade damaged Pokémon for damage output

**End-Game Cleanup:**
1. Bring in Tauros when opponents at ~50% HP
2. Body Slam → Hyper Beam if KO guaranteed
3. Accept trades that leave you with 1 Pokémon vs 0

---

### 8. Move Selection Algorithm (Simplified)

```python
def select_move(battle_state):
    """
    Simplified move selection for Gen 1 agent
    """
    scores = {}
    
    for move in available_moves:
        score = 0
        
        # 1. KO Check (highest priority)
        if can_ko(move, opponent):
            score += 1000
            if move.name == "Hyper Beam":
                score += 100  # No recharge on KO
        
        # 2. Sleep Advantage
        if move.name in SLEEP_MOVES:
            if not opponent_has_slept and not we_have_slept:
                score += 800
            elif opponent_slept_count < our_slept_count:
                score += 600
        
        # 3. Paralysis Spread
        if move.has_paralysis_chance:
            if opponent.status is None and opponent.speed > 100:
                score += 400  # Prioritize fast threats
            elif opponent.status is not None:
                score -= 100  # Waste to paralyze already statused
        
        # 4. Expected Damage
        expected_dmg = calculate_expected_damage(us, opponent, move)
        score += expected_dmg  # Raw damage points
        
        # 5. Type Effectiveness Bonus
        if get_type_effectiveness(move.type, opponent.types) >= 2:
            score += 200
        
        # 6. Switch Prediction (advanced)
        if predict_opponent_will_switch():
            # Score moves that hit predicted switch-in
            predicted_switch_in = predict_switch_target()
            switch_damage = calculate_expected_damage(us, predicted_switch_in, move)
            score += switch_damage * 0.5  # Weight by prediction confidence
        
        scores[move] = score
    
    # Return highest scoring move
    return max(scores, key=scores.get)
```

---

## SOURCES

- [Smogon RBY Mechanics Guide](https://www.smogon.com/rb/articles/rby_mechanics_guide)
- [Smogon RBY Speed Guide](https://www.smogon.com/rb/articles/rby_speed)
- [Smogon Critical Hits in RBY](https://www.smogon.com/rb/articles/critical_hits)
- [Smogon RBY Battling Guide](https://www.smogon.com/rb/articles/rby_battling)
- [Smogon RBY OU Viability Rankings (2024-2025)](https://www.smogon.com/forums/threads/rby-ou-viability-rankings.3685861/)
- [Bulbapedia Damage Calculation](https://bulbapedia.bulbagarden.net/wiki/Damage)
- [Bulbapedia Generation I Battle Glitches](https://bulbapedia.bulbagarden.net/wiki/List_of_battle_glitches_in_Generation_I)
- [Smogon Important RBY Differences](https://www.smogon.com/rb/articles/differences)

---

**Document Version:** 1.0  
**Last Updated:** November 4, 2025  
**Maintained by:** Josh Yeung (pokechamp-based-agent-track1)
