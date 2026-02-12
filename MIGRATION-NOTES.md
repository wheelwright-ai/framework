# WAI v2 Migration Notes (Living Document)

## Purpose
Capture execution details, decisions, edge cases, and patterns discovered during WAI v2 migration. This document serves as:
- Cross-session continuity (context restoration if sessions reset)
- Primary source material for Phase 9 documentation
- Migration guide template (becomes `guides/migrating-to-v2.md`)

## Migration Overview

**Start Date:** 2026-02-12
**Agent:** Claude Opus 4.5
**Branch:** wai-v2-migration
**Restore Point:** v1.0-pre-migration tag at commit 497c6db

---

## Phase 0: Safety Checkpoint

**Executed:** 2026-02-12T07:14:34Z
**Commit:** f21b8fb
**Status:** ✅ Complete

### What Was Done
- Verified git state (working tree clean, 1 unpushed commit)
- Pushed pre-migration state to origin/main
- Created tag `v1.0-pre-migration` at commit 497c6db
- Pushed tag to origin
- Created branch `wai-v2-migration`
- Created `WAI-MIGRATION.yaml` at repo root
- Committed with phase completion recorded in migration state

### Key Decisions
- **Tag-first approach:** Tag before branching ensures unbreakable restore point even if branch work goes wrong
- **Migration state in YAML:** Single source of truth for "where are we?" - any agent can resume by reading this file
- **Commit hash in YAML:** Record commit hash after each phase for audit trail and verification

### Edge Cases
- None encountered - clean execution

### Patterns Observed
- Git amend workflow: Initial commit → update YAML with commit hash → amend commit
- This creates slight mismatch (YAML shows intermediate hash) but acceptable for phase tracking

### Documentation Seeds
- **For quickstart guide:** "Tag your current state first - this is your undo button"
- **For migration guide:** "Migration branch keeps main clean. Tag ensures you can always revert."
- **For WAI-MIGRATION.yaml spec:** "completed_phases array records commit hash for each phase completion"

### Verification Checklist Used
- [x] Tag v1.0-pre-migration exists and is pushed
- [x] On wai-v2-migration branch
- [x] WAI-MIGRATION.yaml exists at repo root
- [x] All existing data is committed

---

## Phase 2: Registry Structure + Manifests

**Status:** ✅ Complete
**Started:** 2026-02-12T07:30Z
**Completed:** 2026-02-12T07:35Z
**Commit:** 7a2e23d

### What Was Done
1. Created registry structure: `registry/wheelwright/framework/`
2. Created PROJECT.md for wheelwright project with identity and vision
3. Copied all files from `./WAI-Spoke/` to `registry/wheelwright/framework/` (additive, original preserved)
4. Created WAI-Manifest.yaml for hub node (in /hub/ directory)
5. Created WAI-Manifest.yaml for framework spoke (in registry location)
6. Created hub/registry.yaml as node index

