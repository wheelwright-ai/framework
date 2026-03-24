# WAI Shipit

**Production Readiness Verification Protocol**

Verify this version is ready to ship to users.

---

## Execution Context

- **Nodes:** spoke, hub, framework
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Paths Required:** spoke_path; framework_path + hub_path (for auto-teach)
- **Lug Storage:** `ty: "shipit"` records in WAI-Lugs.jsonl

---

## When to Use

- Before releasing to users/production
- Before publishing a package
- Before merging to main branch
- After completing a feature set
- When user explicitly requests quality verification

## Prerequisites

- Code changes complete (not mid-implementation)
- Tests exist for the codebase
- WAI-Spoke/ directory exists
- Git repository initialized

## Follow-ons

- Push to remote (always — closeout handles this automatically)
- `/wai (Step 9b: auto-teach on closeout)` — Distribute to spokes (if framework)
- Deploy to production (if applicable)
- Announce release (if public)

## Use Cases

**Use Case 1: Feature Complete**
- Situation: New feature implemented, ready for users
- Action: Run shipit to verify quality before release
- Result: All gates pass, safe to deploy

**Use Case 2: Before PR Merge**
- Situation: PR ready, need to verify quality
- Action: Run shipit to catch issues before merge
- Result: Clean code, tests pass, ready for review

**Use Case 3: Periodic Health Check**
- Situation: Want to verify codebase is in good shape
- Action: Run shipit as quality audit
- Result: Identify tech debt, sprawl, security issues

**Use Case 4: After AI-Heavy Session**
- Situation: Lots of AI-generated code, worried about sprawl
- Action: Run shipit for file hygiene + quality gates
- Result: Cleaned up files, validated implementations

---

## Purpose

Confirm the current state meets quality standards before release:
- Clean, organized codebase
- All tests pass
- Dependencies secure
- Documentation current
- No breaking changes (or documented)

**Critical:** If issues arise at any step, **call them out immediately**. Do not proceed blindly.

---

## Shipit Procedure

### 0. Production Release Intent

**First: clarify what this shipit is for.**

> Is this a production release? (y/n)

- **Yes (release):** All steps run. After closeout, a git tag `v{version}` is applied and pushed. This marks the commit as stable — anyone cloning or targeting tags gets a known-good state.
- **No (progress save):** All steps run identically. No tag is applied. Commit is pushed but not marked as a release.

Record the answer. It determines whether Step 9b runs.

---

### 1. Sync `.claude/commands/` (FRAMEWORK ONLY)

**If running from the framework repo: keep IDE skills in sync with canonical templates.**

```bash
# Keep Claude Code slash commands in sync (flat — Claude Code requirement)
yes | cp templates/commands/wai*.md .claude/commands/

# Sync canonical source → template spoke skill subdirs
for skill_dir in templates/spoke/skills/*/; do
  id=$(basename "$skill_dir")
  # Find the command file in this skill dir
  for f in "$skill_dir"*.md; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    src="templates/commands/$fname"
    [ -f "$src" ] && \cp "$src" "$f" 2>/dev/null || true
  done
done
```

This prevents the three-copy problem: `templates/commands/` is canonical (authoring source); `.claude/commands/` is flat (Claude Code requirement); `templates/spoke/skills/{id}/` is the spoke install template (subdir-per-skill structure). All must match on canonical content.

**Skip this step** if not running from the framework repo (spokes have no `.claude/commands/`).

---

### 2. File Hygiene & Maintenance

**AI tends to create sprawl. Clean it up before validation.**

**Scan for orphaned/temp files:**
```bash
# Find common AI sprawl patterns
find . -name "temp_*.py" -o -name "test_*.py.bak" -o -name "*.tmp"
find . -name "debug_*" -o -name "scratch_*" -o -name "old_*"
find . -name "*.orig" -o -name "*_backup*" -o -name "copy_of_*"
```

**Relocate or delete:**

| File Type | Action |
|-----------|--------|
| Temp/debug files | Delete |
| Useful reference | Move to `WAI-Spoke/reference/` |
| Teaching material | Move to `WAI-Spoke/seed/ingest/` |
| Outdated duplicates | Delete |
| Unknown purpose | Ask user |

**Check for:**
- Files in wrong directories
- Duplicate implementations
- Abandoned experiments
- Uncommitted large files

**Report findings before proceeding:**
```
File Hygiene Report:
- [N] temp files deleted
- [N] files relocated to reference/
- [N] files need user decision
- Issues: [list any concerns]
```

**If issues found:** Stop and resolve before continuing.

