# WAI Observation & Verification System

**"Trust but verify" - Every action must be observed, logged, and confirmed**

---

## Core Principle

> Do not execute actions and assume they succeeded.  
> Execute → Observe → Verify → Log.  
> If unexpected result occurs, inform user immediately.  
> No hallucinations. No silent failures.

This system ensures:
- ✅ **Accountability** - Proof of what was done
- ✅ **Idempotency** - Multi-agent work without conflicts
- ✅ **Auditability** - Complete playback of session activity
- ✅ **Reliability** - Failed actions caught immediately
- ✅ **Safety** - Unexpected results trigger alerts

---

## Architecture

```
Skill Execution Flow:
┌─────────────┐
│   PLAN      │  What we're going to do
└──────┬──────┘
       ↓
┌─────────────┐
│   EXECUTE   │  Actually run the command/action
└──────┬──────┘
       ↓
┌─────────────┐
│   OBSERVE   │  Capture output, exit code, state
└──────┬──────┘
       ↓
┌─────────────┐
│   VERIFY    │  Compare against expected result
└──────┬──────┘
       ↓
┌─────────────┐
│    LOG      │  Record observation to audit log
└──────┬──────┘
       ↓
┌─────────────┐
│   REPORT    │  Inform user of result
└─────────────┘
```

---

## 1. Observation Log Structure

### File Location
```
WAI-Spoke/observations.jsonl
```

### Schema

```json
{
  "id": "obs-20260208-001",
  "timestamp": "2026-02-08T14:32:15Z",
  "session_id": "close-session-1",
  "agent": "Claude Sonnet 4.5",
  "action": "git.push",
  "plan": "Push all commits to origin/main",
  "command": "git push origin main",
  "expected_result": {
    "exit_code": 0,
    "output_contains": ["Everything up-to-date", "pushing"],
    "files_changed": 0,
    "side_effect": "commits visible on github"
  },
  "actual_result": {
    "exit_code": 128,
    "output": "fatal: Could not read from remote repository...",
    "stderr": "Permission denied (publickey)",
    "files_changed": 0,
    "duration_ms": 234
  },
  "verification": {
    "passed": false,
    "match_expected": false,
    "unexpected_aspects": [
      "Exit code 128 (expected 0) - authentication failure",
      "Permission denied (publickey) - SSH key issue"
    ]
  },
  "user_action": "USER_INFORMED",
  "user_message": "🚨 GIT PUSH FAILED: Permission denied (publickey). Fix SSH key then retry.",
  "impact": "BLOCKS_COMPLETION",
  "idempotency": {
    "is_idempotent": false,
    "retry_strategy": "user_fixes_ssh_then_retry",
    "side_effects": "commit already on local, safe to retry"
  },
  "remediation": {
    "suggested_next_step": "Fix SSH key in ~/.ssh/",
    "verification_command": "ssh -T git@github.com",
    "retry_command": "git push origin main"
  }
}
```

### Log Entry Size Optimization

- Observations are **compact JSONL** (one entry per line)
- Large outputs **truncated to 1KB** with `[... truncated N bytes]`
- Kept under **0.5 MB per session**
- Older sessions archived (if needed)

---

## 2. Observation Categories

### Git Operations

```json
{
  "action": "git.status",
  "expected_result": {
    "exit_code": 0,
    "contains_files": true,
    "clean_repo": false
  }
}

{
  "action": "git.add",
  "expected_result": {
    "exit_code": 0,
    "files_staged": [".claude/commands/wai-closeout.md"]
  }
}

{
  "action": "git.commit",
  "expected_result": {
    "exit_code": 0,
    "output_contains": ["files changed", "insertion"],
    "commit_created": true
  }
}

{
  "action": "git.push",
  "expected_result": {
    "exit_code": 0,
    "output_contains": ["Everything up-to-date", "pushing"],
    "remote_updated": true
  }
}

{
  "action": "git.log.verify",
  "expected_result": {
    "exit_code": 0,
    "commit_visible_on_remote": true,
    "commit_hash": "6c3511c"
  }
}
```

