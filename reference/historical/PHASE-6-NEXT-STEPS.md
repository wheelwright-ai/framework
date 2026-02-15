# Phase 6: Skill Integration - Next Steps

**Date:** 2026-02-08  
**Phase:** 6 of 8  
**Status:** Ready to begin  
**Est. Duration:** 2 hours  

---

## Context (From Phase 1-5)

Complete observation system now available:
- ✅ wai/observation.py - Core logging
- ✅ wai/config.py - SSH/git config
- ✅ wai/utils/git.py - Git operations
- ✅ wai/closeout.py - Closeout workflow
- ✅ wai/briefing.py - Session briefing

All modules tested and working.

---

## Phase 6 Goal

**Integrate observations into all workflow skills.**

Every skill that has a workflow (init, sync, teach, learn, etc.) should:
1. Load SSH config at startup
2. Log observations for every action
3. Check idempotency before acting
4. Use git operations from wai.utils.git

---

## Skills to Update

### Priority 1: Critical Workflow Skills

1. **wai-closeout.md** (`.claude/commands/`)
   - Already has closeout.py integration planned
   - Verify 4-phase workflow
   - Display observation summary
   - Add fail signal handling

2. **wai-init.md**
   - Load SSH config (for initial git setup)
   - Log observation for init actions
   - Create default sshconfig lug if needed

3. **wai-sync.md**
   - Load SSH config
   - Log observations for sync operations
   - Use git operations from utils.git

### Priority 2: Teaching Skills

4. **wai-teach.md**
   - Load SSH config
   - Log observations for teach actions
   - Integrate with closeout for git push

5. **wai-learn.md**
   - Load SSH config
   - Log observations for learn actions
   - Verify hub connection

### Priority 3: Advisory Skills

6. **wai-red-light.md**
   - Check failed observations
   - Suggest remediation
   - Offer recovery steps

7. **wai-green-light.md**
   - Validate observations passed
   - Confirm system state
   - Show audit trail

---

## Implementation Template

For each skill, follow this pattern:

### 1. Add config loading

```python
from wai.config import get_config

config = get_config()
git_author = config.get_git_author()
ssh_key = config.get_ssh_key_path()
```

### 2. Generate session ID

```python
import uuid
from datetime import datetime

session_id = f"{skill_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
```

### 3. Log before acting

```python
from wai.observation import log_observation

log_observation(
    action_id=f"{skill_name}.{action_name}",
    action_category="workflow",
    action_description=f"Perform {action_name}",
    plan="What we're doing",
    command="actual command",
    expected_result={...},
    actual_result={...},
    verification={...},
    session_id=session_id,
)
```

### 4. Check idempotency

```python
from wai.observation import get_logger

logger = get_logger()
already_done = logger.check_already_done(action_id, session_id)
if already_done:
    print(f"✓ Already completed")
    return
```

### 5. Use git operations

```python
from wai.utils.git import create_git_ops

git = create_git_ops()
obs = git.push(session_id=session_id)
if not obs["verification"]["passed"]:
    print(f"✗ Failed: {obs['actual_result']['stderr']}")
    if obs.get("remediation"):
        print(f"Fix: {obs['remediation']['suggested_next_step']}")
```

---

## Files to Modify

### Skill Files (`.claude/commands/`)
```
.claude/commands/wai.md                          ← Main entry point
.claude/commands/wai-init.md                     ← Initialize wheel
.claude/commands/wai-sync.md                     ← Sync with hub
.claude/commands/wai-teach.md                    ← Teach hub
.claude/commands/wai-learn.md                    ← Learn from hub
.claude/commands/wai-closeout.md                 ← Enhanced closeout
.claude/commands/wai-red-light.md                ← Check failures
.claude/commands/wai-green-light.md              ← Verify success
```

### CLI Files (`wai/cli/`)
```
wai/cli/main.py                                  ← Command dispatcher
wai/cli/commands/init.py                         ← Init logic
wai/cli/commands/sync.py                         ← Sync logic
(similar for other commands)
```

### Test Files
```
tests/test_skill_integration.py                  ← New tests
tests/test_observation_in_skills.py              ← New tests
```

---

## Testing Strategy