---

### 3. Breaking Change Detection (P3)

**Identify changes that could break existing users.**

**Check for:**
- API signature changes
- Removed public functions/classes
- Changed configuration formats
- Database schema changes
- CLI argument changes
- File format changes

**For each breaking change:**
- Document in CHANGELOG.md
- Add migration guidance
- Consider deprecation warnings
- Update version appropriately (major bump if significant)

**Report:**
```
Breaking Changes Detected:
- [change 1]: [migration path]
- [change 2]: [migration path]
- None detected ✓
```

**If breaking changes found:** Confirm user acknowledges before proceeding.

---

### 4. Dependency Audit (P4)

**Verify dependencies are secure and current.**

```bash
# Python
pip-audit  # or safety check
pip list --outdated

# Node
npm audit
npm outdated

# General
# Check for known vulnerabilities in dependencies
```

**Check for:**
- Known security vulnerabilities
- Severely outdated packages
- Deprecated dependencies
- License compatibility issues

**Report:**
```
Dependency Audit:
- Security vulnerabilities: [count] ([severity])
- Outdated packages: [count]
- Action required: [yes/no]
```

**If critical vulnerabilities found:** Stop and address before proceeding.

---

### 5. Quality Gates (P3, P4) — MANDATORY ENFORCEMENT

**🔒 All quality checks must pass. Failure aborts shipit.**

#### 5a. Test Execution (REQUIRED)

Detect and run the test suite:

```bash
# Auto-detect test command
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    pytest -v
elif [ -f "package.json" ]; then
    npm test
elif [ -f "Makefile" ]; then
    make test
else
    echo "⚠️ No test suite detected - SKIP (warn user)"
fi
```

**Exit codes:**
- `0` = All tests passed → CONTINUE
- `non-zero` = Tests failed → **ABORT SHIPIT**

**On failure:**
```
❌ QUALITY GATE FAILED: Tests
   [X] tests failed out of [Y] total
   
   First 5 failures:
   [failure details]
   
   ⛔ SHIPIT ABORTED
   Fix failing tests and run shipit again.
```

#### 5b. Linting (REQUIRED if linter exists)

Detect and run linter:

```bash
# Auto-detect linter
if command -v ruff &> /dev/null; then
    ruff check .
elif command -v flake8 &> /dev/null; then
    flake8 .
elif command -v pylint &> /dev/null; then
    pylint $(find . -name "*.py")
elif command -v eslint &> /dev/null; then
    eslint .
else
    echo "⚠️ No linter detected - SKIP (warn user)"
fi
```

**Exit codes:**
- `0` = Clean → CONTINUE
- `non-zero` = Linting errors → **ABORT SHIPIT**

**On failure:**
```
❌ QUALITY GATE FAILED: Linting
   [N] linting errors found
   
   Fix linting errors and run shipit again.
    Override: Set SHIPIT_SKIP_LINT=1 to bypass (NOT RECOMMENDED)
```

#### 5c. Idempotency Testing (REQUIRED for Wheelwright projects)

**Purpose:** Verify closeout operations are replay-safe and concurrent-safe.

Detect and run idempotency test suite:

```bash
# Check if idempotency tests exist
if [ -d "tests/idempotency" ] && [ -f "tests/idempotency/test_runner.py" ]; then
    echo "🔄 Running idempotency tests..."
    python tests/idempotency/test_runner.py --category=all --timeout=300
    IDEMPOTENCY_EXIT_CODE=$?
else
    echo "ℹ️  No idempotency tests found - SKIP (Wheelwright projects should have these)"
    IDEMPOTENCY_EXIT_CODE=0
fi
```

**Exit codes:**
- `0` = All idempotency tests passed → CONTINUE
- `non-zero` = Idempotency tests failed → **ABORT SHIPIT**

**Test Categories Verified:**
- **Closeout Replay (7 tests):** Second closeout detects completion and skips operations
- **Concurrent Closeout (8 tests):** File locking prevents corruption during concurrent operations
- **Signal Deduplication (9 tests):** Duplicate signal publication prevention
- **Migration Resume (10 tests):** Checkpoint-based resume from interruption

**On failure:**
```
❌ QUALITY GATE FAILED: Idempotency
   [X] of 34 idempotency tests failed
   
   Failed categories:
   - Closeout Replay: [details]
   - Concurrent Safety: [details]
   
   ⛔ SHIPIT ABORTED
   Idempotency failure indicates closeout operations are not replay-safe.
   This must be fixed before shipping to prevent data corruption.
```

