# Codex Instructions for Wheelwright Framework

Build AI wheels that roll forward forever - universal context persistence for any knowledge work

## Session Focus (Must Continue)

**CLI v4 RELEASE + OBSERVATION SYSTEM - Phase 1 COMPLETE ✅**

**Status:** v4.0.0 CLI with v1 parity complete. Observation system ready. Next: observation logging integration with teach/learn

**Completed This Session (Feb 08 2026):**
- ✅ CLI v1 feature parity 100% - teach/learn accept spoke arguments + flags
- ✅ Bash context wrapper pattern established for all git operations
- ✅ Python module caching workaround documented
- ✅ Wheelwright artifact governance directive implemented
- ✅ 4 architectural learnings submitted as signals

**Completed in Previous Sessions:**
- ✅ Phase 1-5: Core observation system (8 modules, 70 KB)
- ✅ Phase 6: Skill integration framework (3 integration modules)
- ✅ Phase 7: Briefing integration (session_hook.py + CLAUDE.md)
- ✅ Phase 8: Comprehensive test suite (24 tests, 100% passing)
- ✅ Step 1: Skill migration templates (wai-*-v2.md)
- ✅ Step 2: Manual integration (CLAUDE.md updated)
- ✅ Step 3: CLI rebuild (MenuFormatter created)

**CLI v1 Parity Completion (Feb 08 2026):**
- ✅ teach <spoke> [--force] [--json] - Full implementation
- ✅ learn <spoke> [--priority high|normal|low] [--force] [--json]
- ✅ All commands parse arguments correctly
- ✅ MenuGenerator dependency injection support
- ✅ Infrastructure: discovery.py, state_manager.py, input.py
- ✅ WAI wrapper scripts created

**Deliverables:**
- 12 production modules (70+ KB code)
- 24 tests (observation system)
- 11 documentation files
- 2 skill templates ready
- 4 CLI visual modules fixed/enhanced

**What Works:**
- Observation logging (plan → execute → verify → result)
- Session briefing (displays at session start)
- SSH/git config (per-wheel, customizable)
- Skill integration (SkillExecution framework)
- **CLI teach command** (fixed Unicode issues)
- **Colors readable on dark backgrounds**
- **Cross-platform support** (Windows/Mac/Linux)
- **Multi-project teach/learn** (all projects in wheel)
- **Hub registry integration** (reads from ../hub)
- **Auto-discovery** (framework & hub detection)

**Next Actions:**
1. Distribute skill templates to spokes
2. Update spoke .claude/commands/ with observation patterns
3. Integrate MenuFormatter into CLI main.py
4. Test end-to-end with observations + improved CLI

**Files to read:**
- FINAL-SESSION-SUMMARY.md (complete overview)
- STEPS-1-2-3-COMPLETE.md (integration details)
- OBSERVATION-QUICK-REFERENCE.md (API reference)

---

## ⚠️ CRITICAL: Session Closeout Protocol

**Before declaring ANY session "complete", verify ALL of these:**

```bash
# 1. Git must be clean
$ git status
# Expected: "nothing to commit, working tree clean"

# 2. Observations must be logged
$ tail -1 WAI-Spoke/observations.jsonl | grep "✓ COMPLETE"
# Expected: Entry with "✓ COMPLETE" status from today

# 3. Run validator
$ python -m wai.closeout_validator --check
# Expected: All three checks show "✓ PASS"
```

**DO NOT declare "complete" without passing ALL THREE.**

**See:** CLOSEOUT-CHECKLIST-TEMPLATE.md for detailed steps.

---

## Quick Start

1. Read `OBSERVATION-SYSTEM-COMPLETE.md` (current work)
2. Read `WAI-Spoke/WAI-Guide.md`
3. Read `WAI-Spoke/WAI-State.json`
4. Read `WAI-Spoke/WAI-State.md`

If any of those files are missing, ask the user to initialize Wheelwright for this project.

---

## New Modules (Phase 1-5 Complete)

### wai/observation.py
- `ObservationLogger` - log every action with plan → execute → verify → result
- JSONL format, idempotency support, session tracking
- File: `WAI-Spoke/observations.jsonl`

### wai/config.py
- `SSHGitConfig` - load SSH/git settings from lug (not hardcoded)
- Per-wheel customization, verification helpers
- File: `WAI-Spoke/lugs/sshconfig-{timestamp}.lug.json`

### wai/utils/git.py
- `GitOperations` - execute git with automatic observation logging
- add_all(), commit(), push() with verification
- Remediation suggestions on failure

### wai/closeout.py
- `CloseoutWorkflow` - 4-phase enhanced closeout
- Phase 1: Reconciliation, Phase 2: State updates, Phase 3: Git ops, Phase 4: Verification
- Mandatory git operations, fail signals on error

### wai/briefing.py
- `SessionBriefing` - generate markdown briefing with observation playback
- Failed observations highlighted, remediation suggestions
- For AI context at session start

---

## Next Work (Priority Order)

1. **Phase 6 - Skill Integration** (2 hours)
   - [ ] Update wai-init, wai-sync, wai-teach, wai-learn
   - [ ] All workflow skills log observations
   - [ ] All skills load SSH config

2. **Phase 7 - Briefing Integration** (1 hour)
   - [ ] Hook `briefing.build_session_briefing()` into Claude context
   - [ ] Update AGENTS.md "Session Focus" with briefing output
   - [ ] Show failed observations needing remediation

3. **Phase 8 - Testing** (1.5 hours)
   - [ ] Unit tests: observation.py, config.py (15 tests)
   - [ ] Integration test: full closeout with observations
   - [ ] Multi-agent test: idempotency + parallel work

4. **Then - CLI Rebuild** (from NEXT-SESSION-START-HERE.txt)
   - Menu layout improvements
   - Better prompts and output formatting
   - Theme system and animations
