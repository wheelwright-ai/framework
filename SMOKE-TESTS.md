# Wheelwright Framework - Smoke Tests

This document describes the smoke test suites for verifying framework integrity and spoke WAI files.

## Quick Start

```bash
# Run framework smoke tests (52 tests)
./smoke-tests-framework.sh

# Run spoke WAI files smoke tests (49 tests)
./smoke-tests-spoke.sh

# Run both
./smoke-tests-framework.sh && ./smoke-tests-spoke.sh
```

## Framework Smoke Tests (52 tests)

**Purpose:** Verify core framework functionality after changes

**Coverage:**
- Section 1: Naming Migration (WWAI → WAI) - 9 tests
- Section 2: No WWAI References - 4 tests
- Section 3: Correct Spelling - 3 tests
- Section 4: WAI File Validity - 2 tests
- Section 5: Session Start Hook - 5 tests
- Section 6: Claude Code Hook Configuration - 3 tests
- Section 7: Unit Tests - 3 tests
- Section 8: Conversation Logging Feature - 5 tests
- Section 9: Hub Learning Dependency - 2 tests
- Section 10: WAI Branding - 4 tests
- Section 11: Token Efficiency Protocols - 12 tests

**What it verifies:**
- ✓ WAI CLI tool exists and is executable
- ✓ .WAI/ directory exists (capitalized)
- ✓ Old .wwai/ and wwai references removed
- ✓ No "WWAI" or "Wheel Wright" in documentation
- ✓ JSON/JSONL files are valid
- ✓ Session-start hook properly configured
- ✓ Unit tests pass
- ✓ Conversation logging documented
- ✓ Hub learning dependency mentioned
- ✓ Token efficiency protocols in WAI-Guide.md and CLAUDE.md
- ✓ Platform templates exist (Cursor, VS Code, Generic)

**Expected output:**
```
=========================================
SMOKE TEST RESULTS
=========================================
Total tests: 52
Passed: 52
Failed: 0

✓ ALL SMOKE TESTS PASSED!
```

## Spoke WAI Files Smoke Tests (49 tests)

**Purpose:** Verify this spoke's WAI files are correctly configured

**Coverage:**
- Section 1: WAI-State.json Structure - 7 tests
- Section 2: Project Foundation - 6 tests
- Section 3: Session State Schema - 6 tests
- Section 4: Decisions Log - 5 tests
- Section 5: Evolution Log - 2 tests
- Section 6: Wheel Signals - 4 tests
- Section 7: WAI Naming Consistency - 4 tests
- Section 8: High-Impact Decisions - 1 test
- Section 9: Current Session State - 2 tests
- Section 10: Token Efficiency Schema - 10 tests

**What it verifies:**
- ✓ WAI-State.json is valid and has all required sections
- ✓ Project foundation is complete with YOLO mode enabled
- ✓ Session state has current_session and last_closeout fields
- ✓ Decisions array has conversation logging, shipit, naming, and unit test entries
- ✓ Evolution log has conversation logging entry
- ✓ wheel-signals.jsonl has high-impact learnings
- ✓ No WWAI references outside historical context
- ✓ At least 5 high-impact decisions recorded (found 15)
- ✓ Token efficiency schema fields exist (complexity_thresholds, capacity_management)
- ✓ ADAPTIVE workflow mode configured

**Expected output:**
```
=========================================
SPOKE SMOKE TEST RESULTS
=========================================
Total tests: 49
Passed: 49
Failed: 0

✓ ALL SPOKE SMOKE TESTS PASSED!
```

## Test Details

### Framework Tests

#### Naming Migration
Ensures WWAI → WAI rename was complete:
- WAI CLI tool exists and is executable
- .WAI/ directory exists (capitalized)
- All WAI state files exist
- Old .wwai/ directory removed
- Old wwai tool removed

#### Content Verification
Checks that documentation is clean:
- No "WWAI" references in CLAUDE.md, README.md, WAI-Guide.md, WAI-State.md
- No "Wheel Wright" (two words) anywhere
- "Wheelwright" (one word) used consistently

#### Conversation Logging
Verifies the new feature is documented:
- CLAUDE.md has "Conversation Logging" section
- CLAUDE.md has closeout and shipit commands
- WAI-Guide.md mirrors the instructions
- .gitignore excludes session-conversation.jsonl
- Hub learning dependency mentioned

### Spoke Tests

#### Schema Validation
Ensures WAI-State.json has correct structure:
- All top-level sections exist (wheelwright, _project_foundation, _session_state, etc.)
- Foundation is complete with identity, boundaries, approach, philosophy
- Session state has current_session and last_closeout fields

#### Decision Tracking
Verifies learnings were recorded:
- Conversation logging decision (impact: 10)
- Shipit command decision (impact: 9)
- WWAI → WAI naming decision (impact: 9)
- Unit test suite decision (impact: 8)

#### Signal Quality
Checks wheel-signals.jsonl has high-impact learnings:
- Valid JSONL format
- Conversation logging signal
- Naming standardization signal
- Unit test pattern signal

## When to Run

**Run smoke tests:**
- After implementing new features
- Before committing major changes
- After renaming or restructuring
- Before creating a PR
- As part of CI/CD pipeline

**Quick health check:**
```bash
# Both test suites should complete in < 10 seconds
time (./smoke-tests-framework.sh && ./smoke-tests-spoke.sh)
```

## Troubleshooting

### CRLF Line Ending Issues
If tests fail with "cannot execute: required file not found":
```bash
sed -i 's/\r$//' smoke-tests-framework.sh smoke-tests-spoke.sh
```

### jq Not Found
Tests require `jq` for JSON processing:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### Permission Denied
Make scripts executable:
```bash
chmod +x smoke-tests-framework.sh smoke-tests-spoke.sh
```

## Adding New Tests

### Framework Test Template
```bash
test_condition "Description" "command to run" "success|failure"
test_file_exists "Description" "/path/to/file"
test_json_valid "Description" "/path/to/file.json"
test_content_contains "Description" "/path/to/file" "pattern"
```

### Spoke Test Template
```bash
test_jq_query "Description" "file.json" ".path.to.field" "expected_value"
test_jq_exists "Description" "file.json" ".path.to.field"
test_jq_array_not_empty "Description" "file.json" ".array.path"
```

---

**Wheelwright Framework** - wheelwright.ai - MIT License
