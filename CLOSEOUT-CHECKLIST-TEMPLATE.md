# Session Closeout Checklist - REQUIRED BEFORE DECLARING COMPLETE

**Use this checklist for EVERY session closeout.**

**DO NOT declare session "complete" until all items are ✓ DONE**

---

## Pre-Closeout

- [ ] All code changes made and tested
- [ ] All tests passing
- [ ] All documentation written
- [ ] All demos/examples working

---

## Git Commitment Phase

### Step 1: Stage All Changes
```bash
git add -A
```
- [ ] Command executed
- [ ] No errors
- [ ] All changes staged

### Step 2: Review Changes
```bash
git status
```
- [ ] Review all changes listed
- [ ] Verify nothing accidental staged
- [ ] Confirm files are correct

### Step 3: Create Commit Message
Template:
```
[Session Title]: [What was accomplished]

Brief description of:
- Features added
- Bugs fixed
- Tests passing
- Production readiness

Files changed: [count]
Lines added: [count]
```

Example:
```
CLI v4.0.0 Release: Hub Registry Integration & Multi-Project Support

- Fixed 5 critical bugs (Unicode, colors, interactive, Windows)
- Released v4.0.0 with hub registry integration
- Added multi-project teach/learn support
- Maintained 100% backward compatibility

Files changed: 46
Lines added: 7622
```

### Step 4: Commit Changes
```bash
git commit -m "[message from Step 3]"
```
- [ ] Command executed without error
- [ ] Got a commit hash (e.g., `71d5a1b`)
- [ ] Commit hash recorded below

**Commit Hash: _________________**

### Step 5: Verify Clean Status
```bash
git status
```

Expected output:
```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

- [ ] Status shows `nothing to commit`
- [ ] Status shows `working tree clean`
- [ ] No files listed as modified
- [ ] No untracked files (except expected like node_modules, __pycache__)

---

## Observations Logging Phase

### Step 1: Create Observation Entry

Template:
```json
{
  "timestamp": "2026-02-08T14:00:00Z",
  "session": "[Session name]",
  "action_id": "session.closeout",
  "action_description": "[What was accomplished]",
  "plan": "[What we set out to do]",
  "status": "✓ COMPLETE",
  "verification": {
    "git_commit": "[commit hash from above]",
    "files_changed": [number],
    "insertions": [number],
    "tests_passing": true,
    "production_ready": [true/false],
    "backward_compatible": [true/false]
  },
  "notes": "[Any important notes for next session]"
}
```

### Step 2: Append to observations.jsonl
```bash
echo '[JSON from above]' >> WAI-Spoke/observations.jsonl
```

- [ ] Appended to WAI-Spoke/observations.jsonl
- [ ] No syntax errors
- [ ] Valid JSON format

### Step 3: Verify Entry
```bash
tail -1 WAI-Spoke/observations.jsonl | python -m json.tool
```

Expected: Pretty-printed JSON of your entry

- [ ] Entry appears at end of file
- [ ] All fields present
- [ ] Status shows `✓ COMPLETE`
- [ ] Timestamp is today's date

---

## Validation Phase

### Run Automated Validator
```bash
python -m wai.closeout_validator --check
```

Expected output:
```
SESSION CLOSEOUT VALIDATION REPORT
================================================================================
✓ PASS | Git Status Clean
       Git status clean

✓ PASS | Git Commit Today
       Git commit exists: 71d5a1b

✓ PASS | Observations Logged
       Observations logged and marked complete

================================================================================
✓ SESSION CLOSEOUT COMPLETE
  All requirements met. Session is properly closed out.
```

- [ ] All three checks show "✓ PASS"
- [ ] No "✗ FAIL" items
- [ ] Report confirms "COMPLETE"

---

## Documentation Phase

### Create Session Summary (if needed)
- [ ] SESSION-[TITLE]-SUMMARY.md created
- [ ] All deliverables documented
- [ ] Metrics recorded
- [ ] Next session notes included

---

## Final Verification

Before declaring "complete", verify:

- [ ] `git status` shows clean working tree
- [ ] `git log --oneline -1` shows today's commit
- [ ] `tail -1 WAI-Spoke/observations.jsonl` shows ✓ COMPLETE entry
- [ ] `python -m wai.closeout_validator --check` shows all ✓ PASS
- [ ] All code tested and working
- [ ] All documentation complete
- [ ] Next session has full context available

---

## Declare Complete ✓

Only after ALL items above are checked, you may write:

**✓ SESSION COMPLETE**

And include:
- Commit hash: `[git hash]`
- Files changed: `[number]`
- Observations logged: Yes
- Git status: Clean
- Production ready: Yes/No

---

## If Validation Fails

If any check fails, run:
```bash
python -m wai.closeout_validator --enforce
```

This will show:
- Which checks failed
- What needs to be fixed
- Steps to complete closeout

---

## Lesson Reminder

**"Complete" is NOT:**
- ❌ Code written
- ❌ Tests passing
- ❌ Docs done
- ❌ Code written + tests passing + docs done

**"Complete" IS:**
- ✅ Code written + tested + documented
- ✅ **Changes staged: `git add -A`**
- ✅ **Changes committed: `git commit -m "..."`**
- ✅ **Observations logged: Entry in observations.jsonl**
- ✅ **Git status clean: `working tree clean`**
- ✅ **Validator passes: `--check` shows all PASS**

**Without all steps above, it's NOT complete.**

---

## Next Session Perspective

When next session starts, they should be able to:

```bash
# 1. See what was done
$ git log --oneline -5
71d5a1b [Your commit message]
[previous commits...]

# 2. See detailed work log
$ tail -5 WAI-Spoke/observations.jsonl
[Your observation entry with status ✓ COMPLETE]

# 3. Understand context
$ python -m wai.closeout_validator --check
✓ All validation passing

# 4. Continue work smoothly
[Next session picks up here with full context]
```

If all of this works, **the session is truly complete.**

---

**Remember:** Session continuity depends on this checklist being followed. Don't skip steps.

