# Bootstrap

Bootstrap assets for creating new Wheelwright nodes from the public framework.

This folder is in transition. The public contract is:

- a framework clone should be able to bootstrap a spoke
- a framework clone should be able to bootstrap a hub
- a framework clone can also be kept as the user's evolving framework fork

The current scripts and docs still reflect the older dogfood-era layout in places. Treat this folder as the active migration surface for that cleanup.

## Current Assets

- `spoke-upgrade.sh`
  - current spoke bootstrap/upgrade entrypoint
  - still tied to old private-path assumptions and needs redesign
- `build_a_wai_spoke.md`
  - manual spoke bootstrap notes
  - needs to be aligned to the public clone model
- `WAI-Minimal.template.md`
  - lightweight single-file capture for initializing context before a full spoke exists
- `capture_a_chat.md`
  - helper notes for turning an existing conversation into importable history

## Target Bootstrap Contract

The public framework should make these flows obvious:

1. Bootstrap a spoke in another project.
2. Bootstrap a hub in another project.
3. Keep the framework clone itself as a local fork and evolve the framework there.

Teachings should remain first-class inputs to bootstrap so the path between framework behavior and distributable teachings stays visible.

## Temporary Guidance

Until the bootstrap redesign lands:

- use this folder as the source of migration work, not as a finalized API
- do not assume this repo contains a live public `WAI-Spoke/`
- treat node runtime data as something created in the target spoke or hub project

## Minimal Capture Mode

If you are starting from a plain chat session without a full local setup:

1. Open this README and `WAI-Minimal.template.md`.
2. Fill the template for the project in one file.
3. Save the result as `WAI-Minimal.md`.
4. After creating a real spoke, place it under that spoke's ingest path and process it through the normal workflow.

## Rule

Bootstrap should create node state. The framework repo should ship the assets that make that possible.
