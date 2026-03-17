

## [2.0.38] - 2026-03-16

### Added
- **`open_type` field on track points** (`epic-open-type-field-v1`) — `open[]` items in track-encapsulation.yaml now support both string (legacy) and object `{text, type}` formats via `oneOf` schema. Types: `unknown`, `deferred`, `intentional`, `blocked`. Historian pattern-scan filters `intentional`/`deferred` items unless they recur in 6+ distinct sessions.
- **`open_type_overrides` config** in historian.yaml — declarative config block for filtered types, override threshold, and passthrough types.
- 3 new tests across both skill files (2 in track-encapsulation, 1 in historian)

---

## [2.0.37] - 2026-03-16

### Added
- **3 teaching files** for hub distribution: `wai-step3a-path-split-v1` (Path A/B + duplicate check in Step 3a), `wai-closeout-step9b-sender-v1` (sender filename + idempotency in Step 9b), `wai-shipit-release-tag-v1` (Step 0 production intent + Step 9b release tag)
- **Shipit Step 1 auto-syncs `templates/spoke/commands/`** alongside `.claude/commands/` — resolves vector-03 (3-file manual sync workaround, 7 of 12 sessions). Single source in `templates/commands/` now propagates to all 3 destinations automatically on every shipit.
- Spoke templates (`templates/spoke/commands/`) and `.claude/commands/` synced to current framework versions

---

## [2.0.36] - 2026-03-16

### Added
- **Teaching adoption Path A/B split** in `wai.md` Step 3a — `safe_to_auto_adopt: true` teachings now use Path A: compact table (Affects / Implication / Challenge Solved) + direct adopt + duplicate check. `safe_to_auto_adopt: false` retains full mailroom ceremony (Path B).
- **Duplicate check** in `wai.md` Step 3a Path A — before appending a signal teaching, checks for existing entry by `timestamp` in `WAI-Signals.jsonl`. Validated live: correctly skipped two already-present signals.
- **Sender in signal filename** — `wai-closeout.md` Step 9b now generates `signal-YYYYMMDD-HHMM-from-{spoke_id}.md.teaching`. Sender spoke_id derived from `wheel.name` (lowercased, spaces → hyphens).

---

## [2.0.35] - 2026-03-16

### Added
- **WAI-Challenges.jsonl** — new first-class append-only file for problem-centric backlog. Stores stable challenge statements independently of idea lugs. Schema: `i`, `ty`, `statement`, `first_seen`, `first_seen_in`, `status`, `related_lugs`, `resolution_notes`. First entry: `chal-shipit-release-vs-checkpoint`.
- **`/wai-improve` Step 3b: Challenge Matching** — after refinement, matches intake challenge against `WAI-Challenges.jsonl` using Jaccard similarity (threshold 0.5, Porter stemming). Proposes new challenge with implicit consent or links to existing. Sets `challenge_id` on idea lug.
- **`challenge_id` field** on idea lug schema (Step 5) and required fields list. Links ideas to their stable challenge anchor.
- **`WAI-Challenges.jsonl` documented** in `wai-lug-advisor.md` — schema, lifecycle, relationship to ideas, type catalog row.
- **Shipit Step 0: Production Release Intent** — asks "Is this a production release?" before any other step. Records intent for Step 9b.
- **Shipit Step 9b: Apply Release Tag** — conditional on Step 0 answer. Applies `git tag v{version}` + push after closeout. Skipped for progress saves. Conflict guard: stops if tag already exists.
- **`activity_filter_exclude`** in `historian.yaml` `pattern_scan` — 22-token blocklist filters protocol-routine activity phrases (`committed`, `updated`, `copied`, etc.) before Jaccard similarity scan. Fixes first-pass noise (30/40 clusters were maintenance phrases). Two new tests.

### Changed
- `wai-improve.md` execution flow diagram updated to include Step 3b.
- `wai-shipit.md` success criteria and output format updated for release tag.
- Historian vectors `vector-01` (legacy root cleanup) and `vector-02` (wai-teach outbox) resolved after investigation.

---

## [2.0.33] - 2026-03-15

### Fixed
- **CI: CRLF line endings** — 18 shell scripts converted to LF; `.gitattributes` added to enforce LF on all text files permanently
- **CI: Missing test infrastructure** — added `run-integration-tests.sh`, `tests/integration/runner.py`, `requirements.txt`, `requirements-test.txt`
- **E2E test suite drift** — `benchmarks/e2e/test_skills.py` updated to match current codebase: `idea`/`response` types, `proposed` status, `wai-teach`/`wai-learn` absorbed commands, title field optional on closed/reconciled records

---

## [2.0.32] - 2026-03-15

### Added
- **Historian pattern-scan sub-mode** — `historian.yaml` extended with `pattern_scan:` section. Runs every wakeup (incremental — only new sessions). Detects `open_recurrence` (3+ sessions), `workaround_churn` (4+ turns or 2+ sessions), `reopened_decision` (2+ sessions) using token-normalized Jaccard similarity (threshold: 0.3). Stores results in `vectors.jsonl`. Surfaces up to 3 patterns at wakeup Step 5c with investigation prompts.
- **`scan_state.json`** — new historian advisor file tracking `last_scan_session` for incremental scanning
- **vectors schema** expanded with 7 new fields: `pattern_type`, `first_seen`, `last_seen`, `occurrences`, `sample_text`, `similarity_scores`, `investigation_prompt`
- **passes_record schema** expanded with `patterns_detected` and `patterns_surfaced`
- 3 new pattern-scan tests in `historian.yaml`

