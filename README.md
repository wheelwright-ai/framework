# Wheelwright Framework

AI session continuity framework for building spokes, hubs, and shared agent behavior.

This repository is the public framework product. It is not a live spoke.

## What This Repo Is

Wheelwright gives AI assistants durable project continuity through file-based protocol assets:

- `skills` define agent behavior
- `teachings` distribute improvements
- `lugs` carry durable work and decision records inside a spoke or hub
- `bootstrap` creates new spoke or hub installations from the framework

The public repo ships the framework assets needed to create and evolve those nodes. Live runtime state belongs in the cloned spoke or hub, not here.

## Repository Roles

- `this repo`: clean public upstream for framework code, teachings, templates, bootstrap, and docs
- `hub`: a separate project created from this framework
- `spoke`: any project initialized to use Wheelwright
- `your local framework clone`: the place where you can evolve the framework itself and then promote sanitized changes upstream

## Current Transition State

The repo is being remodeled from a historical dogfood layout into a cleaner public architecture.

Target direction:

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
templates/
tests/
docs/
```

Until that remodel is complete, some public assets still live in legacy paths such as `framework/`, `templates/`, `teachings/`, `hub/`, and `tools/`.

## What Public Does Not Contain

This public repo should not carry:

- live `WAI-Spoke/`
- session history
- lugs from active work
- private runtime artifacts
- personal operational traces
- hub or spoke state that belongs to a real running node

If you want a working node, clone the framework and bootstrap one.

## Bootstrap Model

A public clone should support three outcomes:

1. Create a spoke.
2. Create a hub.
3. Evolve the framework itself from a local fork.

Teachings remain first-class bootstrap assets. The framework should preserve the visible path between product code and the teachings that distribute it.

## Public Surfaces Today

These are the strongest public framework surfaces in the current tree:

- `bootstrap/`
- `templates/`
- `teachings/`
- `tools/`
- `docs/`
- `shared/codebase/skills/`
- selected parts of `hub/`
- `tests/`

These are not part of the default public remodel:

- `WAI-Spoke/`
- `archive/`
- `benchmarks/`
- `test-bench/`
- `src/`
- `tracks/`
- most of `reference/` unless individual documents are rescued

## Using The Framework

### Create a spoke

Use the framework bootstrap flow to create a spoke in another project directory. During the current transition, the bootstrap assets live under `bootstrap/` and `templates/`.

The spoke should contain the live `WAI-Spoke/` state, lugs, sessions, and runtime files. This framework repo should not.

### Create a hub

Use the hub templates and teachings to create a dedicated hub project. Hub runtime state and registry data belong in that hub project, not in this repo.

### Evolve the framework

Keep your local framework clone as a working fork, improve the framework there, and promote only sanitized framework changes back upstream.

Rule of thumb: promote the product, not the process.

## Source Of Truth

- behavioral protocol: `templates/commands/` and `spoke/codebase/templates/commands/`
- shared teachings: `shared/teachings/`
- hub teachings: `hub/teachings/`
- framework docs: `docs/`
- shared framework skills: `shared/codebase/skills/`

Those paths will be normalized further during the public remodel.

## Status

Current planning and migration artifacts:

- [PUBLIC-PRIVATE-CUTOVER.md](PUBLIC-PRIVATE-CUTOVER.md)
- [REPO-VALUE-AUDIT.md](REPO-VALUE-AUDIT.md)
- [REPO-MOVE-MAP.md](REPO-MOVE-MAP.md)

They describe the target public shape, what survives the remodel, and what moves to the private fork.

## License

MIT. See [LICENSE](LICENSE).

## Creator

Created by Mario Vaccari.
