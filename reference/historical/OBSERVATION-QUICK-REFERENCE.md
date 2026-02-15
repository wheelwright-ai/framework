# Observation System - Quick Reference

**For developers using the observation system in skills and workflows.**

---

## Import What You Need

```python
# Observation logging
from wai.observation import get_logger, log_observation

# SSH/Git config
from wai.config import get_config

# Git operations with observation
from wai.utils.git import create_git_ops

# Session briefing
from wai.briefing import build_session_briefing

# Closeout workflow
from wai.closeout import CloseoutWorkflow
```

---

## Common Tasks

### Task 1: Log an Observation

```python
from wai.observation import log_observation

log_observation(
    action_id="my.action",
    action_category="git",  # or: file, state, sync
    action_description="Push to GitHub",
    plan="Push commits to origin/main",
    command="git push origin main",
    expected_result={
        "exit_code": 0,
        "output_contains": ["main"]
    },
    actual_result={
        "exit_code": 0,
        "stdout": "...",
        "stderr": None,
        "duration_ms": 2340,
    },
    verification={
        "passed": True,
        "checks": [
            {"name": "exit_code_zero", "passed": True},
            {"name": "output_contains_main", "passed": True},
        ]
    },
    session_id="closeout-20260208-001",
    agent="YourAgent",
    tags=["git-ops", "critical"],
)
```

### Task 2: Check If Action Already Done (Idempotency)

```python
from wai.observation import get_logger

logger = get_logger()
already_done = logger.check_already_done(
    action_id="git.push",
    session_id="closeout-001"
)

if already_done:
    print(f"✓ Already completed at {already_done['timestamp']}")
else:
    print("✗ Need to run this action")
    # proceed with action
```

### Task 3: Get Git Config (SSH, User, Email, etc.)

```python
from wai.config import get_config

config = get_config()

# SSH info
ssh_key = config.get_ssh_key_path()           # ~/.ssh/id_ed25519
ssh_verify = config.get_ssh_verify_command()  # ssh -T git@github.com

# Git user
author = config.get_git_author()              # User Name <email>
user = config.get_git_user()                  # User Name
email = config.get_git_email()                # user@example.com

# Git settings
remote = config.get_git_default_remote()      # origin
branch = config.get_git_default_branch()      # main
```

### Task 4: Run Git with Observation

```python
from wai.utils.git import create_git_ops

git = create_git_ops(repo_path=".")
session_id = "closeout-20260208-001"

# Stage all changes
obs_add = git.add_all(session_id, agent="MySkill")
if not obs_add["verification"]["passed"]:
    print(f"✗ Add failed: {obs_add['actual_result']['stderr']}")
    return

# Commit
obs_commit = git.commit("Work complete", session_id, agent="MySkill")
if not obs_commit["verification"]["passed"]:
    print(f"✗ Commit failed")
    if obs_commit.get("remediation"):
        print(f"→ {obs_commit['remediation']['suggested_next_step']}")
    return

# Push
obs_push = git.push(session_id=session_id, agent="MySkill")
if not obs_push["verification"]["passed"]:
    print(f"✗ Push failed")
    if obs_push.get("remediation"):
        print(f"→ Recovery steps: {obs_push['remediation']['recovery_steps']}")
```

### Task 5: Run Enhanced Closeout

```python
from wai.closeout import CloseoutWorkflow

workflow = CloseoutWorkflow(repo_path=".", dry_run=False)
summary = workflow.execute(message="Closeout: feature complete")

if summary["status"] == "complete":
    print("✅ Closeout successful")
else:
    print(f"❌ Closeout failed: {summary.get('error', 'Unknown error')}")
    # Check summary["phase_3_git_operations"] for details
```

### Task 6: Get Session Briefing for AI Context

```python
from wai.briefing import build_session_briefing

briefing = build_session_briefing(session_id="closeout-001")
print(briefing)  # Markdown formatted

# Or get just the summary
from wai.briefing import get_briefing
bf = get_briefing()
summary = bf.build_observation_summary()
# {total: X, complete: Y, failed: Z, categories: {...}}
```

---

## Workflow: Typical Closeout Skill

```python
#!/usr/bin/env python3
"""Closeout skill with observations."""

import sys
from wai.closeout import CloseoutWorkflow

def main():
    # Run closeout
    workflow = CloseoutWorkflow(repo_path=".", dry_run=False)
    summary = workflow.execute(message="Closeout: work cycle complete")
    
    # Display result
    if summary["status"] == "complete":
        print("\n✅ Closeout complete!")
        print(f"   Session: {summary['session_id']}")
        print(f"   Observations: {summary['observations_count']}")
        return 0
    else:
        print("\n❌ Closeout incomplete")
        
        # Show what failed
        phase3 = summary.get("phase_3_git_operations", {})
        if not phase3.get("all_passed"):
            print("   Git operations failed")
            print("   Check observations.jsonl for remediation steps")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## File Locations

```
Production Modules:
  wai/observation.py              ← Observation logging
  wai/config.py                   ← SSH/git config
  wai/utils/git.py                ← Git operations
  wai/closeout.py                 ← Closeout workflow
  wai/briefing.py                 ← Session briefing