### Key Decisions
- **Single project structure:** Only one active project (Wheelwright) with one extension (framework)
- **Hub location:** Hub lives outside framework repo at `/home/mario/projects/wheelwright-ai/hub/`
- **Hub files not in git:** Hub manifest and registry created but not committed to framework repo (separate node)
- **Registry paths:** `registry/{project}/{extension}/` pattern established
- **PROJECT.md source:** Derived from README.md rather than WAI-Guide.md (which doesn't exist in main spoke)
- **Additive copy:** Original WAI-Spoke/ directory preserved, registry is a copy

### Edge Cases Encountered
1. **No WAI-Guide.md:** Main spoke lacks WAI-Guide.md, used README.md for PROJECT.md content instead
2. **TestSpoke is test data:** ./TestSpoke/WAI-Spoke/ only contains seed directory, not a real spoke - skipped
3. **Hub outside repo:** Hub files created successfully but not part of framework git tracking
4. **Templates/examples:** Multiple template/example WAI-Spoke dirs exist - correctly ignored, not migrated

### Patterns Observed
- **79 files copied:** Complete spoke structure including reference/, seed/, lugs/, observations
- **Manifest structure identical:** Hub and spoke manifests have same schema, differentiated by node_type and node_path
- **Template versions:** All nodes report lugs:2, brief:1, guide:1 (v2 schema established)
- **Cursor tracking ready:** hub_lug_cursor field present for cross-node signal flow (Phase 6)

### Documentation Seeds
- **For registry structure docs:** "Registry uses {project}/{extension} paths, PROJECT.md at project level captures shared identity"
- **For manifest docs:** "WAI-Manifest.yaml tracks node identity, framework version, template versions, and cursor state"
- **For hub/spoke relationship:** "Hub lives independently with its own manifest, spokes reference hub via hub_path in State"
- **For migration:** "Copy before delete - registry is duplicated data until Phase 7 cleanup verifies completeness"

### Verification Checklist
- [x] Registry directory structure exists: registry/wheelwright/framework/
- [x] PROJECT.md created with project identity
- [x] All spoke files copied to registry (79 files)
- [x] Hub manifest created: /hub/WAI-Manifest.yaml
- [x] Framework manifest created: registry/wheelwright/framework/WAI-Manifest.yaml
- [x] Hub registry index created: /hub/registry.yaml with 1 node listed
- [x] Original WAI-Spoke/ still exists (not moved, copied)

---

## Phase 1: Lug Schema Migration

**Status:** ✅ Complete
**Started:** 2026-02-12T07:20Z
**Completed:** 2026-02-12T07:25Z
**Commit:** 73112e9

### Pre-Flight Checks
- [x] Backup all WAI-Lugs.jsonl files (.v1-backup copies) - 5 backups created
- [x] Inventory: 368 v1 Lugs, 134 signals to absorb
- [x] Schema validation: v1 used i/ty/s/status fields

### Execution Log
1. Created migrate_lugs_v2.py script with comprehensive v1→v2 mapping
2. Ran dry-run to identify edge cases (invalid JSON, empty arrays)
3. Executed migration: 368 v1 Lugs → 350 v2 Lugs
4. Created absorb_signals.py to convert signals to Lugs
5. Absorbed 134 signals → 10 high-impact Lugs (impact ≥ 8)
6. Added tombstone headers to WAI-Signals.jsonl files
7. Fixed template file with proper v2 example
8. Verified: All required fields present, PEV fields added, data preserved

### Decisions Made
- **Status mapping:** open/ready/active → published, in-progress → in_progress, closed/complete/completed → resolved
- **Default values:** impact: 3, created_by: "conductor", node: derived from path
- **Signal absorption:** Each signal offer becomes a Lug with impact ≥ 8
- **Edge case handling:** Skip invalid JSON lines (shell variables, trailing text), preserve valid data
- **Lost data acceptable:** 18 lines lost (3 invalid JSON, 1 string, 1 empty array, 13 trailing text) - all corrupted/invalid entries

### Edge Cases Encountered
1. **Shell variables in JSON:** Lines 44-47 in main file contained `$(date ...)` - uneval'd shell vars, skipped correctly
2. **Trailing text in reference file:** Lines 263-287 had non-JSON test output, skipped correctly
3. **Empty template:** Template file was `[]`, replaced with proper v2 example
4. **Minified reference schema:** reference/auto file used different minified schema (ca/ua/cla vs created_at) - handled by migration logic
5. **Signal structure:** Signals have offers array, each offer becomes separate Lug

### Patterns Observed
- **Multi-schema handling:** Script successfully handled 3 different v1 schema variants
- **Graceful degradation:** Invalid entries skipped without stopping migration
- **Additive migration:** All new fields added, originals preserved with _v1_* prefix
- **Verification built-in:** Line count comparison confirms no unexpected data loss

### Documentation Seeds
- **For Lug schema docs:** "v2 adds impact, created_by, node, PEV fields (perceive/execute/verify), and calibration fields (resolution/resolution_reason)"
- **For migration guide:** "Migration script handles multiple v1 schemas, skips invalid JSON gracefully, preserves originals in _v1_* fields"
- **For signal absorption:** "Signals with impact ≥ 8 become Lugs, marked with _absorbed_from_signal metadata"
- **For PEV pattern:** "PEV fields added as null - available for future use when Lugs track perceive/execute/verify steps"

### Verification Checklist
- [x] Every Lug has: id, type, title, status, impact, created_by, node, created_at
- [x] PEV fields present (null is fine - schema is ready)
- [x] No data lost (350 v2 ≥ 341 valid v1 + 10 absorbed signals, 18 invalid entries correctly discarded)
- [x] _v1_status preserves original values
- [x] v1-backup files exist for all migrated files (5 backups)
- [x] WAI-Signals.jsonl files have tombstone headers
- [x] git diff shows only additions to existing Lug content (additive migration)

---

## Cross-Session Restoration Protocol

If context resets mid-migration, new agent should:

1. **Read WAI-MIGRATION.yaml** - Identify current_phase and last completed phase
2. **Read this file (MIGRATION-NOTES.md)** - Get narrative of what happened
3. **Read Hub WAI-Lugs.jsonl** - Filter for type: "observation" with "Phase X" in title for detailed learnings
4. **Verify git state:**
   ```bash
   git status  # Should be on wai-v2-migration branch
   git log --oneline -5  # Verify commits match migration state
   ```
5. **Review verification checklist** for last completed phase
6. **Proceed with current_phase** from migration state

---

## Token Usage Tracking

- Phase 0: ~15K tokens (setup + notes creation)
- Phase 1: [To be measured]
- Phase 2: [To be measured]
- ...

This helps estimate session boundaries.

---

## Notes for Phase 9 (Documentation Writing)

This section accumulates cross-cutting observations that don't fit in phase-specific notes:

### Overall Patterns
- [To be filled as patterns emerge]

### What Worked Well
- [To be filled throughout migration]

### What Was Harder Than Expected
- [To be filled throughout migration]

### Architectural Insights
- [To be filled throughout migration]

### Agent Recommendations
- [To be filled - what should future agents know?]

