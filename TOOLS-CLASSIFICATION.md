# Tools Classification

First-pass classification of `tools/` for the public remodel.

Purpose:

- separate public framework utilities from private dogfood helpers
- identify what can move into `shared/codebase/tools/`
- identify what should stay private or be excluded from the public export

Disposition labels:

- `PUBLIC`
- `PRIVATE`
- `REVIEW`
- `EXCLUDE`

## Public Candidates

These appear to be reusable framework utilities or validation surfaces:

- `lug_utils.py`
- `wai_validate.py`
- `luci_check.py`
- `security_scan.py`
- `pre_commit_health.py`
- `migrate_lugs_to_folders.py`
- `migrate_signals_v2.py`
- `enrich_lugs.py`
- `tool_advisor.py`
- `advisor_context_refresh.py`
- `advisor_schedule_eval.py`
- `lathe_score.py`
- `score_backlog.py`
- `human_hours.py`
- `historian_scan.py`
- `tag_vibe_affinity.py`
- `closeout.sh`
- `wai-chain.sh`

Reasoning:

- they look like productized validators, migrations, scoring helpers, or framework operations
- they do not obviously depend on Mario-only identity or private repo topology by filename alone

## Likely Private Dogfood Helpers

These look tightly coupled to a live spoke or personal operating workflow:

- `generate_wakeup_brief.py`
- `generate_ozi_brief.py`
- `generate_knowme.py`
- `spoke_cleanup.py`
- `spoke_expediter.py`
- `spoke_health_check.py`
- `spoke_integrity_score.py`
- `spoke_parity_check.py`
- `model_usage_logger.py`
- `promote_brief_refinement.py`
- `knowme_prompt.md`

Reasoning:

- centered on live-spoke reporting, brief generation, parity, or personalized operating artifacts
- these may still inform the private fork strongly, but they are not clean public framework surfaces in their current form

## Needs File-Level Review

These may be public, private, or split depending on their internal dependencies:

- `compass_report.py`

Reasoning:

- the name is too generic to classify confidently from structure alone

## Exclude Immediately

- `__pycache__/`

Reasoning:

- generated local artifacts with no public value

## Recommended Next Actions

1. Read each `PUBLIC` and `PRIVATE` candidate to confirm whether path and data dependencies match the first-pass classification.
2. Move confirmed public utilities toward `shared/codebase/tools/`.
3. Keep private dogfood helpers for the private fork unless they are deliberately generalized.
4. Remove generated artifacts from the public remodel without ceremony.