Data Files:
  WAI-Spoke/observations.jsonl    ← Observation log
  WAI-Spoke/lugs/sshconfig-*.lug.json  ← SSH config

Documentation:
  OBSERVATION-SYSTEM-COMPLETE.md  ← Implementation details
  OBSERVATION-QUICK-REFERENCE.md  ← This file
```

---

## Observation Structure

Every observation has this structure:

```json
{
  "id": "obs-20260208-00001",
  "timestamp": "2026-02-08T14:32:15.123456Z",
  "session_id": "closeout-001",
  "agent": "CloseoutWorkflow",
  "action": {
    "id": "git.push",
    "category": "git",
    "description": "Push to origin/main"
  },
  "plan": "Push commits to GitHub",
  "command": "git push origin main",
  "expected_result": {"exit_code": 0, ...},
  "actual_result": {"exit_code": 0, "stdout": "...", ...},
  "verification": {"passed": true, "checks": [...]},
  "idempotency": {"idempotent": true, "safe_to_retry": false},
  "remediation": null,  # or {issue: ..., suggested_next_step: ...}
  "status": "complete",  # or "failed"
  "tags": ["git-ops", "critical"]
}
```

---

## SSH/Git Config Structure

SSH config lug (sshconfig-*.lug.json):

```json
{
  "id": "sshconfig-abc123",
  "type": "sshconfig",
  "wheel_id": "7a1d9c5b3e2f",
  "ssh": {
    "key_path": "~/.ssh/id_ed25519",
    "key_type": "ed25519",
    "key_passphrase": null,
    "verify_command": "ssh -T git@github.com"
  },
  "git": {
    "user": "User Name",
    "email": "user@example.com",
    "author_format": "User Name <user@example.com>",
    "default_remote": "origin",
    "default_branch": "main"
  },
  "github": {
    "host": "github.com",
    "api_endpoint": "https://api.github.com",
    "remote_format": "git@github.com:{owner}/{repo}.git"
  }
}
```

---

## Error Handling Patterns

### Pattern 1: Check Git Operation Result

```python
git = create_git_ops()
obs = git.push(session_id="sess-001")

if obs["verification"]["passed"]:
    print("✓ Push succeeded")
else:
    # Show error
    print(f"✗ Error: {obs['actual_result']['stderr']}")
    
    # Show remediation
    if obs.get("remediation"):
        print(f"Fix: {obs['remediation']['suggested_next_step']}")
```

### Pattern 2: Multi-Step with Stops

```python
git = create_git_ops()

obs1 = git.add_all(session_id)
if not obs1["verification"]["passed"]:
    print("✗ Add failed, stopping")
    return

obs2 = git.commit("msg", session_id)
if not obs2["verification"]["passed"]:
    print("✗ Commit failed, stopping")
    return

obs3 = git.push(session_id)
if not obs3["verification"]["passed"]:
    print("✗ Push failed, stopping")
    return

print("✓ All steps succeeded")
```

### Pattern 3: Check Before Acting (Idempotency)

```python
logger = get_logger()
session_id = "work-session-001"

# Check if already done
already = logger.check_already_done("my.action", session_id)
if already:
    print(f"✓ Already done: {already['timestamp']}")
    return already

# Not done, proceed
obs = do_my_action(session_id)
logger.log_observation(...)
```

---

## Gotchas & Tips

### ✅ DO
- Always check `verification["passed"]` after operations
- Always provide `session_id` (for tracking)
- Stop on first failure (don't continue on errors)
- Include remediation suggestions when you fail
- Tag observations (e.g., ["git-ops", "critical"])

### ❌ DON'T
- Don't assume success without checking result
- Don't continue after a failed critical operation
- Don't log without verification
- Don't hardcode SSH paths (use config)
- Don't skip git push (it's mandatory)

### 💡 TIPS
- Use `dry_run=True` for closeout to preview
- Check `remediation` field for suggested fixes
- Session IDs should be descriptive (closeout-20260208-001)
- Tag observations with action category + priority
- Cleanup old observations: `logger.cleanup_old_observations()`

---

## Common Session IDs

```
closeout-20260208-001      ← For closeout workflows
sync-20260208-145300       ← For sync operations
teach-20260208-150000      ← For teach operations
learn-20260208-150500      ← For learn operations
cli-init-20260208-200000   ← For CLI commands
manual-work-20260208-100   ← For manual operations
```

---

## Verify Your Setup

```bash
# Check SSH key exists
ls ~/.ssh/id_ed25519

# Test SSH connectivity
ssh -T git@github.com

# Check git config
git config user.name
git config user.email

# Check observations file
ls WAI-Spoke/observations.jsonl

# Check SSH config lug
ls WAI-Spoke/lugs/sshconfig-*.lug.json
```

---

## Get Help

- See `OBSERVATION-SYSTEM-COMPLETE.md` for implementation details
- See `SYSTEM-RELIABILITY-PROTOCOL.md` for architecture
- See individual module docstrings for API details
