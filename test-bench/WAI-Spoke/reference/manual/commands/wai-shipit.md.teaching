# WAI Shipit

**Production Readiness Verification Protocol**

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

## Prerequisites

- Code changes complete
- Tests exist
- WAI-Spoke/ exists
- Git initialized

## Follow-ons

- Push to remote
- Deploy to production
- Announce release

---

## Shipit Procedure

### 1. File Hygiene
Scan for temp/debug/orphaned files. Delete or relocate.

### 2. Breaking Change Detection
Identify API/schema changes. Document with migration paths.

### 3. Dependency Audit
Check for security vulnerabilities and outdated packages.

### 4. Quality Gates
- Tests: 100% pass
- Coverage: meets threshold
- Linting: clean

### 5. Benchmarks
Run if available. Flag regressions.

### 6. Documentation
Update README, CHANGELOG as needed.

### 7. Pre-Ship Summary
Present full report. Get user confirmation.

### 8. Execute Closeout
Full `/wai-closeout` protocol.

### 9. Teach All Spokes (Auto)

**After successful closeout, distribute updates to all spokes.**

Runs automatically when:
- Running from framework or hub node
- `lug-wai-paths` provides paths
- Closeout completed successfully

---

## Output Format

```
## Shipit Complete

### Pre-Flight
- File hygiene: ✓
- Tests: ✓ [X/X passing]
- Documentation: ✓

### Closeout
- Version: [X.Y.Z]
- Commit: [hash]

### Teach (auto)
- Spokes: [N]/[M] taught

## Status: SHIPPED ✓
```

---

*Shipit = Verify quality, save, teach.*
