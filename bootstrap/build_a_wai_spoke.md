# Build a WAI Spoke

Manual spoke bootstrap notes for the public framework remodel.

This document is transitional. It describes the intended spoke outcome, but the bootstrap contract is being redesigned so a framework clone can create a spoke cleanly without relying on a live in-repo dogfood setup.

## Goal

Create a spoke in another project directory.

The spoke owns:

- `WAI-Spoke/`
- session history
- lugs
- runtime artifacts
- local AI integration files

The public framework repo should only provide the assets and bootstrap flow that create that state.

## Minimum Spoke Shape

At minimum, a spoke needs:

```text
WAI-Spoke/
  WAI-State.json
  WAI-Lugs.jsonl
  seed/ingest/
  lugs/incoming/
  lugs/outgoing/
```

Depending on the bootstrap path, it may also create:

- session directories
- processed ingest directories
- AI instruction files such as `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`
- helper scripts and hooks

## Transitional Manual Outline

If you need to assemble a spoke by hand while the new bootstrap is being built:

1. Create the target project directory and ensure it has git if you want the spoke tracked.
2. Create the minimal `WAI-Spoke/` structure in that target project.
3. Seed `WAI-State.json` from framework templates rather than inventing ad hoc structure.
4. Create an empty `WAI-Lugs.jsonl`.
5. If you have prior chat history, stage it for ingest using the capture guidance in this folder.
6. Add the appropriate AI instruction files for the tool you use.

## Important Boundary

Do not turn this framework repo into the spoke you are creating.

The spoke should live in its own project directory. This repo stays the clean framework upstream.

## Next Step In This Remodel

This document will be replaced by a bootstrap flow that makes these modes explicit:

1. create a spoke
2. create a hub
3. evolve the framework fork itself
