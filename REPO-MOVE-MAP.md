# Repo Move Map

Current-path to target-path plan for the public remodel.

Purpose:

- turn the value audit into an executable migration map
- show what survives, what is excluded, and what needs partial extraction
- identify blockers before file moves begin

Disposition labels:

- `MOVE` — keep and relocate into the target public structure
- `KEEP-TEMP` — keep in place for the transition, then revisit after bootstrap/tests are updated
- `EXTRACT` — rescue only part of the current path into the new public structure
- `EXCLUDE` — remove from the public remodel
- `PRIVATE` — preserve in the private fork only

Target public structure:

```text
spoke/
  codebase/
  teachings/
shared/
  codebase/
  teachings/
hub/
  codebase/
  teachings/
bootstrap/
tests/
docs/
templates/
```

The `templates/` path remains public for now because it is already a strong shipped surface. During implementation, some of its contents may migrate under `spoke/`, `shared/`, or `hub/`, but that should happen only once bootstrap and test contracts are updated.

## Keep / Move First

### `bootstrap/`

- disposition: `KEEP-TEMP`
- target: remain `bootstrap/` during the transition
- eventual role: public entrypoint for creating a spoke, creating a hub, or evolving a framework fork
- why:
  - already an obvious public surface
  - changing its path and behavior at the same time would create unnecessary churn
- blockers:
  - `bootstrap/spoke-upgrade.sh` assumes a live in-repo `WAI-Spoke/`
  - docs still frame bootstrap around the current dogfood layout
- follow-on work:
  - redesign the entrypoint contract first
  - then decide whether the implementation lives under `shared/codebase/bootstrap/` later

### `templates/`

- disposition: `KEEP-TEMP`
- target: remain `templates/` during the transition, then split intentionally
- why:
  - it is the main distributable asset surface today
  - contains spoke, hub, command, and AI-tool templates that should remain public
- likely future split:
  - `templates/spoke/*` informs `spoke/`
  - `templates/HUB/*` informs `hub/`
  - `templates/commands/*`, `templates/agents/*`, `templates/generic/*` inform `shared/`
- blockers:
  - split ownership with `framework/templates/`
  - command and teaching assets overlap with other public surfaces
- follow-on work:
  - inventory duplicates and define source-of-truth before any physical split

### `teachings/`

- disposition: `EXTRACT`
- target: primarily `shared/teachings/`, with spoke/hub-specific teachings moved later by scope
- why:
  - high public value
  - direct match for the teachings-driven bootstrap model
- blockers:
  - current teaching assets are mixed with signal-style historical items and framework-level skills
  - other teaching homes exist under `templates/teachings/` and `hub/teachings_repo/`
- follow-on work:
  - separate framework teachings from historical signal artifacts
  - define what remains as public teachings versus what becomes private archive material

### `framework/docs/`

- disposition: `EXTRACT`
- target: `docs/`
- why:
  - docs are public product material and should become easier to find
  - keeping docs nested under `framework/` makes ownership less obvious after the remodel
- blockers:
  - some docs point to dogfood-specific or benchmark-heavy surfaces
  - some doc areas may reference excluded directories
- follow-on work:
  - rescue the strong docs first: setup, glossary, hub architecture, spoke structure, goal-state
  - defer or drop benchmark-specific docs unless the harness is retained

### `framework/skills/`

- disposition: `MOVE`
- target: `shared/codebase/skills/`
- why:
  - these appear to be reusable framework behavior assets rather than private state
  - they fit the shared surface better than the old `framework/` bucket
- blockers:
  - tests and scripts may refer to current paths
- follow-on work:
  - path migration plus targeted test updates

## Public But Needs Decomposition

### `hub/`

- disposition: `EXTRACT`
- target:
  - framework behavior and templates -> `hub/codebase/`
  - hub teachings -> `hub/teachings/`
  - live/state-like files -> `PRIVATE` or `EXCLUDE`
- current concerns:
  - `hub/WAI-Hub/skills/WAI-Skills.jsonl` looks public and reusable
  - `hub/WAI-Manifest.yaml`, `hub/registry.yaml`, `hub/health.yaml`, `hub/taste.user.yaml`, `hub/WAI-Ledger.jsonl`, `hub/WAI-Lugs.jsonl`, and machine/intake content look stateful or example-like rather than clean shipped code
- blockers:
  - hub tree does not yet clearly separate product from state
- follow-on work:
  - define a minimal public hub template set
  - move all live/intake/machine/runtime content out of the public remodel

