# WAI v1 Data Archive

This directory contains the complete state of WAI v1 (the CLI-based version) at the time of v2 migration.

## Why This Exists

WAI v1 used a CLI-based approach with the `wai` command. After an incident where the CLI accidentally destroyed the Hub folder, the architecture was redesigned as a file-based protocol (v2).

This data is preserved as:
1. **Historical reference** - Understanding how the system evolved
2. **Data recovery** - If any v1 Lugs/observations need to be referenced
3. **Migration reference** - For understanding what was migrated to v2

## Contents

### Core State Files
- `WAI-State.json` - v1 JSON state
- `WAI-State.md` - v1 strategic vision document (detailed)
- `WAI-Manifest.yaml` - v1 manifest format

### Work Logs
- `WAI-Lugs.jsonl` (94KB) - All Lugs from v1 development
- `WAI-Signals.jsonl` (27KB) - Cross-node signals from v1
- `WAI-Skills.jsonl` (10KB) - v1 skill definitions
- `observations.jsonl` (40KB) - Session observations from v1

### Index Files
- `WAI-File-Index.json` - File tree snapshot at v1
- `WAI-Point.json` - Entry point configuration

### Supporting
- `_framework/` - Framework utilities
- `lugs/` - Lug-related files
- `reference/` - v1 reference materials
- `seed/` - Seed data for new projects
- `wai-cli-launch.sh`, `wai-shell.sh` - v1 CLI launchers

## Migration to v2

v2 replaced:
- CLI commands → File-based skills (YAML)
- WAI-State.json → WAI-Manifest.yaml + BRIEF.md + EXTENSION.md
- Centralized state → Distributed spoke structure
- Signals as separate system → Signals as high-impact Lugs (impact >= 8)

## Data Value

The `WAI-Lugs.jsonl` file contains ~500+ Lugs documenting:
- All decisions made during framework development
- Diagnosis and prescriptions for bugs found
- Observations about patterns discovered
- Session summaries from development

This is institutional memory preserved as reference.

## Usage

**Read-only.** This data should not be modified.

To reference historical Lugs:
```bash
grep "some-topic" reference/v1-data/WAI-Lugs.jsonl | jq '.'
```

To see v1 skill definitions:
```bash
cat reference/v1-data/WAI-Skills.jsonl | jq '.'
```
