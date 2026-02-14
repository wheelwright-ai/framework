# BRIEF — small-benchmark

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md (wheel-wide policies)

**Purpose:** Benchmark project testing Wheelwright selective file loading efficiency

---

## Always
- Load ONLY files needed for the task (never reference files)
- Follow file_load_policy from WAI-Manifest.yaml
- Track token usage and file loading metrics

## Never
- Load reference documentation files (reference/*.md)
- Load all files naively
- Ignore file_load_policy constraints

## When Uncertain
- Check WAI-Manifest.yaml for load_always vs load_on_demand vs never_load
- Prefer minimal file loading over comprehensive
