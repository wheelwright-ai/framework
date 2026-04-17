# Repo Value Audit

First-pass value audit for the current Wheelwright Framework repository.

Purpose:

- decide what deserves to survive the remodel
- separate framework product from private dogfood/state
- identify partially implemented areas that need follow-on work instead of being moved blindly

Disposition labels:

- `KEEP-PUBLIC` — belongs in the clean public framework repo
- `ARCHIVE-PRIVATE` — valuable, but only in the private fork/archive
- `DELETE/EXCLUDE` — not worth carrying forward into the public remodel
- `REVIEW` — useful, but needs a deliberate decision or partial extraction

## Top-Level Audit

### Strong keep-public candidates

- `bootstrap/`
  - core to the public product
  - currently hard-wired to live `WAI-Spoke/` assumptions, so it needs redesign rather than removal

- `templates/`
  - still the main shipping surface for generated spoke/hub assets
  - likely feeds future `spoke/`, `shared/`, and `hub` layout

- `teachings/`
  - high-value public framework asset
  - should likely become part of the new `spoke/teachings`, `shared/teachings`, or `hub/teachings` layout

- `tools/`
  - contains most operational/product scripts worth preserving
  - needs classification into public framework tools vs private spoke-only tools

- `tests/`
  - public value is high
  - many tests currently assume a live `WAI-Spoke/`, so they need adaptation rather than deletion

- `framework/`
  - public value is high
  - contains docs, skills, templates, and conceptual specs

- `hub/`
  - keep public where it contains framework hub code and teachings structure
  - split out private hub state/data during remodel

- `README.md`
  - public essential
  - currently describes the repo as a live dogfood spoke and will need major revision

- `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`
  - standard public repo value

### Strong archive-private candidates

- `WAI-Spoke/`
  - largest private/value-rich dogfood area
  - should not survive in the public remodel
  - this entire tree is the strongest candidate for the private overlay/fork

- `.claude/`
  - valuable for your private workflow
  - too tool-specific and operationally personal for the clean public repo as-is
  - selected template-worthy parts already belong under `templates/`

- `.gemini/`
  - same pattern as `.claude/`

- `KnowMe.md`
  - high private value, low public product value in current form
  - contains dogfood/session-oriented framing

- `hub-profile.json`, `hub-registry.json`, `.spoke-metadata.yaml`
  - likely operational state or private coordination artifacts
  - not obvious public product assets in current location

### Strong delete/exclude candidates

- `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`
  - pure local artifacts

- `.env.dev`
  - local/private

- `benchmark_epic008.json`
  - singleton artifact with no obvious product role

- `archive/`
  - useful as private historical reference, but not as part of the clean public baseline
  - some parts may later inform docs, but the directory itself is not a clean public surface

### Review / likely partial extraction

- `benchmarks/`
  - very large
  - user judges overall value as questionable
  - recommendation: remove from the public remodel unless a small, clearly reusable subset proves necessary during implementation

- `reference/`
  - appears to be a mix of useful architecture docs and historical migration residue
  - user is doubtful on overall value
  - recommendation: default to archive/private exclusion; only rescue individual docs if they are actively needed in the public docs set

- `test-bench/`
  - connected to benchmarking
  - looks like a clone-heavy operational sandbox
  - user is comfortable removing it with benchmarks unless a must-keep fixture is discovered

- `src/`
  - small but suspicious
  - looks like an alternate implementation surface that may be partially implemented
  - user is doubtful on value
  - recommendation: default to exclude unless a clear shipped component depends on it

- `website/`
  - unclear whether this is public product, supporting docs site, or unrelated application work
  - review before move

- `tracks/`
  - user says this has its own repo
  - recommendation: remove from this public remodel and treat as external ownership unless a tiny compatibility stub is needed

- `lug/`
  - likely documentation/spec material
  - may belong under `shared/` or docs after review

- `examples/`
  - public value possible
  - must be sanitized and aligned to the new architecture

- `data/`, `registry/`, `config/`
  - probably public in part, but need file-level review

- `wai/`, `wai_ozi.py`, `wai-enter.sh`, `wai-exit.sh`
  - likely productized entrypoints/utilities
  - review how they fit the new structure

## Strong New Direction From User Decisions

These are now working assumptions, not loose suggestions:

- the public repo should have no live `WAI-Spoke/`
- bootstrap should explicitly support creating a spoke, creating a hub, or evolving the framework fork itself
- the public remodel should prioritize `spoke/`, `shared/`, and `hub/` as the main product surfaces
- `benchmarks/`, `test-bench/`, `src/`, and `tracks/` are out of the default public remodel unless a concrete dependency is discovered
- `reference/` is out by default; rescue only individual documents with clear product value

Implication:

- the remodel should start by shrinking the public surface, not by finding a home for every existing directory
- “partially implemented” areas should be treated as design debt to resolve, not as assets to move forward intact

## High-Noise / High-Cruft Areas

### `WAI-Spoke/`

Disposition: `ARCHIVE-PRIVATE`

Why:

- contains live spoke state, sessions, lugs, runtime, archive, and generated outputs
- directly conflicts with the chosen public model
- should become the nucleus of the private `mariov96/wai-framework` overlay

Implication:

- anything in this tree that is actually framework source must be promoted out explicitly
- we should not move `WAI-Spoke/` into the new public layout; we should mine it selectively

### `archive/`

Disposition: `ARCHIVE-PRIVATE`

Why:

