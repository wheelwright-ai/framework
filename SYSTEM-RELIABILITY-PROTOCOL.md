# System Reliability Protocol

**Three-Layer Foundation for Bulletproof Automation**

---

## Layer 1: Enhanced Closeout Skill

**File:** `.claude/commands/wai-closeout-enhanced.md`

### What It Does
- Executes 4 phases: Reconciliation → State Updates → Git Ops → Verification
- **Git is mandatory** - closeout incomplete without push
- **Fail signals (🚨)** stop execution immediately on critical errors
- **Version bumping** via `--bump-patch/minor/major` flags
- **Dry-run mode** for preview-only execution

### Key Guarantee
```
"Without git, there is no persistence."

Closeout succeeds ONLY when:
1. ✅ All files staged
2. ✅ Commit created locally
3. ✅ Commit PUSHED to origin/main
4. ✅ Remote verified (git log shows commit)
5. ✅ State files updated
6. ✅ All checkmarks displayed
```

### Fail Signal Examples
```
🚨 GIT PUSH FAILED 🚨
├─ Error: Permission denied (publickey)
├─ Cause: SSH key issue
└─ Fix: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

🚨 GIT COMMIT FAILED 🚨
├─ Error: Nothing to commit
├─ Cause: Unstaged changes exist
└─ Fix: git add -A
```

---

## Layer 2: Observation & Verification System

**File:** `WAI-OBSERVATION-SYSTEM.md` + `WAI-OBSERVATION-IMPLEMENTATION.md`

### What It Does
- **Execute → Observe → Verify → Log** (never skip steps)
- Every action captured: exit code, output, duration, stderr
- Observations stored in `WAI-Spoke/observations.jsonl` (JSONL, <0.5MB)
- If verification fails: alert user immediately, **don't continue**
- All agents read observations before acting (prevents duplicate work)

### Observation Structure
```json
{
  "id": "obs-20260208-001",
  "timestamp": "2026-02-08T14:32:15Z",
  "session_id": "close-session-1",
  "agent": "Claude Sonnet 4.5",
  "action": "git.push",
  "plan": "Push to origin/main",
  "command": "git push origin main",
  "expected_result": { "exit_code": 0, "output_contains": [...] },
  "actual_result": { "exit_code": 128, "stderr": "..." },
  "verification": { "passed": false, "unexpected_aspects": [...] },
  "remediation": { "suggested_next_step": "Fix SSH key" }
}
```

### Key Guarantee
```
"Trust but verify - every action is observed."

Before acting: Check observations.jsonl
During action: Capture exit code, output, duration
After action: Verify against expected_result
If mismatch: Alert user with remediation steps
```

---

## Layer 3: SSH Key Facts (Wheel-Wide Default)

**Established Facts** (applies to all wheels):

```
SSH Key Location:    ~/.ssh/id_ed25519
SSH Test Command:    ssh -T git@github.com
Expected Success:    Exit code 1 (GitHub returns 1 for auth success)

When git.push fails with "Permission denied (publickey)":
  1. Verify: file.verify "~/.ssh/id_ed25519"
  2. Test: ssh -T git@github.com
  3. If fails: Add public key to GitHub > Settings > SSH Keys
  4. Retry: git push origin main
```

### Observation for SSH Verification
```json
{
  "action": "ssh.verify",
  "command": "ls -l ~/.ssh/id_ed25519",
  "expected_result": { "exit_code": 0, "file_exists": true },
  "actual_result": { "exit_code": 0, "output": "-rw------- ..." },
  "verification": { "passed": true }
}
```

---

## How They Work Together

### Example: Closeout Execution

```
Session: close-session-1
Agent: Claude Sonnet 4.5

PHASE 1: Autosave Reconciliation
  obs-001: lugs.reconcile
    ✅ Status: 2 autosave lugs reconciled
    ✅ Verified: session-summary lug created

PHASE 2: State Updates
  obs-002: state.update
    ✅ Status: session_count incremented to 28
    ✅ Verified: timestamp updated

PHASE 3: Git Operations
  obs-003: git.status
    ✅ Status: 2 files modified
    ✅ Verified: files exist and have changes
  
  obs-004: git.add
    ✅ Status: 2 files staged
    ✅ Verified: git status shows staged
  
  obs-005: git.commit
    ✅ Status: Commit 6c3511c created
    ✅ Verified: commit hash matches
  
  obs-006: ssh.verify
    ❌ Status: SSH key permission denied
    ❌ Verified: FAILED (exit code 255 vs expected 0)
    🚨 FAIL SIGNAL: Fix SSH key
       Remediation: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
  
  obs-007: git.push
    ⏭️  SKIPPED due to failed SSH
    (Not executed because ssh.verify failed)

PHASE 4: Verification
  obs-008: git.log.verify
    ⏭️  SKIPPED due to failed push

RESULT:
  ❌ CLOSEOUT INCOMPLETE
  ├─ Blocker: SSH authentication failed (obs-006)
  ├─ Last successful: git.commit (obs-005)
  ├─ Action: Fix SSH, run closeout again
  └─ Idempotency: Safe to retry (commit already exists)
```

### Next Session Recovery

