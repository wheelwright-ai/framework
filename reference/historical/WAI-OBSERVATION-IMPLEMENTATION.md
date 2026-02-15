# WAI Observation System - Implementation Guide

**How to integrate observations into existing skills**

---

## Phase 1: Create observations.jsonl

### Initialize File

```bash
# Create empty observations log
touch WAI-Spoke/observations.jsonl

# Verify it's readable
ls -lah WAI-Spoke/observations.jsonl
```

### First Entry (Schema Test)

```json
{"id": "obs-init-001", "timestamp": "2026-02-08T14:00:00Z", "session_id": "system-init", "agent": "Framework", "action": "system.initialize", "plan": "Initialize observations system", "status": "initialized"}
```

---

## Phase 2: Update Closeout Skill

### Pattern: Every Action Gets Observed

**Before:**
```python
def closeout():
  git.push()  # Assume it works
```

**After:**
```python
def closeout():
  obs = observe_git_push()
  if not obs.verification.passed:
    raise FAIL_SIGNAL(obs)  # Don't continue
```

### Implement `observe_git_push()`

```python
def observe_git_push():
  """Execute git push with full observation"""
  
  obs = Observation(
    id=f"obs-{now().isoformat()}",
    timestamp=now(),
    session_id=get_session_id(),
    agent="Claude",
    action="git.push",
    plan="Push commits to origin/main",
    command="git push origin main",
    expected_result={
      "exit_code": 0,
      "output_contains": ["Everything up-to-date", "pushing"],
      "side_effect": "commits visible on remote"
    }
  )
  
  # Execute
  result = execute("git push origin main")
  
  # Capture actual result
  obs.actual_result = {
    "exit_code": result.exit_code,
    "stdout": result.stdout[:1024],  # Truncate
    "stderr": result.stderr[:1024],
    "duration_ms": result.duration
  }
  
  # Verify
  obs.verification = {
    "passed": result.exit_code == 0,
    "unexpected_aspects": []
  }
  
  if result.exit_code != 0:
    obs.verification.unexpected_aspects.append(
      f"Exit code {result.exit_code} (expected 0)"
    )
  
  # Log
  append_to_jsonl("WAI-Spoke/observations.jsonl", obs)
  
  # Report
  if not obs.verification.passed:
    show_fail_signal(obs)
  
  return obs
```

---

## Phase 3: Add Idempotency Checks

### Check Before Acting

```python
def before_any_action(action, parameters):
  """Check if this action was already successfully completed"""
  
  observations = load_jsonl("WAI-Spoke/observations.jsonl")
  
  for obs in observations:
    if (obs.action == action and 
        obs.parameters == parameters and 
        obs.verification.passed):
      
      return (True, obs)  # Already done
  
  return (False, None)  # Not done yet
```

### Use in Skill

```python
def create_observation_file():
  """Create WAI-Observation-System.md"""
  
  # Check if already done
  already_done, prev_obs = before_any_action(
    "file.create",
    {"path": "WAI-OBSERVATION-SYSTEM.md"}
  )
  
  if already_done:
    print(f"✅ Already created in {prev_obs.session_id}")
    return  # Skip
  
  # Not done, so create
  obs = observe_file_create(
    "WAI-OBSERVATION-SYSTEM.md",
    content=...
  )
```

---

## Phase 4: Observation for SSH Fix

### Verify SSH Key Setup

```python
def verify_ssh_setup():
  """Verify SSH key is properly configured"""
  
  obs = Observation(
    action="ssh.verify",
    plan="Check if SSH key exists and is accessible",
    command="ls -l ~/.ssh/id_ed25519",
    expected_result={
      "exit_code": 0,
      "file_exists": True,
      "file_readable": True
    }
  )
  
  result = execute("ls -l ~/.ssh/id_ed25519")
  obs.actual_result = {
    "exit_code": result.exit_code,
    "output": result.stdout
  }
  
  obs.verification.passed = result.exit_code == 0
  
  if not obs.verification.passed:
    obs.remediation = {
      "issue": "SSH key not found at ~/.ssh/id_ed25519",
      "next_step": "Generate SSH key or restore from backup",
      "command": "ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519"
    }
  
  append_to_jsonl("WAI-Spoke/observations.jsonl", obs)
  
  return obs
```

### Test SSH Connection

```python
def verify_ssh_github():
  """Test SSH connection to GitHub"""
  
  obs = Observation(
    action="ssh.test_github",
    plan="Verify SSH key works with GitHub",
    command="ssh -T git@github.com",
    expected_result={
      "exit_code": 1,  # GitHub returns 1 for auth success
      "output_contains": ["Hi ", "authenticated"]
    }
  )
  
  result = execute("ssh -T git@github.com 2>&1")
  obs.actual_result = {
    "exit_code": result.exit_code,
    "output": result.stdout + result.stderr
  }
  
  obs.verification.passed = (
    result.exit_code == 1 and 
    "authenticated" in result.stdout
  )
  
  if not obs.verification.passed:
    obs.remediation = {
      "issue": "SSH key not configured for GitHub",
      "next_step": "Add public key to GitHub Settings > SSH Keys",
      "get_public_key": "cat ~/.ssh/id_ed25519.pub"
    }
  
  append_to_jsonl("WAI-Spoke/observations.jsonl", obs)
  
  return obs
```

---

## Phase 5: Session Playback

### Load and Display Observations