- already self-identifies as deprecated/historical in multiple subpaths
- contains deprecated gardener scripts, old CLI code, and one-off migration scripts
- valuable for private forensic reference, not clean public structure

Implication:

- keep privately
- only rescue specific files if they are still the best source of truth for a public component

### `reference/`

Disposition: `ARCHIVE-PRIVATE`

Why:

- contains both architecture material and obvious historical/v1 residue
- `reference/historical/` and `reference/v1-data/` are not good public product surfaces in the remodel
- user is doubtful on overall value

Recommendation:

- archive by default
- rescue only specific documents if the public docs truly need them

### `benchmarks/`

Disposition: `DELETE/EXCLUDE`

Why:

- large footprint
- likely blends useful benchmark harnesses with bulky saved outputs
- user is comfortable removing it from the public remodel

Recommendation:

- exclude from the public remodel
- if a genuinely valuable benchmark harness is discovered later, reintroduce a minimal curated benchmark package rather than carrying the current tree forward

### `test-bench/`

Disposition: `DELETE/EXCLUDE`

Why:

- likely useful for teaching/bootstrap validation
- likely also contains clone-style sandbox state
- user notes it is connected to benchmarking and is comfortable removing it

Recommendation:

- exclude from the public remodel unless a tiny fixture subset proves essential for bootstrap or teaching validation

### `src/`

Disposition: `DELETE/EXCLUDE`

Why:

- looks like an alternate implementation surface with very small footprint relative to `tools/` and `framework/skills`
- user is doubtful on value

Recommendation:

- exclude from the public remodel unless a concrete dependency emerges during path mapping

### `tracks/`

Disposition: `DELETE/EXCLUDE`

Why:

- user says it has its own repository
- carrying it here would blur ownership boundaries in the remodel

Recommendation:

- remove from the public remodel
- leave only documentation or integration references if truly needed

## Partial / Split-Brain Implementations

These are the strongest signs that remodeling is not just path cleanup.

### 1. Public model vs current docs/bootstrap

Status: partially implemented / contradictory

Evidence:

- `README.md` still describes this repository as a live dogfood spoke
- bootstrap docs and scripts assume the framework repo carries `WAI-Spoke/`
- `PUBLIC-PRIVATE-CUTOVER.md` now says the public repo should have no live `WAI-Spoke/`

Implication:

- docs and bootstrap need coordinated redesign
- this is not a simple move operation

### 2. `templates/` vs `framework/templates/`

Status: partially implemented / split ownership

Observation:

- both exist
- duplicate filenames were not the main issue in the quick scan, which suggests a conceptual split instead of a tidy one
- likely one is “shipped generator surface” while the other is “framework internal template/spec surface”

Implication:

- we need one clear template authority in the remodeled public tree

### 3. Root `teachings/` vs `hub/teachings_repo/` vs `templates/teachings`

Status: partially implemented / multiple teaching homes

Observation:

- no simple filename duplication surfaced, but there are clearly multiple teaching containers
- this is likely intentional evolution that never got normalized

Implication:

- the remodel needs a single obvious teaching topology
- this is central because bootstrap is supposed to stay teachings-driven

### 4. `src/` vs `tools/` vs `framework/skills`

Status: partially implemented / alternate implementation surfaces

Observation:

- `src/` is small compared with `tools/` and `framework/skills`
- likely indicates an architectural direction that did not become the dominant one

Implication:

- default assumption is now that `src/` is an unfinished branch of the design unless a concrete public dependency is found

### 5. `hub/` mixes code and state

Status: partially implemented / mixed concerns

Observation:

- contains reusable hub/framework code and clearly stateful artifacts like registries, intake, ledgers, machine records

Implication:

- public remodel should keep hub code and teachings, but strip live hub state

### 6. Tests assume live spoke layout

Status: partially implemented / now misaligned with target model

Observation:

- many tests explicitly assert `WAI-Spoke/` structure, lugs, sessions, and spoke-local runtime behavior

Implication:

- test suite needs splitting into:
  - public framework tests
  - bootstrap-generated spoke/hub tests
  - private dogfood tests, if any

## Recommended First-Cut Disposition Map

### Keep public and remodel

- `bootstrap/`
- `framework/`
- `templates/`
- `teachings/`
- `tools/`
- `tests/`
- selected `hub/`
- selected `reference/` docs only if actively needed
- selected `examples/`
- selected `lug/`
- selected `config/`, `data/`, `registry/`, `wai/`

### Move to private overlay/archive

- `WAI-Spoke/`
- `.claude/`
- `.gemini/`
- `.hub/`
- `archive/`
- `reference/` (default)
- `KnowMe.md`
- stateful root JSON/YAML files that are operational rather than productized

### Exclude/delete from public baseline

- caches
- local env files
- singleton generated artifacts with no product role
- `benchmarks/`
- `test-bench/`
- `src/`
- `tracks/`
- raw benchmark outputs unless explicitly retained as public fixtures

## Strongest Recommendations Before Remodeling

1. Do a path-by-path source-of-truth audit before moving files.
2. Treat `WAI-Spoke/` as private by default; only rescue framework assets explicitly.
3. Collapse the teaching topology into one obvious public model before rewriting bootstrap.
4. Decide whether `src/` is real or abandoned before assigning it a place in the new structure.
5. Split public framework tests from private/live-spoke assumptions early, otherwise the remodel will look more broken than it is.

## Next Audit Step

The next useful pass is a move-map audit:

- current path
- proposed target path
- disposition
- rationale
- blockers / follow-on work

That is the artifact we should build before physically moving directories.
