# Closeout Feedback Template Update

**Date:** 2026-02-08 (Post-Session Improvement)  
**Reason:** Address assumption-based language in closeout feedback  
**Status:** ✅ Implemented and pushed

---

## Problem Identified

**Lesson from earlier closeout:**
- We said "Closeout successful" but git push hadn't happened
- We assumed git push worked without verifying
- No explicit solutioning for what actually failed
- Assumption-based language masked real issues

---

## Solution Implemented

### 1. New Feedback Template: `wai-closeout-feedback-v2.md`

**Mandatory template for all closeout feedback going forward.**

Features:
- ✅ **Explicit success outcomes** - Lists what verified
- ❌ **Explicit failure outcomes** - Shows issue + root cause + solutioning
- **No assumptions** - Every claim backed by verification command
- **Numbered steps** - Clear remediation for every failure type
- **Phase-by-phase** - Tests each of 4 phases independently

### 2. Updated `wai-closeout.md`

**Now includes:**
- Reference to feedback template (mandatory use)
- Actual verification commands (not assumptions)
- Mandatory verification checklist (testable items)
- Forbidden phrases list
- Required phrases list

### 3. Explicit Success/Failure Rules

**Success block (use when ALL verifications pass):**
```
✅ CLOSEOUT SUCCESSFUL

All 4 phases complete:
- Phase 1: Reconciliation ✅
- Phase 2: State Updates ✅
- Phase 3: Git Operations ✅
- Phase 4: Verification ✅

Verified:
- git status clean ✅
- Remote branch updated ✅
- Commit hash: [ACTUAL_HASH] ✅
```

**Failure block (use when ANY phase fails):**
```
❌ CLOSEOUT INCOMPLETE

Failed at: Phase 3 (Git Operations - Push)
Issue: Permission denied (publickey)
Root cause: SSH key not configured

Solution:
1. Test SSH: ssh -T git@github.com
2. If fails: Generate and add key
3. Verify: ssh -T git@github.com
4. Retry: closeout
```

---

## Key Improvements

### Removed Phrases (Never Use)
❌ "Probably succeeded"  
❌ "Seems to have worked"  
❌ "Should be pushed"  
❌ "Likely committed"  
❌ "I believe it worked"  

### Required Phrases (Always Use)
✅ "Verified with git status"  
✅ "Confirmed with git log"  
✅ "Checked origin/main"  
✅ "Working directory clean"  
✅ "Commit hash matches"  

---

## Verification Commands (Now Mandatory)

After EVERY closeout, run these and report results:

```bash
# 1. Local state
git status
→ MUST show: "nothing to commit, working tree clean"
→ MUST show: "Your branch is up to date with 'origin/main'"

# 2. Remote state
git log origin/main --oneline -1
→ MUST show: new commit hash

# 3. Comparison
git log --oneline -1
→ Local hash MUST match remote hash

# 4. Content
cat WAI-Spoke/observations.jsonl | wc -l
→ MUST show: observations logged
```

**If ANY command shows different results than expected → Report failure, not success**

---

## Example: Correct Feedback

### Success Example (With Verification)

```
# Closeout Result: observation-system-complete-2026-02-08

## Status: SUCCESS ✅

## Phase Results

### Phase 1: Reconciliation ✅
- Autosave lugs processed
- Session changes identified

### Phase 2: State Updates ✅
- WAI-State.json updated
- Session count incremented

### Phase 3: Git Operations ✅
- All files staged (25 files)
- Commit created: bd47509
- Push succeeded to origin/main
- Remote commit verified

### Phase 4: Verification ✅
- git status: "nothing to commit, working tree clean" ✅
- git status: "Your branch is up to date with 'origin/main'" ✅
- git log --oneline -1: bd47509 (matches origin/main)
- observations.jsonl: 24 observations logged

## ✅ CLOSEOUT SUCCESSFUL

Verified: All phases complete, all commands show clean state.
Remote commit: bd47509 visible on origin/main
Local state: Working directory clean
```

