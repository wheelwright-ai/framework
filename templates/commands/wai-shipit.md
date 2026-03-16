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
- `/wai-teach` — Distribute to spokes (if framework)
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
yes | cp templates/commands/wai*.md .claude/commands/
```

This prevents the two-copy problem: `templates/commands/` is canonical; `.claude/commands/` is what Claude Code reads. They must match.

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

### 5. Quality Gates (P3, P4)

**All quality checks must pass.**

#### 5a. Test Execution
```bash
pytest -v  # or project test command
```
- **100% of tests must pass**
- Report any failures with details

#### 5b. Coverage Check
```bash
pytest --cov=. --cov-report=term-missing
```
- Check against coverage threshold (if defined)
- Report uncovered critical paths

#### 5c. Linting & Type Checking
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

### 6. Benchmark Execution (P5)

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

**After successful closeout, distribute updates to all spokes.**

This step runs automatically when:
- Running from framework or hub node
- `lug-wai-paths` provides hub_path and framework_path
- Closeout completed successfully

**Teach Procedure:**
```
1. Read hub registry for active spokes
2. For each spoke with WAI-Spoke/:
   - Generate upgrade-adoption-plan.json
   - Distribute template files to seed/ingest/
   - Update registry with taught_at timestamp
3. Report results
```

**Report:**
```
Teach Distribution:
- Spokes taught: [N]/[M]
- Files distributed: [N] per spoke
- Registry updated: ✓
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
- Spokes: [N]/[M] taught
- Files: [N] per spoke
- Registry: updated

## Status: SHIPPED ✓
```

---

## Related Commands

- `/wai-closeout` - Just save state (no quality gates)
- `/wai-status` - Framework health check
- `/wai-time` - Check context usage

---

*Shipit = Verify quality, then save. Ready for users.*