```python
def show_session_playback(session_id):
  """Display timeline of session activity"""
  
  observations = load_jsonl("WAI-Spoke/observations.jsonl")
  session_obs = [o for o in observations 
                 if o.session_id == session_id]
  
  print(f"\nSESSION PLAYBACK: {session_id}")
  print(f"Total actions: {len(session_obs)}\n")
  
  for obs in session_obs:
    status = "✅" if obs.verification.passed else "❌"
    print(f"{obs.timestamp} {status} {obs.action}")
    print(f"  Plan: {obs.plan}")
    
    if not obs.verification.passed:
      print(f"  Error: {obs.verification.unexpected_aspects[0]}")
      if obs.remediation:
        print(f"  Fix: {obs.remediation.get('suggested_next_step')}")
    
    print()
```

### In Session Briefing

```python
def update_session_briefing():
  """Show current session status in briefing"""
  
  prev_session = get_last_session()
  obs = load_jsonl("WAI-Spoke/observations.jsonl")
  session_obs = [o for o in obs if o.session_id == prev_session]
  
  if not session_obs:
    return "No previous session"
  
  # Count outcomes
  passed = sum(1 for o in session_obs if o.verification.passed)
  failed = sum(1 for o in session_obs if not o.verification.passed)
  
  # Find blocker
  blockers = [o for o in session_obs 
              if not o.verification.passed and 
              o.impact == "BLOCKS_COMPLETION"]
  
  print(f"""
📋 PREVIOUS SESSION STATUS
├─ Completed: {passed} actions ✅
├─ Failed: {failed} action(s) ❌
{"" if not blockers else f"├─ Blocker: {blockers[0].action}"}
└─ Recovery: {blockers[0].remediation.get('suggested_next_step') if blockers else 'None needed'}
  """)
```

---

## Phase 6: Multi-Agent Coordination

### Before Parallel Work

```python
def check_ongoing_work():
  """Check if other agents are working"""
  
  observations = load_jsonl("WAI-Spoke/observations.jsonl")
  
  # Find recent activity (last 1 hour)
  recent = [o for o in observations 
            if (now() - o.timestamp).seconds < 3600]
  
  if recent:
    agents = set(o.agent for o in recent)
    print(f"⚠️  Recent activity by: {agents}")
    print("Consider waiting or reading observations.jsonl")
    
    # Show last action
    last = max(recent, key=lambda o: o.timestamp)
    print(f"Last: {last.action} ({last.timestamp})")
```

### Prevent Duplicate Work

```python
def safe_parallel_execute(action, parameters):
  """Check before taking action to avoid duplicates"""
  
  # Read current observations
  observations = load_jsonl("WAI-Spoke/observations.jsonl")
  
  # Check if already done
  for obs in observations:
    if (obs.action == action and 
        obs.parameters == parameters):
      
      if obs.verification.passed:
        print(f"✅ Already completed in {obs.session_id}")
        return False  # Skip
      elif obs.idempotency.can_safely_retry:
        print(f"🔄 Retrying (failed before in {obs.session_id})")
        return True  # Safe to retry
      else:
        print(f"⚠️  Previous attempt failed (not idempotent)")
        return False  # Don't retry
  
  return True  # New action, proceed
```

---

## Phase 7: Integrate with Existing Skills

### Apply to All Skills

Every skill that runs commands should use observations:

1. **wai-closeout.md**
   - git.status
   - git.add
   - git.commit
   - git.push
   - git.log.verify

2. **wai-red-light.md**
   - quality.check
   - lint.run
   - test.run

3. **wai-green-light.md**
   - verification.run
   - deployment.check

4. **wai-shipit.md**
   - quality.gate
   - benchmark.run
   - documentation.sync
   - (calls closeout)

---

## Example: Updated Closeout with Observations

```python
def closeout(bump_version=None, dry_run=False):
  """Enhanced closeout with full observations"""
  
  session_id = get_session_id()
  observations = []
  
  try:
    # Phase 1: Reconciliation
    print("Phase 1: Autosave Reconciliation")
    obs = observe_lug_reconciliation()
    if not obs.verification.passed:
      raise_fail_signal(obs)
    observations.append(obs)
    
    # Phase 2: State Updates
    print("Phase 2: State Updates")
    obs = observe_state_update()
    if not obs.verification.passed:
      raise_fail_signal(obs)
    observations.append(obs)
    
    # Phase 3: Git Operations
    print("Phase 3: Git Operations")
    
    obs = observe_git_status()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs)
    
    obs = observe_git_add()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs)
    
    obs = observe_git_commit()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs)
    
    # Check SSH before pushing
    obs = verify_ssh_setup()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs, message="Fix SSH first")
    
    obs = observe_git_push()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs)
    
    # Phase 4: Verification
    print("Phase 4: Verification")
    obs = observe_git_log_verify()
    observations.append(obs)
    if not obs.verification.passed:
      raise_fail_signal(obs)
    
    # Success!
    print_success_report(observations)
    
  except FailSignal as e:
    print_fail_report(e.observation)
    raise
```

---

## Summary: Implementation Checklist

- [ ] Create WAI-Spoke/observations.jsonl
- [ ] Update closeout skill to use observations
- [ ] Add idempotency checks before actions
- [ ] Implement SSH verification observations
- [ ] Add session playback to briefing
- [ ] Test multi-agent coordination
- [ ] Document observation patterns
- [ ] Train all skills to use observations

**Result:** Every action is observed, verified, logged, and auditable.