### File Operations

```json
{
  "action": "file.create",
  "expected_result": {
    "file_exists": true,
    "file_size_bytes": 5670,
    "file_readable": true
  }
}

{
  "action": "file.edit",
  "expected_result": {
    "file_exists": true,
    "content_changed": true,
    "diff_lines": 45
  }
}

{
  "action": "file.delete",
  "expected_result": {
    "file_exists": false,
    "backup_created": true
  }
}
```

### State Operations

```json
{
  "action": "state.update",
  "expected_result": {
    "file_valid_json": true,
    "field_updated": "session_count",
    "new_value": 28
  }
}

{
  "action": "state.verify",
  "expected_result": {
    "file_readable": true,
    "json_valid": true,
    "required_fields_present": true
  }
}
```

---

## 3. Verification Protocol

### Before-Action
```
Create observation with plan and expected results
```

### Execute Action
```bash
git push origin main
# Capture: exit code, stdout, stderr, duration
```

### After-Action
```
Compare actual_result vs expected_result
If mismatch: unexpected_aspects = differences
If verification fails: ALERT USER IMMEDIATELY
Log the observation
```

---

## 4. Idempotency & Multi-Agent Work

### How Observations Enable Idempotency

```
Agent A (Session 1):
  ✅ obs-001: Create wai-closeout.md (succeeded)

Agent B (Session 2):
  - Read observations.jsonl
  - See: obs-001 already created this file
  - Decision: SKIP (already done per obs-001)
  - Result: No duplicate work

Multi-agent Safety:
  ✅ Shared observations.jsonl prevents duplicate work
  ✅ Each agent reads before acting
  ✅ Failed actions aren't repeated
  ✅ Idempotency fields guide retry decisions
```

---

## 5. Session Integration

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
  "last_successful_action": "git.commit 6c3511c"
}
```

### Next Session Playback

```
SESSION PLAYBACK: close-session-1
Started: 2026-02-08T14:00:00Z
Agent: Claude Sonnet 4.5

Timeline:
  14:00:15 ✅ lugs.reconcile → 2 lugs reconciled
  14:00:20 ✅ state.update → session_count=28
  14:00:25 ✅ git.status → 2 files modified
  14:00:30 ✅ git.add → 2 files staged
  14:00:35 ✅ git.commit → 6c3511c created
  14:00:40 ❌ git.push → FAILED
             Exit code: 128 (expected 0)
             Error: Permission denied (publickey)
             Fix: Add SSH key to GitHub
             Retry: git push origin main
  (blocked) git.log.verify

Status: INCOMPLETE
Last successful: git.commit 6c3511c
Blocker: SSH authentication
Recovery: Fix SSH, then retry git.push
```

---

## 6. SSH Key Facts (Wheel-Wide Default)

### Established Facts

```
SSH Key Location: ~/.ssh/id_ed25519
SSH Test Command: ssh -T git@github.com

When git.push fails with "Permission denied (publickey)":
  1. Verify SSH key: file.verify "~/.ssh/id_ed25519"
  2. Test SSH connection: execute "ssh -T git@github.com"
  3. If fails: Add public key to GitHub settings
  4. Retry: git push origin main
```

### Observation for SSH Verification

```json
{
  "action": "ssh.verify",
  "plan": "Check if SSH key is properly configured",
  "command": "ssh -T git@github.com",
  "expected_result": {
    "exit_code": 1,
    "output_contains": ["Hi username", "authenticated"]
  },
  "actual_result": {
    "exit_code": 255,
    "stderr": "Permission denied (publickey)"
  },
  "remediation": "Add ~/.ssh/id_ed25519.pub to GitHub settings"
}
```

---

## 7. Integration with Closeout Skill

Every phase includes observations:

```
Phase 1: Autosave Reconciliation
  ✅ observe(action="lugs.reconcile", expected={...})

Phase 2: State Updates
  ✅ observe(action="state.update", expected={...})

