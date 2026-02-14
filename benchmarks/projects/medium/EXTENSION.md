# medium-benchmark Extension

## Identity

**Role:** Benchmark Test Project (Medium Tier)
**Lens:** Multi-file coordination, dependency tracking, efficient context management

**Primary Focus:**
- Test WAI multi-file change coordination
- Measure token efficiency with larger codebases
- Verify reference file avoidance at scale

---

## Behaviors

### Always
- Use file_load_policy from WAI-Manifest.yaml
- Track cross-file dependencies
- Load related files together (e.g., model + view + controller)
- Never load reference/* files

### Never
- Load all files naively
- Miss file dependencies
- Waste tokens on unnecessary context

---

## Skills Loaded

- safe-refactor (guardian)
- session-observer (watcher)

---

## Offers

Benchmark metrics:
- Multi-file coordination efficiency
- Token usage at medium complexity
- Dependency tracking validation
- Reference file avoidance proof
