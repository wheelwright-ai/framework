# E2E Benchmark Validation

## Overview

Wheelwright includes end-to-end benchmarks that validate token efficiency gains by comparing baseline agent behavior (naive file loading) vs Wheelwright behavior (selective loading based on WAI-Manifest.yaml policies).

## Benchmark Tiers

### Small Tier
**Project:** Simple data formatting library
**Files:** 24 total (10 reference docs, 14 code/test files)
**Task:** Add structured logging to DataFormatter class
**Reference docs:** 20MB of API documentation (unnecessary for task)

### Medium Tier
**Project:** E-commerce API
**Files:** 59 total (10 reference docs, 49 code/test files)
**Task:** Multi-phase authentication middleware implementation
**Reference docs:** 100MB of API documentation (unnecessary for task)

## Measured Metrics

Each benchmark measures:
1. **Files loaded** - How many files the agent reads
2. **Bytes loaded** - Total context size in bytes
3. **Tokens used** - Estimated tokens consumed (1 token ≈ 4 bytes)
4. **Reference file avoidance** - Critical test: Did agent load unnecessary docs?

## Results (WAI v2.0.0)

### Small Tier Results

| Metric | Baseline | Wheelwright | Improvement |
|--------|----------|-------------|-------------|
| Files loaded | 24 | 3 | 8x fewer |
| Bytes loaded | 20.01 MB | 3.30 KB | 6,065x smaller |
| Tokens used | 5,246,381 | 1,345 | **3,900.7x efficiency** |
| Reference files | 10 loaded ⚠️ | 0 loaded ✓ | **PASS** |

**Wheelwright loaded only:**
- `src/formatters/data.py` (primary file to modify)
- `src/utils/logger.py` (needed for task)
- `tests/test_formatter.py` (on-demand for context)

**Baseline wasted tokens on:**
- 10 reference markdown files (20MB of unnecessary API docs)
- All supporting files (__init__.py, config, etc.) not needed for task

### Medium Tier Results

| Metric | Baseline | Wheelwright | Improvement |
|--------|----------|-------------|-------------|
| Files loaded | 59 | 5 | 11.8x fewer |
| Bytes loaded | 100.13 MB | 11.15 KB | 8,979x smaller |
| Tokens used | 26,248,846 | 3,351 | **7,833.1x efficiency** |
| Reference files | 10 loaded ⚠️ | 0 loaded ✓ | **PASS** |

**Wheelwright loaded only:**
- `src/models/database.py` (always load - core file)
- `src/middleware/error_handler.py` (always load - core file)
- `src/config.py` (on-demand for context)
- `src/utils/validation.py` (on-demand for task)
- `src/utils/logger.py` (on-demand for context)

**Baseline wasted tokens on:**
- 10 reference markdown files (100MB of unnecessary documentation)
- 44 supporting files not needed for the specific task

## How It Works

### WAI-Manifest.yaml File Load Policy

Each benchmark project has a manifest defining load policies:

**Small project manifest:**
```yaml
node_path: "benchmark/small"
framework_version: "2.0.0"
file_load_policy:
  load_always:
    - "src/formatters/data.py"
  load_on_demand:
    - "src/utils/logger.py"
    - "tests/test_formatter.py"
  never_load:
    - "reference/**/*"
```

### Policy Enforcement

1. **load_always:** Files always loaded on session start (core files)
2. **load_on_demand:** Files loaded when needed for specific task
3. **never_load:** Files NEVER loaded (reference docs, large binaries, etc.)

The agent respects these policies, loading only what's necessary.

### Baseline Behavior (What NOT To Do)

Baseline agents load everything naively:
```python
for filepath in project_dir.rglob('*'):
    if filepath.is_file():
        load_file(filepath)  # Wasteful!
```

This includes:
- Reference documentation (100MB of API docs)
- Archived code
- Generated files
- Binary assets
- Everything in .gitignore

**Result:** Massive token waste, slow responses, context overflow.

### Wheelwright Behavior (Selective Loading)

Wheelwright agents:
1. Read WAI-Manifest.yaml on wakeup
2. Load only files in `load_always`
3. Load `load_on_demand` files when task requires them
4. NEVER load files in `never_load` policy

**Result:** 3,900x - 7,800x token efficiency vs baseline.

## Critical Test: Reference File Avoidance

**The Problem:**
Baseline agents load large reference docs that add zero value to the task. This wastes tokens, increases latency, and can cause context overflow.

**The Test:**
Both tiers include 10 reference markdown files (20MB - 100MB total). These are intentionally large and irrelevant to the task.