### Changed
- `templates/commands/wai.md`, `.claude/commands/wai.md`, `templates/spoke/commands/wai.md`: Step 5c now includes pattern-scan run after narrative-review threshold check
- `historian.yaml`: `scope.reads` and `never_modifies` updated to flat track storage path (`sessions/track_*.jsonl`)

---

## [2.0.31] - 2026-03-15

### Changed
- **Flat session track storage** — tracks migrated from `WAI-Spoke/session-YYYYMMDD-HHMM/track.jsonl` (per-directory) to `WAI-Spoke/sessions/track_YYYYMMDD-HHMM.jsonl` (flat files). 11 existing tracks migrated.
- `framework/skills/track-encapsulation.yaml`: updated scope.writes, scope.creates, lifecycle steps, resume algorithm, backward_compat rules, tests, notes
- `templates/commands/wai.md`, `.claude/commands/wai.md`, `templates/spoke/commands/wai.md`: Steps 5a, 6, 9 updated to flat path
- `templates/commands/wai-closeout.md`, `.claude/commands/wai-closeout.md`: Step 5 track_path example + Step 6 note updated
- `teachings/spoke-wai-update-v1.md.teaching`: all session path references updated

---

## [2.0.28] - 2026-03-15

### Added
- **Step 9b: Signal Teach** — `wai-closeout.md` now automatically distributes new signals as teaching files at every closeout when hub is connected. No separate `/wai-teach` needed for signals.
- **`teachings/closeout-absorbs-signal-teach-v1.md.teaching`** — distributes updated closeout to all spokes
- **5 signal teachings** written to `teachings/` this session (impacts 8-9)
- **`/wai-improve` installed** on framework spoke from `wai-improve.md.teaching`

### Changed
- `templates/commands/wai-closeout.md`: preamble (capture `old_last_closeout`), Step 9b inserted, success criteria updated
- `decision-plan-dogfood-execute-protocol` lug: type → `core-protocol`, dogfood inputs clarified (full file content required), rejection loop added, exception clause expanded, `review_log` pattern introduced
- `taste.spoke.yaml`: Green Light asks must include challenge + value
- `WAI-Spoke/WAI-Guide.md`, `WAI-Spoke/WAI-State.md`, `examples/demo-wheel/`: WAI CLI references removed

### Fixed
- Signal distribution no longer requires a manual step after closeout

---

## [2.0.11] - 2026-03-03

### Added
- **Spoke Detection and Initialization**: `wai-teach` now auto-detects if target is a spoke
  - Detects spoke by checking for `WAI-Spoke/WAI-State.json`
  - Automatically initializes new spokes from `templates/spoke/` template
  - Configures WAI-State.json with smart defaults (directory name, git repo detection)
  - Prompts for hub path and registers spoke in hub registry
  - Enables any spoke to teach any directory - universal teach capability

### Changed
- `wai-teach.md`: Added "Spoke Detection" and "Spoke Initialization" sections
- `wai.md`: Updated skills documentation to reflect new auto-detect capability

### Fixed
- Teach protocol no longer requires manual spoke setup
- Hub registry is automatically updated when initializing new spokes

---

## [2.0.6] - 2026-02-21

### Added
- **Auto-Teach/Learn Protocol**: Automatic lug distribution integrated into closeout cycle
  - Created `wai/outbox_delivery.py` - autonomous outbox delivery module
  - Updated closeout skill with Step 1: Distribute Outbox Lugs (before state save)
  - Added delivery summary to wakeup briefing
  - Eliminates manual `/wai-teach` command requirement

- **Anti-Hallucination Validation Framework**: Pattern for preventing AI interpretation drift
  - Created signal lug with 7 required specification elements
  - Validation questions, forbidden phrases, compliance reporting
  - Ready for broadcast distribution to all spokes

- **Infrastructure Modules**:
  - `wai/scaffold.py` - Lug directory structure scaffolding for all spokes
  - `wai/framework_builder.py` - Upgrade adoption plan generation
  - Generated `upgrade-adoption-plan.json` v3.1.0 with 9 files

### Changed
- Closeout procedure now includes automatic outbox delivery as first step
- Steps 2-11 renumbered to accommodate new Step 1
- Wakeup briefing shows recent delivery summary

### Deprecated
- Manual `/wai-teach` command (archived to `wai/archive/teach.py.deprecated`)
- Teaching now automatic on closeout

### Fixed
- Teach command routing bugs resolved by new delivery architecture
- Delivery confirmations now use correct source_wheel_id
- Hub registry is authoritative source for wheel identity

### Session Stats
- Files created: 6
- Files modified: 2
- Lines of code: 959
- Lugs delivered: 2 (to hub)
- Signals extracted: 2 (impact 9-10)

\n## 2026-03-17: Session 35\n- **Epic Complete:** Implemented the full  pipeline for ingesting external AI conversations.\n- **Protocol Update:** Enhanced the  skill with a complete lifecycle and the 'Victory Briefing' announcement format.
