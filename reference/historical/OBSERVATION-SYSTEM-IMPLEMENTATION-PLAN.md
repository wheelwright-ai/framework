# Observation System Implementation Plan

**Date:** 2026-02-08  
**Scope:** Build observation system + SSH config lug + skill integration  
**Outcome:** Complete reliability layer with session lookback across all workflow skills  

---

## Concept Overview

**Three integrated components:**

1. **Observation System** (observations.jsonl)
   - Every workflow skill logs: plan → execute → verify → result
   - Session playback shows what happened and why
   - Multi-agent safety: before acting, check if already done

2. **SSH/Git Config Lug** (customizable user config)
   - Store SSH key location, git config, authentication details
   - Skills read this lug instead of hardcoded facts
   - User can customize per-wheel SSH setup

3. **Skill Integration** (all workflow skills)
   - closeout, teach, learn, sync, init
   - Each uses observation system
   - Each reads SSH/git config from lug
   - Complete end-to-end audit trail

---

## Implementation Checklist

### Phase 1: Foundation (observations.jsonl + schema)
- [ ] Create WAI-Spoke/observations.jsonl (empty JSONL)
- [ ] Define observation schema (with examples)
- [ ] Create wai/observation.py module
  - `log_observation(action, plan, command, expected, actual, verified)`
  - `read_observations()`
  - `check_already_done(action_id)`
  - `remediate_on_failure(obs)`

### Phase 2: SSH/Git Config Lug
- [ ] Create lug template: `ssh-config.lug.json`
  - Fields: ssh_key_path, ssh_key_type, git_user, git_email, git_remote, github_host
  - Defaults: ed25519, ~/.ssh/id_ed25519, etc.
- [ ] Create wai/config.py to load SSH config lug
  - `load_ssh_config()` → reads from lugs.jsonl
  - `get_ssh_key_path()`, `get_git_user()`, etc.

### Phase 3: Enhanced Closeout Skill
- [ ] Update wai-closeout-enhanced.md
  - Phase 1: Load SSH config lug
  - Phase 2: Reconcile + observe
  - Phase 3: State updates + observe
  - Phase 4: Git ops + observe + verify
  - Phase 5: Verify & alert on fail signals
- [ ] Create wai/closeout.py (Python execution)
  - Implements 4-phase model
  - Calls observation.log_observation()
  - Reads SSH config via config.load_ssh_config()

### Phase 4: Skill Integration (all workflows)
- [ ] Update wai/cli/main.py
  - init command: log observations
  - sync command: log observations
  - Other commands: wrap with observation logging
- [ ] Add observation context to all skill files
- [ ] Update wai-red-light.md, wai-green-light.md with observation checks

### Phase 5: Session Briefing + Playback
- [ ] Create wai/briefing.py
  - `build_session_briefing()` - includes observation summary
  - `playback_observations()` - show what happened in session
- [ ] Update Claude hook to display observation playback
- [ ] Show in briefing: "Session observations: X actions logged, all verified"

### Phase 6: Testing + Validation
- [ ] Unit tests for observation.py
- [ ] Unit tests for config.py
- [ ] Integration test: closeout workflow with observations
- [ ] Multi-agent test: two agents reading same observations.jsonl

### Phase 7: Documentation + Migration
- [ ] Update WAI-State.md with observation examples
- [ ] Update CLI help with observation references
- [ ] Create migration script to backfill observations for past sessions
- [ ] Update templates/WAI-Spoke/ with observation files

---

## Technical Design

### Observation Schema (observations.jsonl)

```json
{
  "id": "obs-20260208-001",
  "timestamp": "2026-02-08T14:32:15.123456Z",
  "session_id": "cli-init-20260208-001",
  "agent": "Claude Sonnet 4.5",
  "environment": {
    "tool": "claude-code",
    "machine": "WSL2-Ubuntu",
    "os": "Linux"
  },
  "action": {
    "id": "git.push",
    "category": "git",
    "description": "Push commits to origin/main"
  },
  "plan": "Push local commits to GitHub origin/main branch after commit verification",
  "command": "git push origin main",
  "expected_result": {
    "exit_code": 0,
    "output_contains": ["main", ".."]
  },
  "actual_result": {
    "exit_code": 0,
    "stdout": "Enumerating objects: 42...",
    "stderr": null,
    "duration_ms": 2340
  },
  "verification": {
    "passed": true,
    "checks": [
      { "name": "exit_code_zero", "passed": true },
      { "name": "output_contains_main", "passed": true },
      { "name": "git_log_verify", "passed": true, "remote_head_matches": true }
    ]
  },
  "idempotency": {
    "idempotent": true,
    "safe_to_retry": true
  },
  "remediation": null,
  "status": "complete",
  "tags": ["closeout", "git-ops", "critical"]
}
```