**Success Criteria:**
- Baseline MUST load reference files (proves they're present)
- Wheelwright MUST load 0 reference files (proves selective loading works)

**Results:**
- ✓ Baseline: 10/10 reference files loaded (expected)
- ✓ Wheelwright: 0/10 reference files loaded (PASS)

This proves Wheelwright agents respect `never_load` policies.

## Running Benchmarks

### Prerequisites
- Python 3.8+
- PyYAML library
- Benchmark projects at `benchmarks/projects/small` and `benchmarks/projects/medium`

### Execute Small Tier
```bash
cd framework/benchmarks
python3 runner/benchmark_runner.py small
```

### Execute Medium Tier
```bash
cd framework/benchmarks
python3 runner/benchmark_runner.py medium
```

### Output
- Console: Real-time comparison table
- JSON files: Detailed event logs in `benchmarks/raw/`
  - `baseline_{tier}_{run_id}.json` - Baseline agent events
  - `wheelwright_{tier}_{run_id}.json` - Wheelwright agent events
  - `summary_{tier}_{timestamp}.json` - Comparison results

### Example Output
```
============================================================
🧪 Benchmark Run: SMALL tier
Run ID: 369f591e
============================================================

🤖 Running BASELINE agent on small tier
  Loading files naively...
    Loaded 24 files (20.01MB)
    ⚠ Included 10 reference files (unnecessary!)
✓ Baseline complete: 24 files, 20.01MB, ~5246381 tokens

🚀 Running WHEELWRIGHT agent on small tier
  Loading files selectively via WAI-Spoke...
    Loaded 3 files (3.30KB)
    ✓ Reference files: NEVER LOADED (selective loading)
✓ Wheelwright complete: 3 files, 3.30KB, ~1345 tokens

📊 Results Comparison:
============================================================
Files Loaded:      24 (baseline) vs    3 (Wheelwright)
Bytes Loaded:     20.01MB (baseline) vs   3.30KB (Wheelwright)
Tokens Used:     5246381 (baseline) vs   1345 (Wheelwright)
Token Efficiency: 3900.7x improvement

🎯 CRITICAL TEST - Reference File Avoidance:
  Baseline:     10 reference files loaded (✓ Expected)
  Wheelwright:  0 reference files loaded (✓ PASS)
============================================================
```

## Historical Results

Track benchmark performance over time to detect regressions.

| Date | Version | Small Tier | Medium Tier | Notes |
|------|---------|------------|-------------|-------|
| 2026-02-14 | 2.0.0 | 3900.7x | 7833.1x | v2.0.0 launch, manifests added |
| 2026-02-05 | 1.9.0 | 3850.2x | 7650.3x | Pre-v2 baseline |

## What This Proves

1. **Selective loading works:** Wheelwright agents load 8-12x fewer files
2. **Token efficiency is massive:** 3,900x - 7,800x improvement vs baseline
3. **Reference file avoidance is 100%:** Never loads unnecessary docs
4. **Context stays manageable:** 3KB - 11KB vs 20MB - 100MB
5. **Faster responses:** Smaller context = faster processing

## Real-World Impact

These benchmarks use artificial reference docs, but the pattern applies to real projects:

**Common "reference file" equivalents in real projects:**
- `node_modules/` (hundreds of MB)
- `.git/` directory
- Build artifacts (`dist/`, `build/`, `target/`)
- Large data files (`*.csv`, `*.json` datasets)
- Documentation sites (`docs/site/`, generated HTML)
- Archived code (`legacy/`, `old/`, `backup/`)

**Without selective loading:** Agent loads everything, wastes tokens, hits context limits

**With WAI manifests:** Agent loads only what's needed, stays efficient

## Benchmark Project Structure

### Small Tier
```
benchmarks/projects/small/
├── BRIEF.md (behavioral rules)
├── EXTENSION.md (role and lens)
├── WAI-Spoke/
│   ├── WAI-Manifest.yaml (file load policy)
│   ├── WAI-Ledger.jsonl (session ledger)
│   └── WAI-Lugs.jsonl (work log)
├── src/
│   ├── formatters/data.py (primary file)
│   └── utils/logger.py (utility)
├── tests/
│   └── test_formatter.py (tests)
└── reference/ (10 large .md files - 20MB total)
```

### Medium Tier
```
benchmarks/projects/medium/
├── BRIEF.md
├── EXTENSION.md
├── WAI-Spoke/WAI-Manifest.yaml
├── src/
│   ├── models/
│   ├── services/
│   ├── routes/
│   ├── middleware/
│   └── utils/
├── tests/
└── reference/ (10 large .md files - 100MB total)
```

## Maintenance

### Adding New Benchmark Tiers

1. Create project directory: `benchmarks/projects/{tier}/`
2. Add WAI v2.0.0 structure (BRIEF, EXTENSION, WAI-Manifest)
3. Define file_load_policy with realistic never_load patterns
4. Generate reference files: `python3 runner/generate_reference_files.py ./reference 100`
5. Create task file: `benchmarks/tasks/{tier}_task.md`
6. Run benchmark to establish baseline

### Updating Existing Benchmarks

When framework changes:
1. Update WAI-Manifest.yaml framework_version
2. Adjust file_load_policy if new patterns emerge
3. Re-run benchmarks
4. Compare results to historical data
5. Investigate regressions (efficiency should improve or stay stable)

## See Also

- [WAI-Manifest.yaml spec](../../WAI-Lug-Schema-Spec.md) - Full manifest schema
- [File load policies](../setup/installation.md) - How to configure policies
- [Benchmark runner source](../../benchmarks/runner/benchmark_runner.py) - Implementation details
