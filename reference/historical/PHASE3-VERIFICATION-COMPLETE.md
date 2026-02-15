# Phase 3: Spoke-Side Verification - COMPLETE

**Date:** 2026-02-01  
**Status:** ✅ Complete and Tested  
**Tests:** 18/18 passing

---

## What Was Implemented

### 1. **Verify-Upgrade Command** (`wai/commands/verify_upgrade.py`)
Core verification system for spoke-side upgrade plan validation:
- ✅ Load upgrade-adoption-plan.json from spoke root
- ✅ Verify hub signature using HMAC-SHA256
- ✅ Verify file hashes for integrity
- ✅ Show adoption guidance with context (why_changed, mentions)
- ✅ Generate adoption decisions (adopt/review/defer)
- ✅ Execute file adoptions with merge strategy support
- ✅ Display detailed adoption summary and guidance to agent

### 2. **Closeout Integration** (`wai/commands/closeout.py`)
Updated closeout to handle upgrades automatically:
- ✅ Phase 1: Detect pending upgrade-adoption-plan.json
- ✅ Phase 2: Verify plan integrity and signature
- ✅ Phase 3: Generate adoption decisions
- ✅ Phase 4: Execute adoptions
- ✅ Phase 5: Standard closeout instructions
- ✅ Optional hub_key parameter for signature verification

### 3. **CLI Integration** (`wai/core.py`)
Added `verify-upgrade` command to CLI:
- ✅ `WAI verify-upgrade [path] [--hub-key KEY]`
- ✅ Argument parsing and validation
- ✅ Spoke initialization check
- ✅ Error handling and exit codes (0 on success, 1 on failure)
- ✅ Command dispatch in main CLI loop

### 4. **Test Suite** (`tests/unit/commands/test_verify_upgrade.py`)
**18 comprehensive tests covering:**
- ✅ Loading upgrade-adoption-plan.json (2 tests)
- ✅ File hash verification (3 tests)
- ✅ Hub signature verification (3 tests)
- ✅ Adoption decision generation (3 tests)
- ✅ File adoption execution (3 tests)
- ✅ Merge strategy support (1 test)
- ✅ Full verify-upgrade command flow (3 tests)

---

## Workflow

### Session Start (Wakeup)

Agent sees:
```
UPGRADE ADOPTION PLAN v3.0.0
================================================

Framework Version: 3.0.0
Created: 2026-02-01T18:12:00Z

Security:
  ✓ Signed by wheelwright-framework-3.0.0

Files:
  Spoke files: 3
    - Ready to adopt: 2
    - Need review: 1

ADOPTION GUIDANCE
────────────────────────────────────────────

Ready to Adopt Immediately:
  ✓ WAI-Guide.md
    Changed from: 2.1.0 → 3.0.0
    Why: Enhanced session start protocol
    Affects: session-start, teaching, reconciliation

Requires Review:
  ⚠ WAI-State.json
    Changed from: 2.0.1 → 3.0.0
    Why: Structure version 3.0, added teaching-adoption-plan schema
    Action: REVIEW
    Merge strategy: merge_sections
      Preserve: _session_state, _project_foundation, decisions, analytics
      Update: wheelwright.structure_version, wheelwright.version, _file_meta
```

### Verification Process

1. **Load Plan**: Read upgrade-adoption-plan.json
2. **Verify Signature**: HMAC-SHA256 comparison with hub key
3. **Verify Hashes**: SHA256 file integrity check
4. **Show Summary**: Display plan metadata and file status
5. **Show Guidance**: Detailed info on why changed, merge strategies
6. **Decision**: Auto-adopt safe files, defer review files

### Adoption Execution

Files flow from `/seed/ingest/` to final locations:
```
/seed/ingest/
  ├── WAI-Guide.md.teaching          → WAI-Spoke/WAI-Guide.md
  ├── WAI-State.json.teaching        → WAI-Spoke/WAI-State.json
  ├── WAI-State.md.teaching          → WAI-Spoke/WAI-State.md
  ├── hub-profile.json.teaching      → (hub only)
  └── ...
```