**Override (NOT RECOMMENDED):**
```bash
# Emergency override (logs warning to session)
export SHIPIT_SKIP_IDEMPOTENCY=1
```

#### 5d. Type Checking (OPTIONAL)

If type checker is configured, run it:

```bash
if [ -f "mypy.ini" ] || grep -q "mypy" pyproject.toml 2>/dev/null; then
    mypy .
    # Type errors are WARNINGS only (don't abort)
fi
```

**Type errors are non-blocking** but should be reported.

#### Quality Gate Summary Report

After all gates:

```
✅ QUALITY GATES PASSED
   Tests:        ✓ [X] passed / [Y] total
   Linting:      ✓ Clean
   Idempotency:  ✓ 34/34 tests passed (replay-safe verified)
   Type Check:   ⚠️ [N] warnings (non-blocking)
   
   → Safe to proceed with shipit
```

**Override Mechanism:**

To bypass failing gates (emergency use only):
```bash
export SHIPIT_SKIP_TESTS=1      # Skip test execution
export SHIPIT_SKIP_LINT=1       # Skip linting
export SHIPIT_FORCE=1           # Skip ALL quality gates
```

**⚠️ WARNING:** Overrides should be logged to WAI-Lugs.jsonl as a signal lug (impact >= 8) for technical debt tracking.

---

### 6. Benchmark Execution (P5) — REGRESSION DETECTION

**Run performance benchmarks if available. Regressions require user acknowledgment.**

#### Benchmark Detection and Execution

**Wheelwright framework benchmark (preferred):**

```bash
# Run Wheelwright WEI benchmark if runner exists
if [ -f "benchmarks/runner/benchmark_runner.py" ]; then
    echo "Running Wheelwright WEI benchmark (small + medium tiers)..."
    python3 benchmarks/runner/benchmark_runner.py small --persist
    python3 benchmarks/runner/benchmark_runner.py medium --persist
    # Note: large tier generates 400MB reference files — skip in shipit unless explicitly requested
    echo "WEI scores appended to benchmarks/benchmark-results.jsonl"
else
    # Fallback: detect other benchmark runners
    if [ -f "benchmark.py" ]; then
        python3 benchmark.py --profile=all
    elif [ -f "package.json" ] && grep -q "benchmark" package.json; then
        npm run benchmark
    else
        echo "No benchmarks detected - SKIP"
    fi
fi
```

#### Regression Analysis

Compare latest WEI score against prior run:

```bash
# If benchmark-results.jsonl exists, compare last two entries
if [ -f "benchmarks/benchmark-results.jsonl" ]; then
    python3 -c "
import json
lines = [l for l in open('benchmarks/benchmark-results.jsonl') if l.strip()]
if len(lines) >= 2:
    prev = json.loads(lines[-2])
    curr = json.loads(lines[-1])
    delta = curr['wei'] - prev['wei']
    flag = 'REGRESSION' if delta < -2 else 'OK'
    print(f'WEI: {prev[\"wei\"]:.1f} -> {curr[\"wei\"]:.1f} ({delta:+.1f}) [{flag}]')
else:
    print('First run — no baseline to compare')
"
fi
```

**Report:**
```
📊 BENCHMARKS
   Executed: [N] benchmarks
   
   Performance vs Baseline:
   ✓ Token efficiency:    2000x (no change)
   ⚠️ Context loading:    -15% (REGRESSION)
   ✓ Resumption speed:    600x (+5% improvement)
   
   Regressions detected: 1
```

**On Regression:**

```
⚠️ PERFORMANCE REGRESSION DETECTED
   Context loading: 1.2s → 1.4s (-15%)
   
   Options:
   [1] Abort shipit - fix regression first
   [2] Continue with acknowledgment (log as technical debt)
   [3] Update baseline (accept new performance level)
   
   Choice: _
```

- **Option 1:** Abort shipit, user fixes regression
- **Option 2:** Continue but log regression to WAI-Lugs.jsonl as a signal lug (impact: 7+)
- **Option 3:** Update baseline if regression is intentional tradeoff

**Benchmark Results Storage:**

```bash
# Append results with timestamp
echo "{\"timestamp\": \"$(date -Iseconds)\", \"results\": {...}}" >> benchmarks/history.jsonl

# Update baseline if user chose option 3
cp benchmarks/latest.json benchmarks/baseline.json
```

**Override:**
```bash
export SHIPIT_SKIP_BENCHMARKS=1  # Skip benchmark execution entirely
```

---

### 7. Documentation Updates (P7, P8)

