# Hub Content Audit

First-pass classification of the current `hub/` tree for the public remodel.

Purpose:

- separate reusable hub framework assets from stateful hub content
- define what can survive into `hub/codebase/` and `hub/teachings/`
- identify what belongs only in a real running hub

Disposition labels:

- `PUBLIC`
- `PRIVATE`
- `REVIEW`
- `EXCLUDE`

## Strong Public Candidates

- `hub/WAI-Hub/skills/WAI-Skills.jsonl`
- `hub/WAI-Hub/skills/closeout/wai-closeout.md`
- `hub/WAI-Hub/skills/hub-health-monitor/hub-health-monitor.md`
- `hub/WAI-Hub/skills/hub-knowledge-base-curator/hub-knowledge-base-curator.md`
- `hub/WAI-Hub/skills/hub-registry-verification/hub-registry-verification.md`
- `hub/WAI-Hub/skills/wai/wai.md`
- `hub/advisors/assessor/schema/SCHEMA.md`
- `hub/advisors/assessor/schema/assay-v1.0.0.json`
- `hub/advisors/assessor/schema/model-registry-v1.0.0.json`
- `hub/teachings_repo/framework/current/migration-lugs-dir-rename-v1.md.teaching`
- `hub/teachings_repo/framework/current/skill-wai-chain-load-v1.md.teaching`
- `hub/teachings_repo/framework/current/skill-wai-lug-compat-v1.md.teaching`
- `hub/teachings_repo/framework/current/teaching-automated-closeout-ceremony-v1.teaching`
- `hub/teachings_repo/framework/current/teaching-knowme-lifecycle-v1.teaching`

Reasoning:

- these look like reusable hub behavior, schemas, and distributable teachings
- they are the strongest inputs to a future `hub/codebase/` and `hub/teachings/` split

## Likely Private Or Stateful

- `hub/WAI-Ledger.jsonl`
- `hub/WAI-Lugs.jsonl`
- `hub/WAI-Lugs.jsonl.v1-backup`
- `hub/WAI-Manifest.yaml`
- `hub/health.yaml`
- `hub/registry.yaml`
- `hub/taste.user.yaml`
- `hub/machines/Sparky.lug.json`
- `hub/intake/wai-v2-migration/decision.lug.json`
- `hub/WAI-Hub/registry/incoming/wheelwright.json`

Reasoning:

- these read like live hub state, runtime registry content, backups, taste/profile data, or operational records
- they may be useful as reference while designing hub templates, but they are not clean shipped framework assets in current form

## Probably Template Or Example Material, But Needs Review

- `hub/BRIEF.md`
- `hub/WAI-Integrity.md`
- `hub/WAI-Hub/signals/README.md`
- `hub/WAI-Hub/signals/incoming/.gitkeep`
- `hub/WAI-Hub/signals/processed/.gitkeep`
- `hub/intake/.gitkeep`
- `hub/intake/processed/.gitkeep`

Reasoning:

- some of these may become documentation or skeleton template material
- `.gitkeep` files may survive only if the final public hub template truly needs empty directories committed

## Recommended Next Actions

1. Promote reusable hub skills, schemas, and teachings into explicit public ownership.
2. Convert any necessary live examples into sanitized templates instead of shipping stateful originals.
3. Remove hub runtime records, taste files, machine records, and registry state from the public export.
4. Define a minimal public hub template set before moving `hub/` into its final structure.
