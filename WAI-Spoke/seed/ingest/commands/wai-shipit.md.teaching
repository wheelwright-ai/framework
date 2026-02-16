# WAI Shipit

**Complete Session Closeout + Git Commit + Push**

One command to end session properly: closeout, commit, push, verify.

## WAI Principles Reinforced

- **P1: Persistence** - Ship it or lose it
- **P2: Verification** - Verify push succeeded before claiming done
- **P3: Stewardship** - Complete the work responsibly
- **P7: Evolution** - Capture session learnings in commit

## When to Use

- End of productive session
- Before context fills up (check with `/wai-time`)
- Before breaks or stopping work
- After completing a feature or fix

---

## Instructions

### Step 1: Execute Full Closeout

Run the complete `/wai-closeout` protocol:

1. **Reconcile autosave lugs** - Consolidate session work
2. **Extract signals** - Capture high-impact decisions (impact >= 8)
3. **Update WAI-State.json** - Increment session count, timestamps
4. **Clear session log** - Ready for next session

### Step 2: Stage Changes

```bash
git status
```

Review what will be committed:
- WAI-Spoke/ files (always)
- Code changes from this session
- New files created

```bash
git add WAI-Spoke/
git add [specific files from session work]
```

**Important:** Be deliberate about what you stage. Don't blindly `git add -A`.

### Step 3: Generate Commit Message

Create a message capturing:
- Session number (from WAI-State.json)
- What was accomplished
- Key decisions made
- Impact summary

Format:
```
WAI Session [N]: [brief summary of accomplishments]
```

Example:
```
WAI Session 28: Fix teach_reconciliation syntax errors, add hub fingerprint signing
```

### Step 4: Commit

```bash
git commit -m "WAI Session [N]: [summary]"
```

### Step 5: Push

```bash
git push origin main
```

### Step 6: Verify (CRITICAL)

**Do NOT skip this step. Do NOT assume success.**

```bash
# Check local is clean
git status
# MUST show: "nothing to commit, working tree clean"
# MUST show: "up to date with 'origin/main'"

# Check remote has the commit
git log origin/main --oneline -1
# MUST show your commit hash

# Verify hashes match
git log --oneline -1
# Local hash MUST equal remote hash
```

---

## Output Format

```
## Shipit Complete

### Closeout
- Session #[N] reconciled
- [N] signals extracted
- State files updated

### Git
- Staged: [N] files
- Commit: [hash]
- Message: "WAI Session [N]: [summary]"
- Push: origin/main

### Verification
- Local clean: yes
- Remote updated: yes
- Commit visible: [hash]

## Status: SHIPPED

Next session will load from this checkpoint.
```

---

## If Something Fails

### Closeout Failed
- Check WAI-Spoke/ directory exists
- Check WAI-State.json is valid JSON
- Retry closeout phase

### Commit Failed
- Check for unstaged changes: `git status`
- Check for merge conflicts: `git diff`
- Stage missing files: `git add [file]`

### Push Failed
```bash
# Test SSH
ssh -T git@github.com

# Check remote
git remote -v

# Check for divergence
git fetch origin
git status
```

If remote is ahead:
```bash
git pull --rebase origin main
git push origin main
```

---

## Language Rules

**Never say:**
- "Should be pushed"
- "Probably worked"
- "I think it shipped"

**Always say:**
- "Verified with git status"
- "Confirmed push with git log origin/main"
- "Commit [hash] visible on remote"

---

## Related Commands

- `/wai-closeout` - Just closeout, no git
- `/wai-time` - Check context before shipping
- `/wai-status` - Framework health check

---

*Shipit = Closeout + Commit + Push + Verify. No shortcuts.*