### SSH Config Lug Schema

```json
{
  "id": "sshconfig-framework-001",
  "type": "sshconfig",
  "wheel_id": "7a1d9c5b3e2f",
  "version": "1.0.0",
  "created": "2026-02-08T00:00:00Z",
  "ssh": {
    "key_path": "~/.ssh/id_ed25519",
    "key_type": "ed25519",
    "key_passphrase": null,
    "verify_command": "ssh -T git@github.com"
  },
  "git": {
    "user": "Mario Vaccari",
    "email": "mario@wheelwright.ai",
    "author_format": "Mario Vaccari <mario@wheelwright.ai>",
    "default_remote": "origin",
    "default_branch": "main"
  },
  "github": {
    "host": "github.com",
    "api_endpoint": "https://api.github.com",
    "remote_format": "git@github.com:{owner}/{repo}.git"
  },
  "verification": {
    "last_ssh_test": "2026-02-08T14:32:15Z",
    "last_ssh_success": true,
    "git_config_valid": true
  },
  "tags": ["ssh", "git", "authentication", "wheel-wide"]
}
```

### Files to Create/Modify

```
Framework structure:
wai/
├── observation.py          (NEW - observation logging)
├── config.py               (NEW - SSH/git config loading)
├── closeout.py             (NEW - closeout workflow)
├── briefing.py             (NEW - session briefing with observations)
├── cli/
│   └── main.py             (MODIFY - integrate observations)
└── utils/
    └── git.py              (NEW - git commands with observations)

WAI-Spoke/
├── observations.jsonl      (NEW - observation log)
├── lugs/
│   └── sshconfig-*.lug.json (NEW - SSH config lug)
└── WAI-Lugs.jsonl          (MODIFY - add observation metadata)

Templates:
├── templates/WAI-Spoke/
│   ├── observations.jsonl  (NEW - template)
│   └── lugs/sshconfig.lug.json (NEW - template)
└── .claude/commands/
    └── wai-closeout-enhanced.md (MODIFY - integrate observations)

Documentation:
├── WAI-OBSERVATION-SYSTEM.md (EXISTS - reference)
└── OBSERVATION-SYSTEM-IMPLEMENTATION-PLAN.md (THIS FILE)
```

---

## Execution Order

1. **Create observation.py module** (core logging)
2. **Create config.py module** (SSH/git loading)
3. **Create SSH config lug** (user customization)
4. **Update closeout.py** (enhanced closeout with obs)
5. **Integrate into CLI** (all commands log observations)
6. **Build session briefing** (playback observations)
7. **Write tests** (complete coverage)
8. **Document & distribute** (templates, migration)

---

## Success Criteria

✅ Observation system logs every skill workflow  
✅ SSH/git config customizable per-wheel via lug  
✅ Session briefing shows observation playback  
✅ Multi-agent safety: check before acting  
✅ All workflow skills integrated  
✅ Tests pass (unit + integration)  
✅ Ready for CLI rebuild  

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| observations.jsonl grows large | Size limit <0.5MB, auto-archive old observations |
| Lug corruption breaks git config | Validation on load, fallback to defaults |
| Multi-agent concurrent writes | Observation IDs are atomic, idempotency checks |
| SSH key permissions change | Verification step in observation system |

---

## Timeline Estimate

- Phase 1 (observation.py): 30 min
- Phase 2 (config.py + lug): 20 min
- Phase 3 (closeout.py): 40 min
- Phase 4 (CLI integration): 30 min
- Phase 5 (briefing): 20 min
- Phase 6 (tests): 40 min
- Phase 7 (docs): 20 min

**Total:** ~3.5 hours for complete implementation

---

## Next Steps

1. ✅ Approve this plan
2. Create Phase 1-2 (core modules)
3. Create Phase 3 (closeout workflow)
4. Integrate Phase 4-5 (CLI + briefing)
5. Test Phase 6 (validation)
6. Deploy Phase 7 (docs)
7. Resume CLI rebuild