```
Agent: Gemini (new agent)

Step 1: Read observations.jsonl
  Sees: obs-001 through obs-008
  Finds: Last failed action was obs-006 (ssh.verify)

Step 2: Check if already done
  before_any_action("git.push", {})
  Result: Not successfully pushed yet (obs-006 blocked it)

Step 3: Fix blocker
  Verify SSH key is now set up correctly
  obs-009: ssh.verify
    ✅ Status: SSH key exists and is accessible
    ✅ Verified: ssh -T git@github.com returns 1 + "authenticated"

Step 4: Retry git push (idempotent)
  obs-010: git.push
    ✅ Status: Push succeeded
    ✅ Verified: Commit visible on origin/main

Step 5: Complete verification
  obs-011: git.log.verify
    ✅ Status: Commit 6c3511c found on remote
    ✅ Verified: git log origin/main shows commit

RESULT:
  ✅ CLOSEOUT COMPLETE
  ├─ All phases executed
  ├─ All verifications passed
  └─ Commit on remote confirmed
```

---

## Multi-Agent Safety

### How Agents Work Together

```
Agent A (Session 1):
├─ obs-001: file.create "wai-closeout-enhanced.md"
│  ✅ File created, verified
├─ obs-002: git.add (file)
│  ✅ Staged, verified
├─ obs-003: git.commit
│  ✅ Commit created, verified
└─ obs-004: git.push
   ❌ FAILED (SSH issue)

Agent B (Session 2):
├─ Read observations.jsonl
├─ See: File already created (obs-001)
├─ See: Commit already made (obs-003)
├─ Decision: Skip duplicate work
├─ Focus: Fix blocker (SSH) and retry push
├─ obs-005: ssh.verify
│  ✅ SSH fixed
├─ obs-006: git.push RETRY
│  ✅ Push succeeds (idempotent)
└─ CLOSEOUT COMPLETE

Result:
✅ No duplicate work
✅ Agent A identified blocker
✅ Agent B fixed blocker
✅ Single file created once
✅ Single commit pushed once
✅ Both agents' work tracked in observations
```

---

## Size & Lifecycle Management

### Observation Log Size

```
Per observation: ~500 bytes
Per session (typical): 20-50 observations = 10-25 KB
Size limit: 0.5 MB per session

Archive strategy:
├─ Current session: Full detail (all observations)
├─ Last 5 sessions: Full detail (for playback)
└─ Older sessions: Summarized (action + outcome)
```

### Session Metadata

```json
{
  "session_id": "close-session-1",
  "started_at": "2026-02-08T14:00:00Z",
  "agent": "Claude Sonnet 4.5",
  "observations_count": 8,
  "observations_file": "WAI-Spoke/observations.jsonl",
  "succeeded": false,
  "failure_reason": "git.push failed - SSH auth issue",
  "recovery_steps": [
    "Fix SSH key",
    "Run: git push origin main",
    "Run: closeout to complete"
  ]
}
```

---

## Key Principles

### 1. **No Assumptions**
```
❌ "Assume git.push worked"
✅ "Execute git.push, capture exit code, verify = 0"
```

### 2. **Fail Fast**
```
❌ "Keep going even if verification fails"
✅ "Fail immediately, alert user, suggest fix"
```

### 3. **Audit Everything**
```
❌ "Action happened, nothing recorded"
✅ "Action recorded, expected vs actual logged"
```

### 4. **Multi-Agent Safe**
```
❌ "Multiple agents duplicate work"
✅ "All agents read observations before acting"
```

### 5. **Session Continuity**
```
❌ "No record of what happened"
✅ "Complete playback available in observations.jsonl"
```

---

## Implementation Roadmap

### Immediate (Next Session)

1. **Initialize observations.jsonl**
   ```bash
   touch WAI-Spoke/observations.jsonl
   ```

2. **Fix SSH Key Issue**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
   # Add public key to GitHub Settings > SSH Keys
   ```

3. **Retry Closeout**
   ```bash
   closeout
   # Should complete successfully with all observations logged
   ```

### Short Term (This Sprint)

- [ ] Create observations.jsonl
- [ ] Update closeout skill to use observations
- [ ] Add idempotency checks (`before_any_action()`)
- [ ] Implement SSH verification observations
- [ ] Add session playback to briefing

### Medium Term (Phase Implementation)

- [ ] Integrate observations into all skills
- [ ] Build multi-agent coordination layer
- [ ] Create observation playback dashboard
- [ ] Set up archive strategy

---

## Summary

### Layer 1: Enhanced Closeout
**Provides:** Git completeness guarantee, fail signals, version control

### Layer 2: Observation System
**Provides:** Action auditing, verification, idempotency, multi-agent safety

### Layer 3: SSH Facts
**Provides:** Wheel-wide defaults, consistent authentication approach

### Together They Ensure

✅ **No hallucinations** - every action verified  
✅ **No silent failures** - alerts on unexpected results  
✅ **No duplicate work** - observations prevent re-execution  
✅ **Complete auditability** - full playback available  
✅ **Safe multi-agent** - shared observations prevent conflicts  
✅ **Session continuity** - recovery path clear  

---

**Result:** A system so reliable that you can trust the output completely.
