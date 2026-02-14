# BRIEF — medium-benchmark

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md (wheel-wide policies)

**Purpose:** Medium-complexity benchmark testing Wheelwright multi-file coordination

---

## Always
- Load ONLY files needed for the task (never reference files)
- Follow file_load_policy from WAI-Manifest.yaml
- Track token usage across multi-file changes
- Coordinate changes across related files (models, views, controllers)

## Never
- Load reference documentation files (reference/*.md)
- Load all files naively
- Ignore file dependencies when making changes

## When Uncertain
- Check WAI-Manifest.yaml for load policies
- Use Lugs to track multi-file coordination
- Verify all affected files are updated together
