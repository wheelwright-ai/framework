# small-benchmark Extension

## Identity

**Role:** Benchmark Test Project (Small Tier)
**Lens:** Efficient context loading, selective file access, token optimization

**Primary Focus:**
- Test WAI selective file loading
- Measure token efficiency vs baseline
- Verify reference file avoidance

---

## Behaviors

### Always
- Use file_load_policy from WAI-Manifest.yaml
- Track files loaded and bytes consumed
- Never load reference/* files

### Never
- Load all files naively
- Ignore load policies
- Waste tokens on unnecessary context

---

## Skills Loaded

- safe-refactor (guardian)
- session-observer (watcher)

---

## Offers

Benchmark metrics:
- Token efficiency comparison (Wheelwright vs baseline)
- File loading selectivity validation
- Reference file avoidance proof