Phase 3: Git Operations
  ✅ observe(action="git.status", expected={...})
  ✅ observe(action="git.add", expected={...})
  ✅ observe(action="git.commit", expected={...})
  ✅ observe(action="git.push", expected={...})

Phase 4: Verification
  ✅ observe(action="git.log.verify", expected={...})

Rule: Any observation with verification.passed=false
      immediately raises FAIL_SIGNAL and halts closeout
```

---

## 8. Size Management (< 0.5 MB)

### Strategies

1. **Truncate outputs** - Max 1KB per observation
2. **Compress old sessions** - Archive after 5 sessions
3. **Summarize successes** - 1 line for routine passes
4. **Keep failures detailed** - For audit and recovery

### Size Calculation

```
Average observation: 500 bytes
Per-session limit: 0.5 MB
Max observations/session: 1,000

Typical session: 20-50 observations
Size: 10-25 KB per session
```

---

## 9. Implementation Pattern

### In Any Skill

```python
def perform_action_with_observation(
    action: str,
    plan: str,
    command: str,
    expected_result: dict
) -> Observation:
    
    # Create observation before execution
    obs = Observation(
        id=generate_id(),
        timestamp=now(),
        session_id=get_session_id(),
        agent=get_agent_name(),
        action=action,
        plan=plan,
        command=command,
        expected_result=expected_result
    )
    
    # Execute action
    result = execute(command)
    obs.actual_result = {
        "exit_code": result.exit_code,
        "stdout": truncate(result.stdout, 1024),
        "stderr": truncate(result.stderr, 1024),
        "duration_ms": result.duration_ms
    }
    
    # Verify
    obs.verification = verify(obs.actual_result, obs.expected_result)
    
    # Log
    append_observations_jsonl(obs)
    
    # Report
    if not obs.verification.passed:
        alert_user(f"🚨 {obs.action.upper()} FAILED")
        show_unexpected_aspects(obs.verification.unexpected_aspects)
        show_remediation(obs.remediation)
        raise ActionFailed(obs)
    
    return obs
```

### Before Taking Any Action

```python
def check_if_already_done(action: str, parameters: dict) -> bool:
    """Check observations to see if this was already done"""
    observations = load_observations_jsonl()
    
    for obs in observations:
        if (obs.action == action and 
            obs.parameters == parameters and 
            obs.verification.passed):
            return True
    
    return False
```

---

## 10. Multi-Agent Example

### Session 1: Agent A (Claude)
```
14:00:35 ✅ obs-005: git.commit 6c3511c
         (file: .claude/commands/wai-closeout-enhanced.md)

14:00:40 ❌ obs-006: git.push FAILED
         (error: Permission denied publickey)
```

### Session 2: Agent B (Gemini)
```
Agent B reads observations.jsonl
Sees: git.commit succeeded in obs-005
      git.push failed in obs-006 due to SSH

Agent B (no duplication):
14:01:00 ✅ obs-007: ssh.verify
         (SSH key now fixed)

14:01:05 ✅ obs-008: git.push RETRY
         (succeeds this time, idempotent)
```

---

## Summary

The **WAI Observation & Verification System** ensures:

✅ **Accountability** - Every action observed and logged  
✅ **Reliability** - Unexpected results trigger alerts  
✅ **Idempotency** - Safe multi-agent work  
✅ **Auditability** - Complete playback of activity  
✅ **Safety** - No silent failures  

**Key Rules:**

1. **Execute → Observe → Verify → Log** (always in order)
2. **If verification fails** → Alert user immediately (don't continue)
3. **SSH key is ~/.ssh/id_ed25519** (wheel-wide fact)
4. **Observations.jsonl is shared** (all agents can read it)
5. **Check if already done** (before taking any action)
6. **Keep logs under 0.5 MB** (compress old sessions)
7. **Session_id links observations to session** (for playback)

**Result:** A system where multi-agent work is safe, auditable, and never hallucinates about what was completed.
