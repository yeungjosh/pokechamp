# Gen 1 RBY OU Quick Reference

## Damage Formula (One-Liner)
```
Damage = ((((2×L×Crit÷5+2)×Pow×A/D)÷50+2)×STAB×Type×random)
Crit=2 if crit else 1 | random=217-255÷255 | STAB=1.5 if match else 1
```

## Critical Hit Rates
```
Normal: (BaseSpeed × 100) / 512
High Crit: (BaseSpeed × 100) / 64
```
- Tauros: 21.48% | Alakazam: 23.44% | Starmie: 22.46% | Snorlax: 5.86%
- Crits ignore ALL stat mods, Reflect, Light Screen

## Status Effects Quick Facts
- **Sleep:** 1-7 turns, wake-up wastes turn
- **Freeze:** Permanent (no thaw chance)
- **Paralysis:** Speed × 0.25, 25% full para chance
- **Burn:** 1/16 HP/turn, Attack × 0.5
- **Toxic:** n/16 HP (n=turns), resets on switch

## Accuracy (True Values)
- 100% → 99.6% (255/256) - ALL moves can miss!
- 90% → 89.5% | 85% → 84.4% | 70% → 69.5%
- Only Swift & Bide never miss

## Top 7 OU Pokemon (Usage)
1. **Tauros** (100%) - Body Slam/Hyper Beam/EQ/Blizzard
2. **Chansey** (100%) - Ice Beam/Soft-Boiled/T-Wave/Thunderbolt
3. **Snorlax** (96%) - Body Slam/EQ/Self-Destruct/Hyper Beam
4. **Starmie** (79%) - Thunderbolt/Blizzard/Recover/T-Wave
5. **Exeggutor** (63%) - Sleep Powder/Psychic/Explosion/Stun Spore
6. **Alakazam** (38%) - Psychic/Recover/Reflect/T-Wave
7. **Rhydon** (25%) - Earthquake/Rock Slide/Body Slam/Substitute

## Key Glitches
- **Hyper Beam:** No recharge if KO
- **1/256 miss:** All moves 99.6% accurate max
- **Wrap:** 2-5 turns opponent can't move (if faster = infinite)
- **Ghost vs Psychic:** 0× (should be 2×)
- **Focus Energy:** Divides crit rate by 4 (NEVER USE)
- **Body Slam:** Normal-types immune to paralysis

## Type Chart Differences
- Bug → Poison: 2× (not 0.5×)
- Poison → Bug: 2× (not 0.5×)
- Ghost → Psychic: 0× (BUG - should be 2×)
- No Dark/Steel/Fairy types

## Priority Rankings
1. **Sleep opponent first** (if neither slept yet)
2. **KO if possible** (especially with Hyper Beam)
3. **Paralyze fast threats** (Alakazam, Starmie, Tauros)
4. **Weaken to ~50% for Tauros sweep**
5. **Preserve Tauros until endgame**

## Speed Tiers
- **130+:** Electrode(140), Jolteon(130)
- **110-120:** Alakazam(120), Starmie(115), Tauros(110), Gengar(110)
- **90-105:** Zapdos(100), Jynx(95)
- **Walls:** Chansey(50), Snorlax(30), Slowbro(30)

## Material Values
- Tauros: 200 | Chansey: 180 | Snorlax: 180
- Starmie: 160 | Exeggutor: 160 | Alakazam: 150
- Zapdos/Rhydon: 140

Multiply by: HP% × Status Modifier
- Healthy: 1.0 | Para: 0.85 | Burn: 0.7 | Poison: 0.8 | Toxic: 0.6 | Sleep: 0.3 | Freeze: 0.1

## Common Cores
- **Lax-Tar-Egg:** Snorlax + Starmie + Exeggutor (balanced)
- **Mie-Don-Dos:** Starmie + Rhydon + Zapdos (synergy)
- **Chansey + Attackers:** Chansey + Tauros/Snorlax (standard)

## Lead Matchups
- **Best Sleepers:** Gengar (110) > Jynx (95) > Exeggutor (55)
- **Counter Leads:** Starmie, Alakazam, Chansey
- **First sleep = huge advantage**

## Win Conditions
- Sleep advantage (+40 pts)
- Tauros alive + foes at 50% HP (+25 pts)
- 3+ paralyzed opponents (+15 each)
- Material advantage > 100 pts (winning)

## Code Snippets

### Crit Chance
```python
crit_rate = (base_speed * 100) / 512
if move in ["slash","razorleaf","crabhammer","karatechop"]:
    crit_rate = (base_speed * 100) / 64
crit_rate = min(crit_rate, 99.6)
```

### Accuracy Check
```python
acc = int(accuracy * 255 / 100)  # Convert to 0-255
rng = random.randint(0, 255)
hits = rng < acc  # 255 always misses
```

### Paralysis
```python
speed = base_speed * 0.25
paralyzed_this_turn = (random.randint(1,4) == 1)
```

### Expected Damage
```python
non_crit = calc_dmg(crit=False)
crit = calc_dmg(crit=True)
expected = (1-crit_rate)*non_crit + crit_rate*crit
```

---

**For full details, see:** `GEN1_RBY_MECHANICS_RESEARCH.md`