### Per-Skill Testing

For each skill after updating:

```bash
# Test the skill loads SSH config
python3 -c "from wai.config import get_config; config = get_config(); print(config.get_git_author())"

# Test observation logging works
python3 -c "from wai.observation import log_observation; log_observation(...)"

# Test the skill in dry-run mode (if applicable)
python3 -m wai.cli sync --dry-run
```

### Integration Testing

```bash
# Run full cycle
python3 -m wai.cli init
python3 -m wai.cli sync
python3 -m wai.cli closeout

# Check observations logged
python3 -c "from wai.observation import get_logger; logger = get_logger(); print(logger.summarize_session())"
```

---

## Checklist for Each Skill

- [ ] Import wai.config, wai.observation, wai.utils.git
- [ ] Load SSH config at skill start
- [ ] Generate session_id
- [ ] Log observation for main action
- [ ] Check idempotency before acting
- [ ] Use git operations from utils.git
- [ ] Handle failures gracefully with remediation
- [ ] Test with dry-run mode
- [ ] Verify observations logged
- [ ] Update docstring with observation info

---

## Example: Updated wai-init.md

```python
#!/usr/bin/env python3
"""Initialize new wheel with observation logging."""

from wai.config import get_config
from wai.observation import log_observation, get_logger
from datetime import datetime

def init_wheel(name: str, project_type: str):
    """Initialize wheel with observations."""
    
    # Generate session
    session_id = f"init-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Load config (creates if needed)
    config = get_config()
    git_author = config.get_git_author()
    
    # Log init action
    log_observation(
        action_id="wai.init",
        action_category="workflow",
        action_description=f"Initialize wheel: {name}",
        plan=f"Create new wheel directory and files",
        command=f"mkdir -p {name} && setup files",
        expected_result={"exit_code": 0, "files_created": ["WAI-Spoke/"]},
        actual_result={"exit_code": 0, "stdout": "Wheel created"},
        verification={"passed": True, "checks": [{"name": "dir_exists", "passed": True}]},
        session_id=session_id,
        tags=["init", "setup"],
    )
    
    print(f"✓ Wheel initialized: {name}")
    print(f"  Session: {session_id}")
    print(f"  Git author: {git_author}")

if __name__ == "__main__":
    init_wheel("my-project", "framework")
```

---

## Validation Checklist

After Phase 6 complete:

- [ ] All 7 workflow skills updated
- [ ] All skills load SSH config
- [ ] All skills log observations
- [ ] All skills check idempotency
- [ ] All skills use git from utils.git
- [ ] Tests pass for all skills
- [ ] Observations file populated after skill runs
- [ ] Session summaries accurate
- [ ] Remediation suggestions appear on failures
- [ ] Dry-run modes work without side effects

---

## Success Criteria

✅ All workflow skills integrated  
✅ Observations logged for every skill action  
✅ SSH config loaded from lugs (not hardcoded)  
✅ Git operations use observation logging  
✅ Idempotency prevents duplicate work  
✅ Fail signals stop further execution  
✅ All tests pass  

---

## Time Estimate

- Read existing skills: 20 min
- Update 7 skills: 80 min (10 min per skill)
- Write tests: 20 min
- Run full validation: 10 min

**Total: ~2 hours**

---

## Dependencies

Phases 1-5 must be complete:
- ✅ wai/observation.py
- ✅ wai/config.py
- ✅ wai/utils/git.py
- ✅ wai/closeout.py
- ✅ wai/briefing.py

All done ✓

---

## Next Phase After 6

**Phase 7: Briefing Integration**
- Hook session briefing into Claude context
- Display at session start
- Update AGENTS.md "Session Focus"
- Show failed observations
- Suggest remediation

---

## Questions?

- Observation API: See `wai/observation.py` docstrings
- Config API: See `wai/config.py` docstrings
- Git API: See `wai/utils/git.py` docstrings
- Examples: See `OBSERVATION-QUICK-REFERENCE.md`
- Full docs: See `OBSERVATION-SYSTEM-COMPLETE.md`

---

**Status:** ✅ Ready to implement Phase 6

**To begin:** Pick first skill, update with config + observations, test, move to next.
