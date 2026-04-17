# Public / Private Cutover

Working policy and implementation plan for splitting Wheelwright Framework into:

- public upstream: this repository
- private development fork: `mariov96/wai-framework`

This file is a planning artifact for the cutover. It is not the reset itself.

## Level Set

The public repository is a framework product, not a live spoke.

That means the public repository:

- does not contain a live `WAI-Spoke/`
- does not contain `sessions/`
- does not contain `lugs/`
- does not contain private runtime history
- does contain the code, teachings, templates, and bootstrap paths needed to create a spoke, create a hub, or evolve the framework itself

The private repository `mariov96/wai-framework` becomes the active dogfood fork:

- it behaves like a normal spoke
- it keeps the valuable session history and lugs
- it carries the private overlay and live operational state
- it promotes sanitized framework advancements back to public intentionally

## Repository Roles

### Public upstream

Purpose: reusable framework product that anyone can clone.

Must contain:

- framework source
- teachings
- templates
- bootstrap scripts
- tests
- docs
- hub framework code that is part of the shipped product
- spoke framework code that is part of the shipped product
- shared framework code that both hub and spokes rely on

Must not contain:

- `WAI-Spoke/`
- `WAI-Spoke/sessions/`
- `WAI-Spoke/lugs/`
- private runtime artifacts
- personal archives
- thought-process traces
- private operational history
- PII beyond Mario being named as creator/maintainer where appropriate

### Private fork

Purpose: active dogfood, experimentation, live work tracking, and personal operating environment.

Will contain:

- live `WAI-Spoke/`
- session history
- lugs
- archives
- private hub state
- any private overlay needed to work effectively day to day

Remote model after cutover:

- public repo: canonical upstream
- private repo: `mariov96/wai-framework`
- private `origin` -> private repo
- private `upstream` -> public repo

## Decision Table

### 1. Public `WAI-Spoke/`

Decision: Option `B`

Public ships no live `WAI-Spoke/`.

Implications:

- bootstrap must create spoke or hub state from framework-owned assets
- docs/tests must stop treating this repo as a live dogfood spoke
- private repo becomes the only home for active `WAI-Spoke/`, sessions, and lugs

Recommendation accepted:

- use teachings as first-class bootstrap inputs so the path between framework code and distributable teachings stays visible

### 2. `.gitignore`

Decision: Option `A`

Public `.gitignore` should reflect explicit product boundaries, not hide framework-owned paths accidentally.

Implications:

- current blanket `WAI-Spoke/` ignore is a cleanup blocker
- private fork can keep spoke-style runtime ignores because it is the live environment
- public repo should exclude only intentional generated/runtime/private paths

Recommendation:

- use `.gitignore` to ignore artifacts, not architecture
- make the public/private boundary visible in the tree itself

### 3. Hub / spoke / shared organization

Decision: keep hub code public, but reorganize the public repo.

Target direction:

- `spoke/`
- `shared/`
- `hub/`

Within each area:

- `codebase/`
- `teachings/`

Recommendation:

- move toward this layout before the public history reset
- make code ownership obvious by path
- keep teachings adjacent to the code they distribute

Related cleanup assumptions now in force:

- `benchmarks/` is not part of the default public remodel
- `test-bench/` is not part of the default public remodel
- `reference/` is private/archive by default unless specific docs are rescued
- `src/` is excluded by default unless a real dependency is found
- `tracks/` is treated as externally owned because it has its own repo

### 4. Bootstrap contract

Decision: public clone should let a user bootstrap:

- a spoke
- a hub
- or an evolving framework fork

Recommendation:

- provide one obvious entrypoint
- preserve teachings-driven bootstrap where possible
- explicitly recommend keeping the cloned framework as the user's local fork to evolve the system

### 5. Public history reset

Decision: Option `A`

Recommendation:

- do one clean reset only after staged validation and private archival

### 6. Private repo bootstrap

Decision: Option `A`

Recommendation:

- create `mariov96/wai-framework` from the clean public baseline immediately after the public baseline is stable

### 7. Private overlay

Decision: Option `C`

Recommendation:

- keep durable private assets tracked in the private repo
- generate volatile runtime pieces where practical
- avoid a private setup that depends on undocumented manual state

### 8. Sanitization

Decision: Option `A`

Recommendation:

- preserve Mario attribution
- strip thought traces, private machine paths, behavioral fingerprints, and PII not required for authorship

### 9. Local rename

Decision: Option `C`

Recommendation:

- revisit folder rename after the private repo exists and remotes are wired
- do not spend early cutover energy on pathname churn

### 10. Promotion workflow

Decision: Option `A`

Recommendation:

- private-first, sanitized promotion into public
- promote the product, not the process

## Recommended Revisions

These are the non-negotiable maintainability improvements implied by the chosen model.

### Structure

- reorganize the public repo into `spoke/`, `shared/`, and `hub/`
- keep `codebase/` and `teachings/` siblings, not mixed
- remove live operational state from the public tree entirely
- add one short README per top-level product surface explaining purpose and source-of-truth

