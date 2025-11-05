# Gen1 Agent - 5 Minute Quickstart

Get on the competition ladder in 5 steps.

---

## Step 1: Register Account (2 min)

1. Go to https://pokeagentshowdown.com
2. Click ⚙️ (gear icon) → Register
3. Username: `PAC-YourName` (must start with "PAC")
4. Password: (choose one, save it)
5. Click Register

✅ Account created

---

## Step 2: Save Credentials (30 sec)

```bash
cd /Users/joshyeung/personal-projects/pokechamp-based-agent-track1/pokechamp

# Create password file
cp passwords.json.example passwords.json

# Edit it (replace with your actual credentials)
# {"PAC-YourName": "your_password"}
```

✅ Credentials saved

---

## Step 3: Test Connection (1 min)

```bash
uv run python ladder_gen1.py \
    --USERNAME "PAC-YourName" \
    --PASSWORD "your_password" \
    --N 1
```

Expected output:
```
Connecting to ladder...
Battle 1: Won
Record: 1-0 (100.0%)
```

✅ Connection works

---

## Step 4: Run 10 Battles (5 min)

**With balanced team:**
```bash
uv run python ladder_gen1.py \
    --USERNAME "PAC-YourName" \
    --PASSWORD "your_password" \
    --team "teams/gen1ou_balanced.txt" \
    --N 10
```

**With random teams:**
```bash
uv run python ladder_gen1.py \
    --USERNAME "PAC-YourName" \
    --PASSWORD "your_password" \
    --N 10
```

✅ Battles running

---

## Step 5: Check Ranking (30 sec)

1. Go to https://pokeagentshowdown.com
2. Click "Ladder"
3. Find "Gen1OU"
4. Look for your username

✅ On the ladder!

---

## Quick Commands

### Test (1 battle)
```bash
uv run python ladder_gen1.py --USERNAME "PAC-You" --PASSWORD "pass" --N 1
```

### Practice (10 battles)
```bash
uv run python ladder_gen1.py --USERNAME "PAC-You" --PASSWORD "pass" --N 10
```

### Grind Rating (50 battles)
```bash
uv run python ladder_gen1.py --USERNAME "PAC-You" --PASSWORD "pass" \
    --team "teams/gen1ou_balanced.txt" --N 50
```

---

## Troubleshooting

**"Invalid username/password"**
- Username must start with "PAC"
- Check password in passwords.json

**"Connection refused"**
- Server may be down
- Try https://pokeagentshowdown.com in browser

**"Team format invalid"**
- Check team file exists: `ls teams/gen1ou_balanced.txt`
- Or use random teams (omit --team flag)

---

## Teams Available

1. **Balanced** (Recommended) - `teams/gen1ou_balanced.txt`
2. **Offensive** - `teams/gen1ou_offensive.txt`
3. **Sleep Focus** - `teams/gen1ou_sleep_focus.txt`
4. **Random** (Default) - Omit `--team` flag

---

## Expected Performance

- First 10 battles: ~60-80% win rate
- After 50 battles: Elo ~1200-1400
- Agent speed: ~20s per battle

---

**Full guide:** See `COMPETITION_SETUP.md` for detailed instructions

**Ready to compete!** 🏆