### Failure Example (With Solutioning)

```
# Closeout Result: session-2026-02-08

## Status: FAILED ❌

## Phase Results

### Phase 1: Reconciliation ✅
- Autosave lugs processed

### Phase 2: State Updates ✅
- WAI-State.json updated

### Phase 3: Git Operations ❌
- Files staged ✅
- Commit created ✅
- Push FAILED ❌

### Phase 4: Verification ⏭️
- Skipped (Phase 3 failed)

## ❌ CLOSEOUT INCOMPLETE

### Failed Phase: Git Operations (Push)

Issue: Permission denied (publickey)
Root cause: SSH key not recognized by GitHub

Verification command that failed:
```
$ git push origin main
Permission denied (publickey)
```

### Solution (Numbered Steps)

1. Test SSH connectivity:
   ```
   ssh -T git@github.com
   ```
   If this fails, SSH is not configured.

2. Generate SSH key (if needed):
   ```
   ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
   ```

3. Add public key to GitHub:
   ```
   cat ~/.ssh/id_ed25519.pub
   # Copy output → GitHub Settings > SSH Keys > Add Key
   ```

4. Verify SSH works:
   ```
   ssh -T git@github.com
   # Should show: "authenticated"
   ```

5. Retry closeout:
   ```
   closeout
   ```

### Observation Log
Check what actually failed:
```bash
cat WAI-Spoke/observations.jsonl | python3 -m json.tool | grep -A 20 "git.push"
```

**Do NOT proceed to other tasks until Phase 3 push succeeds.**
```

---

## Implementation Rules

### Rule 1: No Success Without Verification
Do NOT claim success unless:
- [ ] Ran `git status` and confirmed output
- [ ] Ran `git log origin/main` and confirmed commit exists
- [ ] Compared local and remote commit hashes
- [ ] WAI-State.json verified as updated

### Rule 2: Failure Always Includes Solutioning
If ANY phase fails:
- Identify SPECIFIC error (not vague)
- Explain ROOT CAUSE
- Provide NUMBERED STEPS to fix
- Include VERIFICATION command for the fix

### Rule 3: Clear Status Only
Every closeout feedback MUST be:
- ✅ SUCCESS (all verifications pass)
- ❌ FAILURE at [SPECIFIC_PHASE] (with solutioning)

NO "probably", "seems", "might have", "should be"

### Rule 4: Use Template
Every closeout feedback uses `wai-closeout-feedback-v2.md` template structure

### Rule 5: Report What Commands Show
Report actual command output, not assumptions:
- "git status shows X" ✅ (not "should be clean")
- "git log shows commit Y" ✅ (not "push likely worked")
- "origin/main has Z commits" ✅ (not "probably updated")

---

## Files Created/Updated

### New
```
.claude/commands/wai-closeout-feedback-v2.md [443 lines]
```

### Updated
```
.claude/commands/wai-closeout.md              [+verification commands]
```

### Committed
```
Commit: bd47509
Message: "Closeout Feedback: Remove assumptions, add explicit verification"
```

---

## This Prevents

✅ Claiming success when push failed  
✅ Assuming files were committed when they weren't  
✅ Vague language masking real failures  
✅ No recovery path when things go wrong  
✅ Manual verification every time  

## This Enables

✅ Clear success/failure states  
✅ Immediate identification of issues  
✅ Numbered recovery steps  
✅ Verification for every claim  
✅ Next AI session starts with clear context  

---

## Next Session Requirement

**EVERY closeout MUST use this template and verification process.**

When you close a session:
1. Run all 4 verification commands
2. Use feedback template
3. Report SUCCESS ✅ OR FAILURE ❌ with solutioning
4. Do NOT use assumption-based language

This prevents the earlier issue of "closeout succeeded" when work wasn't actually persisted.

---

**Status: ✅ IMPLEMENTED AND PUSHED**

Commit: bd47509  
This improvement live and ready for next session.