### Naming

- retire transitional or mixed-vocabulary paths once the new layout lands
- use role-based names like `codebase`, `teachings`, `runtime`, `generated`, `archive`
- avoid duplicate “reference” copies unless one is explicitly generated

### Bootstrap

- add one clear public bootstrap entrypoint
- make spoke bootstrap and hub bootstrap obvious options
- keep teachings as first-class bootstrap assets instead of burying them behind private state

### Source of truth

- mark generated files clearly
- document canonical inputs for every generated or distributed artifact
- avoid behavior that depends on stale mirrored copies without provenance

### Tests

- split tests by product surface: spoke, shared, hub, bootstrap
- add public-boundary tests asserting no live `WAI-Spoke/`, no `sessions/`, no `lugs/`
- add fresh-clone bootstrap smoke tests for both spoke and hub creation

### Docs

- add a root architecture map after the restructure
- add a promotion workflow document
- add a short public-reset note after history is rewritten

### Public surface discipline

- remodel only the public assets that still earn their keep
- default high-noise areas out of scope unless they prove a concrete dependency
- treat partial implementations as design cleanup work, not as content that must survive

## Target Public Shape

Exact file lists will be refined during implementation, but the public shape should converge toward:

```text
spoke/
  codebase/
  teachings/
hub/
  codebase/
  teachings/
shared/
  codebase/
  teachings/
bootstrap/
tests/
README.md
```

The current root-level mixed state should be treated as transitional, not as the final public architecture.

Current exclusion default for the remodel:

- `WAI-Spoke/`
- `archive/`
- `benchmarks/`
- `test-bench/`
- `src/`
- `tracks/`
- `reference/` unless specific documents are rescued
- private tool-specific folders and operational overlays

## Phased Implementation Plan

### Phase 1: Boundary and path inventory

Goal: know what exists, what is product, and what is private.

Deliverables:

- current-path inventory
- public/private/sanitize classification
- first-pass map from current paths to `spoke/`, `shared/`, `hub/`
- explicit exclude list for `benchmarks/`, `test-bench/`, `src/`, `tracks/`, and default-archived `reference/`

### Phase 2: Public architecture reshape

Goal: make the public repo legible before resetting history.

Deliverables:

- new top-level path structure
- relocated framework code and teachings
- per-surface README files
- no carry-forward of excluded high-noise areas unless they are explicitly rescued by the move map

### Phase 3: Bootstrap redesign

Goal: ensure a clean public clone can create a spoke or hub.

Deliverables:

- single obvious bootstrap entrypoint
- teachings-aware spoke bootstrap
- teachings-aware hub bootstrap
- docs that explain how to evolve the framework from a local fork

### Phase 4: Public sanitization

Goal: remove all private/live state from the public tree.

Deliverables:

- no live `WAI-Spoke/`
- no sessions
- no lugs
- no private runtime/state artifacts
- scrubbed docs/examples
- excluded high-noise directories removed from the public export

### Phase 5: Verification

Goal: prove the new public baseline works.

Deliverables:

- public-boundary tests
- spoke bootstrap smoke test
- hub bootstrap smoke test
- updated docs validation

### Phase 6: Private preservation

Goal: keep all valuable pre-reset history and private state.

Deliverables:

- private mirror/archive of the current repo
- rollback instructions
- clear reference to the archived source

### Phase 7: Public reset

Goal: establish the clean public era.

Deliverables:

- fresh public history
- one-time reset note
- post-reset clone guidance

### Phase 8: Private repo creation

Goal: stand up `mariov96/wai-framework` as the new working fork.

Deliverables:

- private repo created
- private overlay applied
- remotes configured as `origin` private / `upstream` public

### Phase 9: Ongoing promotion workflow

Goal: prevent drift back into mixed public/private behavior.

Deliverables:

- promotion workflow doc
- explicit sanitization checklist
- private-first -> public-promotion working norm

## Verification Gates

The cutover is not done until all of these are true:

- public tree contains no live `WAI-Spoke/`
- public tree contains no sessions or lugs
- public tree contains no `benchmarks/`, `test-bench/`, `src/`, or `tracks/` unless one was explicitly rescued and justified
- public tree uses the new `spoke/`, `shared/`, `hub/` organization consistently enough to be understandable
- bootstrap from a fresh public clone can create a spoke
- bootstrap from a fresh public clone can create a hub
- private archive exists before public history reset
- private repo exists and tracks the public repo as upstream

## Promotion Rule

Promote framework advancements from private to public by moving only the reusable, sanitized product change.

Public receives:

- framework behavior
- teachings
- templates
- tools
- tests
- docs

Public does not receive:

- process history
- session traces
- lugs
- live spoke state
- private runtime assumptions

## Refinement Items For Tomorrow

- exact mapping from current paths to `spoke/`, `shared/`, `hub/`
- exact `codebase/` and `teachings/` subpaths for each area
- bootstrap command surface and user-facing language
- `.gitignore` redesign for the transition
- public-boundary test plan
- private overlay contents for `mariov96/wai-framework`