**Document what's known and can be captured.**

**Review and update:**
- `README.md` - Current with new features/changes?
- `CHANGELOG.md` - Version changes documented?
- `llms-full.txt` (or master prompt) - Capabilities current?
- API documentation - Endpoints/functions documented?
- Configuration docs - New options documented?

**For each file:**
- Check if session changes require updates
- Make updates where applicable
- Note what was updated

**Report:**
```
Documentation:
- README.md: [updated/no changes needed]
- CHANGELOG.md: [updated/no changes needed]
- [other docs]: [status]
```

---

### 8. Pre-Ship Summary

**Before executing closeout, present full report:**

```markdown
## Shipit Pre-Flight Check

### File Hygiene
[summary]

### Breaking Changes
[summary]

### Dependencies
[summary]

### Quality Gates
- Tests: ✓/✗
- Coverage: ✓/✗
- Linting: ✓/✗

### Benchmarks
[summary]

### Documentation
[summary]

## Ready to Ship: [YES/NO]

[If NO: list blockers]
[If YES: proceed to closeout?]
```

**Get user confirmation before closeout.**

---

### 9. Execute Closeout

**Only after all checks pass:**

Run full `/wai-closeout` protocol:
1. Lug reconciliation
2. Signal extraction
3. Incomplete work capture
4. Version increment
5. State update
6. Session log clear
7. Documentation finalization
8. Summary generation
9. Git commit + push (mandatory)
10. Verification

---

### 9b. Apply Release Tag (Production Release Only)

**Skip this step if production release = no.**

After the closeout commit is confirmed, read the version from `WAI-State.json` → `wheel.version` (updated by closeout):

```bash
git tag v{version}
git push origin v{version}
```

**Report:**
```
Release Tag:
- Tag: v{version}
- Pushed: ✓
```

**If tag already exists:** Stop. Report the conflict — do not force-overwrite an existing tag. Resolve manually.

---

### 10. Teach All Spokes (Auto)

**After successful closeout, updates are distributed automatically.**

This step runs automatically when:
- Running from framework or hub node
- Closeout completed successfully (Step 9b generates teaching files)

**Teach Procedure:**
```
1. `wai-closeout` Step 9b generates `.teaching` files
2. Files are published to the canonical hub layout (`teachings_repo/`)
3. Spokes auto-discover and pull these updates on their next wakeup
4. No separate manual distribution or `upgrade-adoption-plan.json` generation is required.
```

**Report:**
```
Teach Distribution:
- Hub teachings generated: ✓
- Available for spokes to pull: ✓
```

**If teach fails for a spoke:** Log warning, continue with others. Report failures at end.

---

## Failure Handling

**Do not proceed blindly. At each step:**

| Issue Severity | Action |
|----------------|--------|
| Critical (security, test failures) | **Stop immediately.** Report and fix. |
| Warning (outdated deps, low coverage) | Report, get user acknowledgment |
| Info (minor cleanup) | Note and continue |

**Always report what was found, even if proceeding.**

---

## Success Criteria

- [ ] File hygiene complete (no sprawl)
- [ ] Breaking changes documented with migration paths
- [ ] Dependencies audited (no critical vulnerabilities)
- [ ] All tests pass
- [ ] Coverage meets threshold
- [ ] Linting clean
- [ ] Benchmarks run (no regressions)
- [ ] Documentation updated
- [ ] User confirmed ready to ship
- [ ] Closeout executed successfully
- [ ] Release tag applied and pushed: `v{version}` (production release only — skip if progress save)
- [ ] All spokes taught (if framework/hub)

---

## Output Format

```
## Shipit Complete

### Pre-Flight
- File hygiene: ✓ [N files cleaned]
- Breaking changes: ✓ [none / documented]
- Dependencies: ✓ [secure]
- Tests: ✓ [X/X passing]
- Coverage: ✓ [X%]
- Linting: ✓ [clean]
- Benchmarks: ✓ [no regressions]
- Documentation: ✓ [updated]

### Closeout
- Session #[N] saved
- Version: [X.Y.Z]
- Commit: [hash]
- Push: [status]
- Release tag: v[X.Y.Z] pushed ✓  *(or "n/a — progress save")*

### Teach (auto)
- Hub teachings generated: ✓
- Available for spokes to pull: ✓

## Status: SHIPPED ✓
```

---

## Related Commands

- `/wai-closeout` - Just save state (no quality gates)
- `/wai-status` - Framework health check
- `/wai-time` - Check context usage

---

*Shipit = Verify quality, then save. Ready for users.*
