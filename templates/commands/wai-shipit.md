# WAI Shipit

Verify quality gates, then run closeout. For releases and progress saves.

---

## Execution Context

- **Nodes:** spoke, hub, framework
- **Paths Required:** spoke_path; framework_path + hub_path (for teach)

---

## Shipit Procedure

### 0. Production Release Intent

Ask: **Is this a production release? (y/n)**
- **Yes:** All steps run. After closeout, git tag `v{version}` is applied and pushed.
- **No:** All steps run. No tag applied.

### 1. Sync Skills (FRAMEWORK ONLY)

If running from the framework repo, sync canonical source to IDE and template spoke:

```bash
# Claude Code slash commands (flat)
yes | cp templates/commands/wai*.md .claude/commands/

# Framework spoke commands (real copies — framework dogfoods teaching workflow)
yes | cp templates/commands/wai*.md WAI-Spoke/commands/

# Template spoke skill subdirs
for skill_dir in templates/spoke/skills/*/; do
  for f in "$skill_dir"*.md; do
    [ -f "$f" ] || continue
    src="templates/commands/$(basename "$f")"
    [ -f "$src" ] && \cp "$src" "$f" 2>/dev/null || true
  done
done
```

Skip if not the framework repo.

### 2. File Hygiene

Scan for AI sprawl: `temp_*`, `*.bak`, `*.tmp`, `debug_*`, `scratch_*`, `old_*`, `*.orig`, `*_backup*`. Delete temp files, relocate useful references, ask user about unknowns. Report findings before proceeding.

### 3. Breaking Change Detection

Check for: API signature changes, removed public functions, changed config formats, CLI argument changes. Document each in CHANGELOG.md with migration guidance. Confirm user acknowledges before proceeding.

### 4. Dependency Audit

Run available security audits (`pip-audit`, `npm audit`, etc.). Check for known vulnerabilities and severely outdated packages. Report findings. Stop on critical vulnerabilities.

### 5. Quality Gates — MANDATORY

All gates must pass. Failure aborts shipit.

**5a. Tests:** Auto-detect and run (`pytest`, `npm test`, `make test`). Non-zero exit = abort.

**5b. Linting:** Auto-detect and run (`ruff`, `flake8`, `eslint`). Non-zero exit = abort.

**5c. Type checking (optional):** Run if configured (`mypy`). Warnings only, non-blocking.

Report gate results. Override with `SHIPIT_SKIP_TESTS=1` or `SHIPIT_SKIP_LINT=1` (emergency only — log as signal).

### 6. Benchmark Execution

Run benchmarks if available (`benchmarks/runner/benchmark_runner.py` for Wheelwright, or project-specific). Compare against prior run. On regression: offer abort / acknowledge / update baseline. Skip with `SHIPIT_SKIP_BENCHMARKS=1`.

### 7. Documentation Updates

Review and update: README.md, CHANGELOG.md, API docs, config docs. Note what was updated.

### 8. Pre-Ship Summary

Present full report (hygiene, breaking changes, deps, gates, benchmarks, docs) and get user confirmation before proceeding.

### 9. Execute Closeout

Run full `/wai-closeout` protocol. All state preservation, signal extraction, teaching generation, commit and push.

### 9b. Apply Release Tag (Production Release Only)

Skip if not a production release.

```bash
git tag v{version}
git push origin v{version}
```

If tag already exists: stop and report conflict. Do not force-overwrite.

### 10. Teach Distribution

Handled automatically by closeout Step 9b — teachings are generated and published to hub during closeout. No separate action needed.

---

## Success Criteria

- [ ] File hygiene complete
- [ ] Breaking changes documented
- [ ] Dependencies audited
- [ ] Tests pass, linting clean
- [ ] Benchmarks run (no unacknowledged regressions)
- [ ] Documentation updated
- [ ] User confirmed ready to ship
- [ ] Closeout executed successfully
- [ ] Release tag applied (production only)

---

*Shipit = Verify quality, then save. Ready for users.*
