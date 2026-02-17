# WAI Shipit

**Production Readiness Verification Protocol**

Verify this version is ready to ship to users.

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

### 1. File Hygiene & Maintenance (FIRST)

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

### 2. Breaking Change Detection (P3)

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

### 3. Dependency Audit (P4)

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

### 4. Quality Gates (P3, P4)

**All quality checks must pass.**

#### 4a. Test Execution
```bash
pytest -v  # or project test command
```
- **100% of tests must pass**
- Report any failures with details

#### 4b. Coverage Check
```bash
pytest --cov=. --cov-report=term-missing
```
- Check against coverage threshold (if defined)
- Report uncovered critical paths

#### 4c. Linting & Type Checking
```bash
ruff check .  # or flake8, pylint
mypy .        # if using type hints
```
- Must be clean (no errors)
- Warnings acceptable but report them

**Report:**
```
Quality Gates:
- Tests: [passed/failed] ([X]/[Y] tests)
- Coverage: [X]% (threshold: [Y]%)
- Linting: [clean/N issues]
- Type checking: [clean/N issues]
```

**If any gate fails:** Stop. Fix issues before proceeding.

---

### 5. Benchmark Execution (P5)

**Run performance benchmarks (if available).**

```bash
# Run project benchmarks
pytest benchmarks/ -v  # or custom benchmark command
```

**Record results:**
- Append to `benchmarks/results.md` (or project equivalent)
- Compare against previous run
- Flag significant regressions

**Report:**
```
Benchmarks:
- Executed: [N] benchmarks
- Regressions: [none / list]
- Results logged to: [path]
```

**If significant regression:** Alert user, get acknowledgment before proceeding.

---

### 6. Documentation Updates (P7, P8)

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

### 7. Pre-Ship Summary

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

### 8. Execute Closeout

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
9. Git commit
10. Verification

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

## Status: SHIPPED ✓
```

---

## Related Commands

- `/wai-closeout` - Just save state (no quality gates)
- `/wai-status` - Framework health check
- `/wai-time` - Check context usage

---

*Shipit = Verify quality, then save. Ready for users.*