### `tools/`

- disposition: `EXTRACT`
- target:
  - public framework utilities -> `shared/codebase/tools/`
  - spoke-only/private operational helpers -> `PRIVATE` or `EXCLUDE`
- why:
  - strong source of public framework code, but mixed with spoke-specific operations
- blockers:
  - many scripts are named around live-spoke operations: `spoke_cleanup.py`, `generate_wakeup_brief.py`, `generate_knowme.py`
  - `__pycache__/` is mixed into the tree and should disappear entirely
- follow-on work:
  - classify each tool into public bootstrap/tooling, public validation, or private dogfood support
  - drop `__pycache__/` and other generated artifacts immediately

### `tests/`

- disposition: `KEEP-TEMP`
- target: remain `tests/` during the transition
- why:
  - test path is conventional and already public
  - reorganizing tests too early will slow bootstrap and boundary work
- blockers:
  - several tests assume a live in-repo `WAI-Spoke/`
  - idempotency and behavioral suites may encode current path assumptions
- follow-on work:
  - adapt tests to the public model
  - add explicit boundary tests for excluded paths
  - add fresh-clone bootstrap smoke tests for spoke and hub creation

### `README.md`

- disposition: `KEEP-TEMP`
- target: remain root `README.md`
- why:
  - root doc should continue to explain the repo
- blockers:
  - currently frames the repo as a live dogfood spoke
- follow-on work:
  - rewrite around “public framework that bootstraps spoke/hub/fork”

## Likely Public, Needs Review

### `wai/`, `wai_ozi.py`, `wai-enter.sh`, `wai-exit.sh`

- disposition: `REVIEW-AS-MOVE`
- likely target: `shared/codebase/cli/` or keep at root if they are the canonical entrypoints
- why:
  - likely product-facing command surfaces
- blockers:
  - command contract and bootstrap contract need to be aligned before moving entrypoints

### `config/`, `data/`, `registry/`, `examples/`, `lug/`

- disposition: `REVIEW-AS-EXTRACT`
- likely target:
  - framework-facing schemas/examples -> `shared/codebase/` or `docs/examples/`
  - stateful/generated content -> `EXCLUDE` or `PRIVATE`
- why:
  - likely mixed-value directories that need file-level review

## Default Private / Excluded

### `WAI-Spoke/`

- disposition: `PRIVATE`
- target: private repo overlay only
- why:
  - explicitly outside the public model
  - contains live sessions, lugs, runtime state, and dogfood history

### `archive/`

- disposition: `PRIVATE`
- why:
  - useful historical reference, poor public product surface

### `.claude/`, `.gemini/`, `KnowMe.md`, `hub-profile.json`, `hub-registry.json`, `.spoke-metadata.yaml`

- disposition: `PRIVATE`
- why:
  - personal or operationally specific
  - any reusable fragments belong under `templates/` or future docs, not in current form

### `benchmarks/`, `test-bench/`, `src/`, `tracks/`

- disposition: `EXCLUDE`
- why:
  - user has already called these out as low-confidence or externally owned
  - carrying them through the remodel would add noise and delay
- rescue rule:
  - only reintroduce a minimal curated subset if a concrete public dependency is discovered

### `reference/`

- disposition: `EXCLUDE` by default
- why:
  - historical and mixed-value
  - rescue individual docs only if they materially improve the public architecture/docs set

## Immediate Implementation Sequence

1. Rewrite `README.md` and bootstrap docs to match the public model.
2. Classify `tools/` into public framework utilities vs private dogfood support.
3. Decompose `hub/` into public framework assets vs stateful/runtime artifacts.
4. Normalize teaching ownership across `teachings/`, `templates/teachings/`, and hub teaching paths.
5. Consolidate `framework/docs/` into a root `docs/` surface.
6. Move reusable `framework/skills/` into `shared/codebase/skills/`.
7. Update tests to validate bootstrap-generated spoke/hub structures instead of a live in-repo spoke.
8. Remove excluded high-noise paths from the public export.

## Open Questions To Resolve During Implementation

- Which `tools/*.py` scripts are truly public framework utilities versus private spoke maintenance helpers?
- Should command markdown under `templates/commands/` remain template-only, or also have a mirrored home under `shared/teachings/`?
- Which current `hub/` files are templates/specimens and which are accidental live state?
- Does `framework/templates/` remain a standalone public surface, or should it collapse into `templates/` once source-of-truth is clear?