For files with merge_strategy, agent can:
- Review merge strategy before adoption
- Preserve local sections (won't be overwritten)
- Update new sections (framework improvements)
- Keep local customizations intact

---

## Architecture

### File Structure

```
wai/commands/
  ├── verify_upgrade.py         (NEW - 320+ lines)
  └── closeout.py               (UPDATED - verification integrated)

wai/core.py                      (UPDATED - CLI command added)

tests/unit/commands/
  └── test_verify_upgrade.py     (NEW - 18 tests)
```

### Key Functions

**`verify_upgrade.py`:**
- `verify_upgrade_command()` - Main entry point
- `_load_plan_file()` - Load JSON from disk
- `_verify_plan_integrity()` - Check file hashes
- `_show_adoption_summary()` - Display overview
- `_show_adoption_guidance()` - Show detailed guidance
- `get_adoption_decisions()` - Auto-decide actions
- `execute_adoptions()` - Copy/merge files

**`closeout.py`:**
- `generate_closeout()` - Now calls verify/adopt
- `_check_pending_upgrades()` - Detect plan
- Integrated full Phase 1-5 workflow

**`core.py`:**
- `_cmd_verify_upgrade()` - CLI handler
- Command dispatch and validation

---

## Security Model

### Verification Chain

```
Plan created with:
  1. Hub fingerprint (HMAC-SHA256 signature)
  2. File hashes (SHA256 of content)
  
Spoke verifies:
  1. Hub signature (HMAC with hub key)
  2. File hashes (SHA256 of ingest files)
  3. Integrity confirmed → safe to adopt
```

### Hash Verification

- Computes SHA256 of file in ingest
- Compares to hash in upgrade plan
- Detects corruption or tampering
- Prevents adoption of modified files

### Signature Verification

- Uses HMAC-SHA256 with hub key
- Protects against man-in-the-middle
- Proves plan came from trusted hub
- Uses `hmac.compare_digest()` for timing-safe comparison

---

## Merge Strategy Support

For files like WAI-State.json that need merge:

```json
{
  "merge_strategy": "merge_sections",
  "sections_to_preserve": [
    "_session_state",      // Local session data
    "_project_foundation", // Local project setup
    "decisions",           // Local decisions
    "analytics"            // Local analytics
  ],
  "sections_to_update": [
    "wheelwright.structure_version",  // Framework updates
    "wheelwright.version",
    "_file_meta"
  ]
}
```

Agent can:
1. See merge strategy and sections
2. Understand what changes are coming
3. Accept automatic merge
4. Or manually review before merging

---

## Integration Points (Next Phases)

### Phase 4: Hub Learning
- Hub learns from spoke customizations
- Learn command reads local changes
- Hub updates future teach plans

### Phase 5: Testing
- End-to-end teach → verify → adopt
- Hub ↔ spoke bidirectional learning
- Security verification full coverage

---

## Test Results

```
tests/unit/commands/test_verify_upgrade.py

18 PASSED in 0.80s

Coverage:
  ✓ Plan loading (2/2)
  ✓ Integrity verification (3/3)
  ✓ Hub signature (3/3)
  ✓ Adoption decisions (3/3)
  ✓ File execution (3/3)
  ✓ Merge strategy (1/1)
  ✓ Full command (3/3)
```

All verification tests passing. No regressions in existing tests.

---

## Ready for Next Phase

✅ Spoke-side verification complete  
✅ Tests green (18/18)  
✅ Integration tested with closeout  
✅ CLI command working  
✅ Security model verified  
✅ Ready for Phase 4 (Hub Learning)  

---

## How to Use

### Manual Verification
```bash
wai verify-upgrade [path] [--hub-key SECRET]
```

### Automatic (Closeout)
```bash
wai closeout
```
Automatically verifies and adopts pending upgrades.

### Custom Hub Key
```bash
export HUB_KEY="your-secret-key"
wai verify-upgrade . --hub-key $HUB_KEY
```

---

## Key Decisions

1. **Trust Model**: Hub key stored in spoke for verification (hub-profile.json)
2. **Adoption Strategy**: Auto-adopt safe files, defer review files for agent
3. **Merge Support**: Preserve local sections, update framework sections
4. **Error Handling**: Skip corrupted files, report to agent
5. **Integration**: Closeout automatically triggers verification and adoption

---

## Next Steps

1. **Phase 4: Hub Learning** (epic `a2f7e9c4b1d6`)
   - Implement learn command
   - Hub learns from spoke customizations
   - Update future teach plans with learnings

2. **Phase 5: Testing** (epic `v3w7x1y5z9a4`)
   - End-to-end scenarios (teach → verify → adopt)
   - Hub ↔ spoke knowledge flow
   - Security verification
   - Performance testing

3. **v3.2 Release**
   - Full documentation
   - Production hardening
   - Fingerprint rotation support

---

*Phase 3 complete: Spoke-side verification infrastructure working, tests green, ready for Hub Learning phase*
