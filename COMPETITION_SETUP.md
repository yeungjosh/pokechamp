# Competition Server Setup - Step-by-Step Guide

## Overview

Get your Gen1 agent running on the PokéAgent Challenge ladder in 5 steps.

---

## Step 1: Register Showdown Account

### 1.1 Visit Competition Server
Go to: **https://pokeagentshowdown.com**

### 1.2 Create Account
1. Click the **gear icon** (⚙️) in top right corner
2. Click **"Register"**
3. Choose username starting with **"PAC"** (required)
   - Example: `PAC-YourName-Gen1`
   - Example: `PAC-JoshAgent`
4. Choose a password (save it!)
5. Click **"Register"**

### 1.3 Verify Account
- You should see "Successfully registered" message
- Test login on website to confirm

**✅ Done:** You now have a competition account

---

## Step 2: Configure Credentials

### 2.1 Create Password File
```bash
cd /Users/joshyeung/personal-projects/pokechamp-based-agent-track1/pokechamp
cp passwords.json.example passwords.json
```

### 2.2 Edit Password File
Open `passwords.json` and add your credentials:

```json
{
  "PAC-YourName-Gen1": "your_actual_password_here"
}
```

Replace:
- `PAC-YourName-Gen1` → Your actual username
- `your_actual_password_here` → Your actual password

**✅ Done:** Credentials saved locally

---

## Step 3: Choose Your Team

Pick one of the custom teams:

**Option A: Balanced Team** (Recommended)
```bash
TEAM="teams/gen1ou_balanced.txt"
```

**Option B: Offensive Team**
```bash
TEAM="teams/gen1ou_offensive.txt"
```

**Option C: Sleep Focus Team**
```bash
TEAM="teams/gen1ou_sleep_focus.txt"
```

Or use random Metamon teams (current default):
```bash
TEAM=""  # Leave empty for random
```

**✅ Done:** Team selected

---

## Step 4: Test Connection (Dry Run)

### 4.1 Quick Test (1 Battle)
```bash
uv run python ladder_gen1.py \
    --USERNAME "PAC-YourName-Gen1" \
    --PASSWORD "your_password" \
    --team "$TEAM" \
    --N 1
```

Replace:
- `PAC-YourName-Gen1` → Your username
- `your_password` → Your password
- `$TEAM` → Team file path (or empty for random)

### 4.2 Expected Output
```
Loading team from teams/gen1ou_balanced.txt
Connecting to pokeagentshowdown.com...
Connected! Starting ladder battle...
Battle started: gen1ou-12345
...
Battle complete: Won/Lost
Win rate: 100.0%
```

### 4.3 Troubleshooting

**Error: "Invalid username/password"**
- Check username starts with "PAC"
- Verify password is correct
- Try logging in on website first

**Error: "Connection refused"**
- Server may be offline
- Check https://pokeagentshowdown.com is accessible
- Try again in a few minutes

**Error: "Team format invalid"**
- Check team file exists
- Verify team file is in Showdown format
- Try without custom team (random)

**✅ Done:** Successfully connected and completed test battle

---

## Step 5: Run on Ladder

### 5.1 Start Ladder Climbing (10 battles)
```bash
uv run python ladder_gen1.py \
    --USERNAME "PAC-YourName-Gen1" \
    --PASSWORD "your_password" \
    --team "teams/gen1ou_balanced.txt" \
    --N 10
```

### 5.2 Monitor Progress
```
Starting battle 1/10...
Win rate: 100.0%
Starting battle 2/10...
Win rate: 50.0%
...
Final win rate: 70.0%
Final Elo: ~1350
```

### 5.3 Check Ladder Ranking
1. Go to https://pokeagentshowdown.com
2. Click **"Ladder"** tab
3. Find **"Gen1OU"** format
4. Look for your username

**✅ Done:** Agent running on ladder!

---

## Quick Reference Commands

### Test 1 Battle
```bash
uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" --N 1
```

### Run 10 Battles (Balanced Team)
```bash
uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" \
    --team "teams/gen1ou_balanced.txt" --N 10
```

### Run 50 Battles (Grind Rating)
```bash
uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" \
    --team "teams/gen1ou_balanced.txt" --N 50
```

### Use Random Teams
```bash
uv run python ladder_gen1.py --USERNAME "PAC-YourName" --PASSWORD "pass" --N 10
```

---

## Team Registration (Before Qualifiers)

### When to Register
- Practice ladder: Oct 13-26 (open to all)
- **Registration deadline:** Before qualifiers start
- Qualifiers: Only registered usernames allowed

### How to Register
1. Complete registration form: https://docs.google.com/forms/d/e/1FAIpQLSfjj6la_Z9x4V39bpPNrByGBHMiF9Ql0aUsUwznJ158NUOGDA/viewform
2. Register **one** Showdown username per team
3. This is the username that will play in qualifiers

**Important:** Different from creating Showdown account (Step 1). This is official competition registration.

---

## Expected Performance

### Baseline Estimates
- **vs Random:** 95%+ win rate
- **vs max_power:** 100% win rate (verified locally)
- **vs abyssal:** 80% win rate (verified locally)
- **vs Competition:** Unknown (likely 60-70%)

### Target Elo
- **1000-1200:** Beginner agents
- **1200-1400:** Intermediate agents (our target)
- **1400-1600:** Strong agents
- **1600+:** Elite agents

### Time Estimates
- **1 battle:** ~20-30 seconds
- **10 battles:** ~5 minutes
- **100 battles:** ~45 minutes

---

## Troubleshooting

### Agent Running Slow
**Check expectimax is disabled:**
```python
# In bots/gen1_agent.py
self.use_expectimax = False  # Should be False
```

### Connection Errors
**Common fixes:**
- Verify username starts with "PAC"
- Check password in passwords.json
- Test login on website first
- Wait a few minutes and retry

### Battle Timeouts
**If agent times out during battles:**
- Server enforces ~60-90 second turn limit
- Gen1Agent should be fast enough (~1-2s/turn)
- Check debug logs for slow operations

### Team Issues
**If team won't load:**
- Verify file exists in `teams/` directory
- Check Showdown format (see team files)
- Try without custom team (omit --team flag)

---

## Next Steps After Setup

1. **Run 20-50 battles** - Get statistically significant results
2. **Monitor Elo** - Track rating changes
3. **Adjust teams** - Switch teams if one performs better
4. **Register for qualifiers** - Complete registration form
5. **Practice until Oct 13** - Open ladder for testing

---

## Files Reference

- `ladder_gen1.py` - Ladder battle script
- `passwords.json` - Your credentials (gitignored)
- `teams/gen1ou_*.txt` - Custom team files
- `bots/gen1_agent.py` - Agent implementation

---

**Ready to compete!** 🏆

For issues: Check https://pokeagent.github.io/track1.html
