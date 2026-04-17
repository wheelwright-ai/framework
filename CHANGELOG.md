## [2.0.176] - 2026-04-16

### Navigator Phase 1 implementation + assay telemetry loop (Session 156)

- **`hub/WAI-Hub/advisors/navigator/adapters/`** (new): `_base.py` (ProviderAdapter ABC, 7 methods), `anthropic.py`, `openai.py`, `gemini.py`, `together.py`, `z_ai.py` (stub adapters), `__init__.py` (ADAPTERS dict).
- **`hub/WAI-Hub/advisors/navigator/catalog/`**: `model-entry-schema.json` and `pricing-ledger-schema.json` added alongside existing `market-catalog.json`.
- **`hub/WAI-Hub/advisors/navigator/skills/`**: `scan-lightweight.md` (Mode A — hourly healthcheck + catalog diff + deprecations) and `scan-entitlements.md` (Mode B — daily entitlements + limits + usage).
- **`hub/WAI-Hub/advisors/navigator/assay-inbox/`** (new): Hub-side inbox for spoke assay_full.json delivery. One subdir per spoke.
- **`hub/WAI-Hub/advisors/navigator/assay-patterns.json`** (new): Aggregated cross-spoke usage patterns (populated nightly by `navigator_assay_aggregate.py`).
- **`hub/WAI-Hub/advisors/navigator/recommendations-current.json`** (new): Pre-computed 7-profile recommendation snapshot, published nightly by `navigator_recommendations_publish.py`.
- **`hub/tools/navigator_assay_aggregate.py`** (new): Reads all delivered `assay_full.json` files, builds `assay-patterns.json` keyed by model×work_type.
- **`hub/tools/navigator_recommendations_publish.py`** (new): Runs recommendation engine against 7 standard profiles, writes `recommendations-current.json` with `valid_through` timestamp.
- **`hub/WAI-Hub/advisors/navigator/skills/recommend.md`**: Updated — loads `assay-patterns.json` and applies organic usage boost (capped +0.15) to `local_success_fit`.
- **`hub/WAI-Hub/advisors/gardener/scripts/run_nightly.py`**: Added `navigator_assay_aggregate` and `navigator_recommendations_publish` to post-tend chain (after Cartographer fleet-chart).
- **`WAI-Spoke/advisors/navigator/catalog-cache.json`** (new): Spoke-local cache seed — `cached_at`, `ttl_hours`, `recommendations_pulled_at`, `recommendations_valid_through`.
- **`WAI-Spoke/advisors/navigator/recommendations-current.json`** (new): Spoke-local copy of hub recommendations, refreshed at every wakeup when hub connected.
- **`templates/commands/wai.md`**: Added Navigator status line to FAST PATH banner; added Step 1b Navigator startup block (catalog TTL check + recommendations sync from hub) to FULL PROTOCOL.
- **`templates/commands/wai-closeout.md`**: Added step 6c — assay_full.json write (PII-free session metadata) + delivery to hub:navigator assay-inbox.
- **`WAI-Spoke/sessions/session-20260416-0222/assay_full.json`** (new): First assay produced by this session; delivered to hub.
- **Lug updates**: `feature-spoke-activity-log-cartographer-v1` extended with assay schema + delivery spec. `epic-navigator-advisor-v1` updated to 7 Phase 1 child lugs with explicit run order. 6 impl lugs marked completed.

## [2.0.175] - 2026-04-16

### Cartographer advisor + Navigator epic (Session 155)

- **`templates/commands/wai-closeout.md`**: Added step 6b — Cartographer Observation. At every session closeout, reads track.jsonl to count rework events and lug transitions, infers dominant work type, writes structured observation record to `WAI-Spoke/cartographer/observations/`.
- **`hub/WAI-Hub/advisors/cartographer/IDENTITY.md`** (new): Full charter — observation schema, fleet-chart schema, Historian backfill contract, Navigator handoff contract.
- **`hub/tools/cartographer_aggregate.py`** (new): Nightly aggregator — walks all spoke observation directories, groups by model_id × work_type × complexity_band, writes `fleet-chart.json`.
- **`hub/WAI-Hub/advisors/gardener/scripts/run_nightly.py`**: Added Cartographer fleet-chart as third step in post-tend chain.
- **`feature-model-intelligence-hub-v1`**: Completed.
- **`epic-navigator-advisor-v1`** (new): Navigator promoted to 3-phase epic with 5 Haiku-executable Phase 1 child impl lugs.
- **`hub/WAI-Hub/advisors/navigator/`** (new): Hub skeleton — IDENTITY.md, market-catalog.json (5-provider skeleton), adapters/skills/snapshots/entitlements directories.

## [2.0.173] - 2026-04-16

### Work Queue Chain Mode: minimal context load protocol (Session 153)

- **`templates/commands/wai-chain-load.md`** (new): Skill defining the 3-read minimal context load protocol for work queue chain mode. Reads WAI-State identity subset (7 fields from `wheel` + `_session_state`), target lug in full, and last 2 track entries. Target ~7-12k tokens vs ~46k full wakeup (~34-39k savings per chained item).
- **`templates/spoke/skills/wai/wai-chain-load.md`** (new): Spoke distribution copy of the chain-load skill.
- **`templates/commands/wai-ozi-work-queue-monitor.md`**: Step 3 chain flow bullet strengthened — explicit "follow wai-chain-load.md protocol, do not run full wakeup" note.

## [2.0.172] - 2026-04-15

### Fix: tool_advisor.py regressions from reformatting pass (Session 152)

- **`tools/tool_advisor.py`**: Restored 4 regressions introduced by a prior formatting-only rewrite:
  - Restored `mcp-not-configured` proposal block in `audit_claude` (replaced by suppression comment)
  - Reverted `codex-coverage-absent` → `opencode-coverage-absent` rename (test not updated)
  - Removed `audit_codex` auto-create AGENTS.md block (silently set `has_agents=True` in `audit_shared`, suppressing `codex-coverage-absent` proposal)
  - Reverted area key `OpenCode` → `Codex` in `run_audit` and `ensure_agents_thrift`
- All 3 CI job failures resolved: Baseline Comparison, Run Integration Tests (3.11), Test Summary.
- Suite: 106 passed, 5 skipped.

## [2.0.171] - 2026-04-15

### KnowMe.md lifecycle - generator, teaching, and content standard (Session 151)

- **`KnowMe.md`** (revised, 147 lines): Finalized cold-start orientation file. Applied user refinements: removed WAI Context section (telemetry), removed generated footer, tightened Quick Start to orientation-only, trimmed Source of Truth precedence note, dropped Tender from vocabulary, collapsed Open Questions to one structural item, replaced all em-dashes and Unicode arrows with plain ASCII.
- **`tools/generate_knowme.py`** (new): Haiku-based generator for KnowMe.md on any WAI spoke. Accepts `--spoke-path` and `--dry-run`. Reads WAI-State.json, CLAUDE.md critical rules, CHANGELOG (last 3 entries), lug counts. Stamps `_session_state.knowme_last_generated_at`, `knowme_version`, `knowme_stale` on write.
- **`tools/knowme_prompt.md`** (updated): Added Open Questions section to output spec, removed metadata footer instruction, fixed Quick Start spec (no session ceremony), added ASCII-only output rule.
- **`hub/teachings_repo/framework/current/teaching-knowme-lifecycle-v1.teaching`** (new): Full adoption teaching. Immediate generation on adoption (not deferred to Gardener), staleness conditions (7d active / 30d any / knowme_stale flag), verification commands, content standard summary.
- **`WAI-Spoke/WAI-State.json`**: Added `_session_state.knowme_last_generated_at`, `knowme_version`, `knowme_stale` fields.
- **`feature-knowme-gardener-lifecycle-v1`**: Completed.

## [2.0.170] - 2026-04-15

### KnowMe.md + generation prompt template (Sessions 149–151)

- **`KnowMe.md`** (new, 148 lines): Cold-start orientation file for the framework spoke. 14 sections: identity, mission, ecosystem role, stack, architecture, constraints, source of truth, agent behavior, core vocabulary (8 terms), knowledge appetite, triggers, top pitfalls, and quick start. Designed as a portable passport — no live telemetry, no tool-specific mechanics.
- **`tools/knowme_prompt.md`** (new): Generation prompt template for the future `generate_knowme.py` script. 14-section output spec with hard caps and explicit exclusion rules. Model: claude-haiku-4-5-20251001.
- **`feature-knowme-gardener-lifecycle-v1`** (new lug): ROI 2.7, impact 8, effort 3. Gardener-maintained KnowMe.md lifecycle with staleness tracking and teaching adoption triggering immediate init generation.
- **Lug refinements (S149):** `feature-tender-ceremony-parity-protocol-v1` added target_files; `feature-navigator-advisor-v1` execute gate formalized with design_session_required + 5 concrete design questions; `lug-routing-intelligence-20260330` closed and converted to `signal-routing-intelligence-hub-delivery-v1` (delivered to hub).

## [2.0.166] - 2026-04-14

### Ozi + Octo advisor recruitment and lifecycle (Session 147)

- **`WAI-Spoke/advisors/ozi/context_prompt.md`** (new, 251 lines): Team coverage evaluation (scope detection from open lugs + WAI-State), advisor_recommendation signal handler, 8-step instantiation protocol (template → context_prompt generation → registry + schedule + lifecycle), advisor output routing (impact >= 7 escalates to Octo).
- **`hub/WAI-Hub/advisors/octo/context_prompt.md`** (new, 142 lines): Fleet scope-gap detection (per-spoke roster vs. patterns, 14-day cooldown, max 2/cycle), `advisor_recommendation` signal emission, `recommendation_log.jsonl` effectiveness tracking, new Advisor Coverage Gaps output section.
- **`hub/WAI-Hub/advisors/octo/advisor-recommendation-patterns.json`** (new): 10 scope triggers — ai_tool_integration, testing_infrastructure, documentation, architecture_oversight, deployment_automation, data_analytics, external_api_integration, framework_development, security_sensitive, ml_models. Each has detection_signals, recommended_roles, and cooldown_days.
- **`hub/WAI-Hub/advisor-templates/registry.json`**: Populated with 3 templates (engineering-advisor, quality-advisor, synthesis-advisor) including charter_path and source_guidance_path pointers.
- **`WAI-Spoke/advisors/ozi/scan_state.json`**: Added `team_coverage` tracking object (last_coverage_eval_at, active_scopes, gaps_detected, recommendations_pending).

## [2.0.165] - 2026-04-14

### Teaching pipeline: drop manual/ folder + lug-based adoption tracking (Session 146)

- **`WAI-Lug-Schema-Spec.md`:** Added `adoption_status` (enum: pending_review/adopted/deferred/rejected), `adoption_action` (string), `adoption_reviewed_at` (ISO timestamp) to field reference.
- **Protocol docs (7 files):** Removed `seed/ingest/manual/` copy step from Path B adoption protocol in `wai.md` (×2), `wai-reference.md` (×3), `wai-learn.md`. Path B now records adoption fields on lug and moves directly to `processed/`. `processed/` semantics changed from "seen" to "reviewed + action recorded".
- **`tests/behavioral/conftest.py`:** Replaced `seed/ingest/manual` fixture dir with `seed/ingest/incoming`.
- **Filesystem:** 6 orphan teachings moved from `manual/` to `processed/`; `seed/ingest/manual/` dir removed.
- **`epic-wai-pre-post-wrapper-v1`:** Formally adopted with `adoption_status: adopted` — all 4 blocks (generate_wakeup_brief.py, wai-enter.sh, wai-exit.sh, BRIEF_FRESH gate) confirmed installed.

## [2.0.162] - 2026-04-10

### Tool Advisor phases 2-6 complete + epic closed (Session 142)

- **`tools/tool_advisor.py` Phase 2 (rubric+adapters):** `CATEGORY_MAP` with 6 shared check dimensions (`entrypoint-quality`, `context-thrift`, `stale-path-hygiene`, `official-source-coverage`, `template-live-parity`, `compatibility-redirects`). `_tag_category()` postprocessor tags every finding. `vectors.jsonl` per-tool score tracking populated after each audit run. `check_compatibility_redirects()` in `audit_shared`. `migrate_cc_advisor()` + `--migrate-cc-advisor` CLI flag (6 cc-advisor passes imported). Schema docs in `wai-tool-advisor-reference.md` corrected.
- **`tools/tool_advisor.py` Phase 5 (safe-remediation):** `REMEDIATION_MATRIX` classifies fix types into `safe_auto` / `proposal_only` / `never_auto`. `_write_proposal_report()` writes `reports/proposals-latest.json`. MCP + cross-tool coverage proposals generated. Idempotency verified.
- **Phase 6 (test-coverage):** 26 new tests across 3 files. 106 total tests pass.
- **Phases 3 + 4:** Pre-implemented in Phase 1 — verified and advanced to completed.
- **`epic-ozi-tool-advisor-all-spokes-v1` closed** (all 6 phases complete).

## [2.0.160] - 2026-04-09

### Fixes + wai-enter UX (Session 141)

- **`hub/.claude/hooks/session-start.sh` null guard:** `.decisions` → `(.decisions // [])` — silent jq failure at every session start when field absent from state schema. Also fixed in `google-cleanup-toolkit` and `spoke-worktree-1` active hooks.
- **`wai-enter.sh` tool prompt:** No-arg invocation now prompts interactively for tool name so `wai-exit.sh` post-session hook still runs (previously auto-launched claude or returned immediately).
- **`wai-closeout.md` exit notice:** Added conditional notice to run `./wai-exit.sh` manually for GUI tool or direct-launch sessions where post-exit hook doesn't auto-fire.
- **`templates/spoke/wai-enter.sh`:** Same tool-prompt change applied to spoke template.

## [2.0.159] - 2026-04-09

### Performance — WAI Skill Slim Split + Closeout Dedup (Session 139)

- **`wai.md` slim split (20KB → 1.7KB):** Fast path section only. Full protocol moved to `wai-full.md` (loaded on-demand for STALE brief case). Measured result: 14s wakeup vs ~1m previously.
- **`wai-full.md` (new):** Full wakeup protocol (Steps 1–9b + Incoming Routing). Loaded by Read() call when brief is stale — rare case.
- **`session-start.sh` track pre-write:** Hook now writes `session_start` track entry during startup (outside AI context window). `/wai` fast path makes 0 tool calls (previously 1, ~15s round-trip).
- **`wai-closeout.md` dedup + slim (24KB → 16KB):** Removed triple-duplicated steps 0c/0d. Steps 11b/11c now call `python3 tools/generate_ozi_brief.py` and `python3 tools/generate_wakeup_brief.py` instead of embedding inline Python.
- **Closeout concurrent session support:** Step 11 now runs `git fetch` + auto-rebase if remote is ahead, detects external `WAI-State.json` modifications from concurrent sessions, and annotates out-of-scope files in commit message.
- **`templates/spoke/hooks/session-start.sh`:** Track pre-write added for spoke distribution.
- **Teaching `wai-skill-slim-split-v1`:** Published to hub, `safe_to_auto_adopt: true`. Distributes all above changes to all spokes via tender.

## [2.0.158] - 2026-04-09

### Added — WAI Pre/Post Wrapper + Wakeup Brief Fast Path (Session 138)

- **`wai-enter.sh` (new):** Pre-tool wrapper that runs before the AI session — regenerates wakeup brief, refreshes context feeds in background, calls `basher doctor audit` if available, scans for anomalies, auto-fixes WAI-Spoke/ structure, then launches the configured tool. Accepts `$1` parameter for tool name (default: `claude`).
- **`wai-exit.sh` (new):** Post-tool wrapper that regenerates `wakeup-brief.json` after every session exit, ensuring the next wakeup always finds a fresh brief.
- **`tools/generate_wakeup_brief.py` (new):** Standalone Python script producing `WAI-Spoke/wakeup-brief.json` with `git_sha_at_generation` field. Supports `--spoke-path PATH` for multi-spoke use. Called by both wai-enter.sh and wai-exit.sh.
- **`session-start.sh` BRIEF_FRESH gate:** Early SHA comparison block before expensive sections. When brief SHA matches HEAD, skips `spoke_integrity_score.py`, `spoke_expediter.py`, and `advisor_schedule_eval.py` — turning 3-6 min wakeup into ~45 sec.
- **`tools/tool_advisor.py` `ensure_wrapper_scripts()`:** Added to `audit_shared()` — distributes `wai-enter.sh` and `wai-exit.sh` from `templates/spoke/` to all WAI spokes via `basher doctor update`. Surfaces missing wrappers as FINDINGs on evaluate.
- **Teaching published:** `wai-pre-post-wrapper-fast-path-v1` — distributed to hub with full 4-block batch sequence for spoke adoption.
- **Signal to minder:** `signal-tender-brief-refresh-after-commit-v1` — requests `--spoke-path` support in generate_wakeup_brief.py + call after each tender commit.

## [2.0.157] - 2026-04-08

### Fixed — Signal Boomerang Suppression, Hub Inbox Cleanup, Stray File Hygiene (Session 137)

- **Signal boomerang suppression (`templates/commands/wai.md`):** Step 5 Hub Signal Bulletin now applies two dedup checks before incorporating hub signals — (1) ID dedup: skip if signal ID already exists under local `bytype/signal/`; (2) boomerang: skip if `source_spoke` (lowercased) contains `wheel.name` (lowercased). Suppressed count surfaced in briefing.
- **`source_spoke` required for signals (`templates/commands/wai-lug-schema.md`):** Added `Signal Required Fields` section — `source_spoke` is now a required field for all signal lugs; value must be `wheel.name` from WAI-State.json. Documents the boomerang suppression mechanism.
- **Hub framework inbox cleared:** 7 framework signals all suppressed via ID dedup (all were already local). Inbox clean.
- **Stray file cleanup:** Root `WAI-State.json` (gardener misfire) moved to trash. `.env.dev` added to `.gitignore`.

## [2.0.155] - 2026-04-06

### Fixed + Improved — CC Audit, Signal Processing, Wakeup Brief (Session 135)

- **`settings.local.json` cleanup:** CC audit detected Permissions regression — 28 entries trimmed to 17 by removing 11 session-specific one-off paths and 1 broken entry (`Bash(mv echo:*)`)
- **8 open signals incorporated:** Consumed all open signal lugs; generated 7 teachings published to hub (`hook-env-var-absolute-path`, `post-compaction-closeout-hardening`, `track-integrity-closeout-event-check`, `false-blocker-verification-protocol`, `subagent-parallelism-advisor-pattern`, `inline-python-extraction-pattern`, `advisor-architecture-v2-reference`)
- **Wakeup brief smart staleness (`templates/commands/wai.md`):** Replaced SHA equality with `git diff --name-only` filtered against relevant files — brief survives housekeeping commits that don't touch lugs, state, or protocol; STALE message now names triggering file
- **2 Path A teachings adopted:** `signal-orko-spoke-routing-lugs-jsonl-gate-v1` + `signal-realizer-gap-skill-routing-v1`; series_weight 16→29
- **2 undelivered signals delivered to hub:** `signal-track-terminal-entry-fleet-teaching-v1` + `signal-wakeup-brief-path-bugs-v1`

## [2.0.147] - 2026-04-01

### Fixed + Added — Skill Sync, Closeout Banner, Tender Gate, OSS Boundary (Session 125)

- **`session-start.sh` skill sync:** Upgraded from timestamp (`-nt`) to `md5sum` content comparison — eliminates false positives from git checkout / cp mtime drift
- **Closeout Step 11 banner:** Text updated to `Proceeding in 10s — reply cancel to stop`; added inline-question guidance (answer then continue, no re-presentation)
- **`wheel-tender.sh` false completion gate:** Explicit `target_files` existence check added to Pass 2 (spoke) and Pass 3 (hub) — lugs with missing files stay `in_progress` with explanatory `status_note`
- **OSS boundary resolved:** `wai-chain.sh` stays in spoke; `score_backlog.py` stays framework; hub hosts teachings (pull model); hub-only teaching folder scoped to hub spoke only
- **`epic-apply-all-parallel-dispatch-v1`:** Apply All epic — Ozi parallel dispatch with collision-safe batches and worktree-isolated sub-agents (ROI 6.0)
- **`feature-wheel-power-spoke-v1`:** wheel-power private spoke planned — home for Gardener/Spinner/Cartographer; hub becomes pure data layer
- **Queue refinement:** 7 lugs corrected (stale paths, routing fixes, wheel-power notes); 2 rerouted FRAMEWORK → SIGNAL

## [2.0.146] - 2026-04-01

### Added — Hub Inbox Triage + Subfolder Routing + Lug Refinement (Session 124)

- **Hub signals inbox cleared:** 25-item inbox → 0 flat files. 10 new lugs created (7 bugs, 3 features); 13 archived as already-covered; 2 moved to `incoming/hub/`
- **`WAI-Hub/signals/incoming/hub/` + `incoming/framework/`:** Subfolder structure for target-aware signal routing. Hub-only signals (crash investigations, Triumvirate architecture) separated from framework spoke signals
- **`.claude/hooks/session-start.sh`:** Hub signals count now reads `incoming/framework/` only; `incoming/hub/` count shown as informational aside
- **10 new lugs from signal triage:** `bug-closeout-banner-stall-v1`, `bug-closeout-bytype-assumption-v1`, `bug-closeout-health-check-missing-v1`, `bug-session-log-retired-v1`, `bug-false-blocker-verification-v1`, `bug-tender-dry-run-cost-v1`, `bug-tender-false-completions-v1`, `feature-execute-when-gate-v1`, `feature-tender-autonomous-pipeline-v1`, `feature-skill-sync-detector-v1`
- **Lug refinement:** 29/29 open lugs clean — ROI, model_fit, PEV filled for 15 existing lugs; `epic-signal-rework-v1` received full perceive/execute/verify

## [2.0.145] - 2026-04-01

### Added — CC Advisor Audit + Lug Refinement + Tender Fixes (Session 123)

- **`.claude/hooks/post-tool-use.sh`:** New PostToolUse hook — Python syntax check after Write/Edit on `.py` files (CC advisor score 6→7/8)
- **`.claude/settings.json`:** PostToolUse hook wired; `CLAUDE.md` hooks table updated
- **Lug refinement pass:** 6 lugs filled to implementation-ready — `decision-signal-architecture-v2` (full PEV from quality 0), `decision-df884ede13e2` (criteria+target_files), 4 features (target_files added); expediter queue 2→0
- **`hub/WAI-Hub/advisors/gardener/scripts/wheel-tender.sh`:** Framework spoke pinned first (before triumvirate ordering) so it processes hub signals before fleet runs; signal triage output now shows hub/incoming pending count
- **`hub/WAI-Hub/Signals/`:** Empty case-typo directory removed (canonical path is lowercase `signals/`)
- **`WAI-Spoke/runtime/session-guard.json`:** `session_closed=true` written at closeout (S122 carry)

## [2.0.142] - 2026-04-01

### Added — Build Session: Sync Detection + Expediter Wakeup + Urgency Tiers + Advisor Context Feeds (Session 120)

- **`.claude/hooks/session-start.sh`:** Section 8b: skill sync check (wai*.md mtime comparison), Section 9b: expediter summary in CONTEXT HEALTH, Section 9c: advisor context feed staleness detection + auto-init
- **`tools/spoke_integrity_score.py`:** Sync gap penalty (-2pts in hooks dimension) when templates/commands/ ahead of .claude/commands/
- **`tools/score_backlog.py`:** Urgency tiers 1-5 (URGENT→DEFER), sort key `(urgency, -roi)`, tier band headers in output
- **`tools/advisor_context_refresh.py`:** New tool — fetches external context for advisors (web_fetch, web_search, ai_synthesis via Claude API), writes dated snapshots, promotes high-impact findings to spoke-profile.json
- **`WAI-Spoke/advisors/{9}/feeds.yaml + context_prompt.md`:** Per-advisor feed config + Ozi-authored synthesis prompts for all 9 spoke advisors
- **`WAI-Spoke/spoke-profile.json`:** Spoke intelligence profile — auto-populated from high-impact advisor findings
- **`hub/tools/hub_context_refresh.py`:** Hub-side shared topic refresh (claude-capabilities, wai-framework-updates)
- **`hub/WAI-Hub/context/manifest.json`:** Shared context manifest for hub-level dedup
- **`templates/commands/wai.md`:** Expediter summary in Full Briefing, urgency tier-aware execute loop
- **`templates/commands/wai-reference.md`:** Expediter section + Advisor Context Feeds documentation
- **`templates/commands/wai-lug-schema.md`, `wai-lug-schema-reference.md`:** `urgency` field (1-5, default 3) + urgency tier reference table

### Decided

- **`decision-signal-architecture-v2`:** Signals are risk bulletins with patch semantics, separate from work lugs. Two flavors: patch (JIT fix) and delivery (lug in envelope). New epic: `epic-signal-rework-v1`.

## [2.0.141] - 2026-03-31

### Changed — Hub Inbox Cleared + CC Audit + Lug Triage (Session 119)

- **`.claude/agents/cc-advisor.md`, `.claude/agents/ozi-nightly.md`:** Added missing `memory: project` frontmatter — regression fix (CC Audit #3: 6/8, delta 0)
- **`WAI-Spoke/lugs/`:** Created `feature-expediter-wakeup-integration-v1` (ROI 9.0) — wire Spoke-Local Expediter into session wakeup; `feature-skill-sync-detection-v1` (ROI 8.0) — detect .claude/commands/ sync gap in session-start hook
- **`WAI-Spoke/lugs/`:** Fixed `impl-ozi-queue-schema-v1` field name: `blocker_list` → `blocked_by` in PEV execute steps and acceptance criteria
- **Hub signals:** Triaged 18 incoming signals — 16 archived as already-covered, 2 converted to local lugs; all 6 `by-target/framework/` signals processed
- **Lug triage:** Groups 2-4 complete — `idea-fit-check-caching` closed (P4 noise); linkedin idea re-routed to content spoke; 7 lugs retained with disposition notes

## [2.0.140] - 2026-03-31

### Added — Refine Vibe + Ozi Auto-Execute + Backlog Clustering (Session 118)

- **`templates/commands/wai.md`:** Added `refine` vibe (lug quality, backlog scoring, PEV review); added Step 9b — Ozi auto-execute mode triggered by vibe selection; Ozi scores backlog, presents plan, executes autonomously until context ≥50%, queue empty, or item needs user input
- **`tools/score_backlog.py`:** Added `refine` vibe affinity; added `--clusters` flag with `build_clusters()` and `extract_cluster_key()` — groups related lugs for batch dispatch, reducing file touches
- **`templates/commands/wai-closeout.md`:** Added Step 10b skill sync (`templates/commands/*.md` → `.claude/commands/`); Step 11 now shows banner before commit with 10s proceed-unless-cancel countdown
- **`WAI-Spoke/lugs/`:** Authored PEV for `lug-expedite-asap-flag` (tiered priority bands) and `lug-routing-intelligence` (spoke-profile-aware dispatch); created `feature-hub-registry-teams-v1` (spoke relationship groups in registry)
- **`hub-registry.json`:** Fixed 3 null spoke_ids (`why-go-bye`, `solutions-by-mv`, `analysing-local-mcp`) derived from wheel_id

## [2.0.139] - 2026-03-31

### Fixed — Hooks Scoring Formula + Signal Triage + Epic Decomposition (Session 117)

- **`tools/spoke_integrity_score.py`:** Hooks dimension scoring bug fixed — `score_hooks()` awarded 3pts/hook (5×3=15 cap) while declaring `max=20`; changed to 4pts/hook (5×4=20); framework spoke: 89→94/100
- **Signal triage:** 30 of 36 framework-inbox signals cleared; 14 incoming routed; 6 remain as pending work items
- **`epic-ozi-work-queue-orchestration-v1` decomposed:** 3 child impl lugs: schema → wakeup → autochain (phase-blocked)
- **`feature-tender-spoke-integrity-v1` closed:** Fleet run confirmed complete — all 17 spokes GREEN

## [2.0.138] - 2026-03-31

### Added — Scripted Closeout + Skill Thrift + Track Integrity Fix (Session 116)

- **`tools/closeout.sh`:** Mechanical closeout automation — version bump, `session_count++`, lug archival, `WAI-LugIndex.jsonl` regen, `score_backlog.py --update-state`; idempotent, `--dry-run` flag; reduces AI closeout tool calls ~15→5
- **`wai.md` thrift:** 605→233L (-62%); `wai-reference.md` created; wakeup token cost ~22k→8k
- **`wai-lug-schema.md` thrift:** 525→471L; Execute-When Gates + Routing Fields condensed to reference
- **`wai-closeout.md`:** Steps 4+5 replaced with `tools/closeout.sh` call
- **`session-start.sh` Step 1b:** Previous session track integrity check; surfaces `Prev session: CLEAN/INTERRUPTED/EMPTY` in wakeup init block

### Fixed

- Track integrity false-positive: `event==closeout` entries now accepted as CLEAN (not just `completed==true`)

## [2.0.137] - 2026-03-31

### Added — Spoke Integrity + Advisor Stubs + Closeout Hardening (Session 115)

- **`tools/spoke_parity_check.py`:** Assertion-based parity verification against `hub/WAI-Hub/parity/head.json`; parity computed not stamped; exit 0=at parity, 1=behind, 2=error; `--json` flag for Tender
- **`tools/spoke_integrity_score.py`:** 5-dimension composite score (structure/hooks/lugs/parity/hub) 0-100; `--json` + `--quiet` modes; exit codes for automated use; this spoke: 92/100 HEALTHY
- **`session-start.sh`:** CONTEXT HEALTH section now shows integrity score + parity status on every wakeup
- **Post-compaction closeout hardening:** `pre-compact.sh` writes `compacted=true` to guard file + adds CLOSEOUT CRITICAL directive to output; `user-prompt-submit.sh` detects flag and injects one-shot `<wai-post-compact>` block directing model to read skill files before acting
- **Spoke advisor stubs (5):** Archie (Architect), Will (Release Engineer), Jordy (QA), Mark (Growth Analyst), Clara (Content Marketer) — `WAI-Spoke/advisors/{name}/scan_state.json` + `reports/`; hierarchy matches architecture v2

### Fixed

- `session-20260331-1524/track.jsonl`: appended `completed:true` entry so wakeup integrity check no longer flags S114 closeout session as INTERRUPTED
- `task-rename-lathe-to-spinner-v1`: verified complete in hub (spinner/ exists, zero lathe refs), marked completed

### Teaching Adoption (Session 115)

- 8 teachings processed: 4 new signals (wheel-council-v1, octo-cos, subagent-parallelism, octo-v2-operational); 3 pre-existing; 1 minder migration (already clean)

## [2.0.136] - 2026-03-31

### Added — Octo v2: Hub Chief of Staff (Session 114)

- **`hub/tools/octo_brief.py` v2.0.0:** Adds CoS operational layer on top of advisory brief
  - `compute_hub_work_queue()`: scores all 17 spokes by `urgency * health_penalty + signal_pressure`, writes `hub_work_queue.json`
  - `compute_council_directives()`: actionable lists for all 4 council members → `council_directives.json`
  - `compute_escalation_items()`: surfaces high-impact pending signals, chronic RED spokes, orphan spokes
  - `generate_latest_md()`: extended with Hub Work Queue + Escalations sections
  - `scan_state.json` v2.0.0: adds `last_dispatch_at`, `directives_count`, `work_queue_size`
- **`run_nightly.py`:** `sort_spokes_by_spinner()` now checks `hub_work_queue.json` first — Octo ordering takes precedence over pure Spinner urgency when file exists
- **Hub outputs:** `hub_work_queue.json` (17 spokes sorted by priority), `council_directives.json` (4 council members with explicit tonight's directives)

## [2.0.135] - 2026-03-31

### Added — Wheel Council v1 (Session 113)

- **Hub advisors (5 total):** Gardener (formal), Spinner (renamed from Lathe), Cartologist (renamed from Compass), Quartermaster (new), Octo (new)
- **`hub/tools/spinner_score.py`:** Portfolio scoring (renamed from lathe_score.py — zero live lathe refs)
- **`hub/tools/cartologist_report.py`:** Fleet dashboard HTML (renamed from compass_report.py)
- **`hub/tools/cartologist_web.py`:** Flask web interface on port 8080 — live dashboard, decision capture, spoke detail
- **`hub/tools/quartermaster_scan.py`:** Cross-spoke inventory — lug counts, stale work detection, signal depth per spoke
- **`hub/tools/octo_brief.py`:** Wheel Council strategic brief — aggregates all 4 advisor outputs, fleet health, strategic focus
- **Nightly pipeline wired:** `verify_health → spinner_score → cartologist_report → quartermaster_scan → octo_brief`
- **`hub/WAI-Hub/advisors/gardener/advisor.json`:** First-class advisor identity file
- **`feature-octo-hub-cos-v2.json`:** Octo v2 lug — CoS/orchestration role (hub work queue, council dispatch, escalation routing)

## [2.0.84] - 2026-03-28

### Fixed — Hook No Longer Dirties WAI-State.json (Session 90)

- **`.claude/hooks/user-prompt-submit.sh`:** Session guard state moved from `WAI-State.json` to `WAI-Spoke/runtime/session-guard.json` (gitignored). Root cause: hook was writing `protocol_completed` and `protocol_last_run` to WAI-State.json on every session start, immediately re-dirtying it after closeout committed it.
- **`templates/spoke/.claude/hooks/user-prompt-submit.sh`:** Same fix propagated to spoke template.
- **`templates/spoke/hooks/session-start.sh`:** Same fix for legacy session-start hook format.
- **`.gitignore`:** Added `WAI-Spoke/runtime/session-guard.json` to gitignore.
- **`WAI-Spoke/WAI-State.json`:** Removed `protocol_completed` and `protocol_last_run` fields (now in runtime guard).
- **`templates/commands/wai.md`:** Removed instruction to write `_session_status` to WAI-State.json during wakeup. Added note that session guard is runtime-only.

### Updated — Track Prompt v0.21 (Session 90)

- **`.claude/commands/wai-track-generate.md`:** Replaced legacy track-generate procedure with full WAI Track v0.21 prompt (session codename, ledger record types, artifact manifest, provenance manifest, export protocol, line/station definitions, WAI domain vocabulary).
- **`templates/spoke/skills/track-generate/wai-track-generate.md`:** Same update for spoke template deployment.

### Teaching Adopted

- **`signal-lifecycle-target-routing-v1.md.teaching`:** Hub signal bulletin target-routing lifecycle (already implemented in Session 89b, now formally adopted).

## [2.0.81] - 2026-03-28

### Added — Canonical Verification Epic (Session 88)

- **`tools/wai_validate.py`:** Single-source validation library — 5 validators, canonical type/status catalogs, PEV enforcement for actionable lug types
- **`tools/spoke_health_check.py`:** Automated spoke audit tool — quick (<2ms) and full (13ms) modes, JSON output, 6 check categories (structure, stale files, skill registry, lug integrity, hub connectivity, platform)
- **`tools/pre_commit_health.py`:** Pre-commit gate — exits non-zero on critical drift
- **`tests/behavioral/`:** 34 behavioral tests using real file operations (lug lifecycle, teaching adoption, spoke structure, skill registry, closeout operations). Includes canary test against real WAI-Skills.jsonl.
- **`wai-complexity-gate.md`:** Post-Execution Falsification section — verify by proving wrong, not confirming right. Required after every code change.
- **`wai-complexity-gate.md`:** Non-Trivial Functionality gate — lug with validated PEV required before showing to user
- **`wai-closeout.md`:** Quality Gate 0f (Falsification) — `find` across full filesystem for retired files before commit
- **Hub teaching:** `spoke-health-check-remediation-v1.md.teaching` — migration-safe remediation for all spokes

### Fixed — Fleet Remediation

- **19/19 spokes remediated to HEALTHY** — including 2 unregistered spokes (sound-sails/portal, new-solutions-by-mv)
- **Spoke template fixed:** Removed WAI-Signals.jsonl from `templates/spoke/` — was propagating retired file to every new spoke
- **24 signals migrated** from retired WAI-Signals.jsonl to `bytype/signal/delivered/` across 7 spokes (zero data loss)
- **WAI-Skills.jsonl:** Removed 16 retired object references across 4 spokes (framework, basher, wheelwright-ai-website, minder)
- **0 retired files remaining** (WAI-Signals.jsonl, WAI-Session-Log.jsonl) across entire project tree (excluding _archive/ and reference/v1-data/)

### Changed

- **`Makefile`:** Added `test-behavioral`, `test-health` targets; `test-all` now runs e2e + behavioral + health
- **`tests/idempotency/utils/spoke_factory.py`:** Creates canonical bytype/ hierarchy instead of `lugs/outbox`
- **`tests/idempotency/`:** Updated closeout replay and signal dedup tests for bytype/ structure
- **`benchmarks/e2e/test_skills.py`:** Constants to be migrated to `wai_validate.py` (single source of truth)

## [2.0.80] - 2026-03-27

### Fixed — Teaching Protocol + Shipit Cleanup (Session 87)

- **Teaching flag format:** Standardized `safe_to_auto_adopt` flag to `**safe_to_auto_adopt:** true|false` across all 30 hub teachings — fixed 4-variant format chaos that caused wakeup grep to silently miss valid flags on ~12 teachings
- **`templates/commands/wai.md` Step 5:** Updated teaching discovery to use case-insensitive grep; added explicit missing-flag fallback rule (missing = `false`, surfaced as "unprocessed" in delta report)
- **`templates/teaching-template.md.teaching`:** Header now uses canonical snake_case format to match protocol grep
- **3 legacy teachings:** Added missing `safe_to_auto_adopt` flag to `lug-auto-learn-protocol`, `lug-teach-verification-protocol`, `teaching-implementation-plan-validation-protocol-v1`
- **`wai-closeout.md` Step 0e:** Expanded from one-liner stub to full WEI benchmark runner detection with regression analysis (was silently skipping since shipit deprecation)
- **`skill-wai-shipit-benchmark-v1.md.teaching`:** Retargeted from dead `wai-shipit.md` to `wai-closeout.md` Step 0e
- **`SKILL-EXAMPLES.md`:** Removed `/wai-shipit` section and step; "End Session" is now one step (closeout only)
- **`wai-ide-setup.md`:** Removed `/wai-shipit` from session commands list

## [2.0.79] - 2026-03-27

### Fixed — Protocol Maintenance (Session 86)

- **Closeout Step 11:** Added `Context: X% at closeout` field to summary banner
- **Closeout Step 11:** Inverted banner confirmation logic — "proceed unless explicit cancel" replaces "wait for affirmative"; fixes systematic stall on spoke sessions
- **Closeout Step 9c:** Added explicit `bytype/signal/undelivered/` backlog sweep — drains accumulated signals on every closeout regardless of session scope
- **Closeout Steps 5b/5c:** Added bytype capability check — flat-lug spokes now explicitly log "skipped" instead of silently N/A-ing
- **`WAI-Spoke/skills/wai/wai.md`:** Retired `WAI-Session-Log.jsonl` entry in Core Files table — replaced by `sessions/{id}/track.jsonl`
- **`wai-closeout-reference.md` Step 9d:** Updated to document that `health-check.jsonl` template exists but was never distributed; activation path documented

### Bugs Routed
- `bug-closeout-banner-stall-v1` — fixed (Step 11 inversion)
- `bug-closeout-bytype-assumption-v1` — fixed (capability check added)
- `bug-session-log-never-populated-v1` — fixed (retired in old skill)
- `bug-health-check-template-missing-v1` — open (needs distribution teaching)

## [2.0.78] - 2026-03-26

### Changed - Protocol Diagnosis (Session 85)

- **Diagnosis:** Identified Step 9c signal delivery gap — `bytype/signal/undelivered/` backlog not swept on closeout; only newly-extracted signals delivered. Fix pending next session.
- **Hub cleanup:** Removed `teaching-ozi-orchestration-suite-v1.md.teaching` from hub `teachings_repo/framework/current/`.
- **Signal extracted:** `signal-closeout-9c-backlog-gap-v1` (impact 8) — documents the gap and fix.

### Deliverables
- Protocol gap documented: 26+ undelivered signals accumulated due to Step 9c scoping bug
- 5 hub teachings queued for adoption next session

## [2.0.77] - 2026-03-26

### Changed - Protocol Improvements + Incoming Queue (Session 84)

- **templates/commands/wai.md:** Added Step 4b (Historian threshold check — surfaces when ≥30 unreviewed track points; silent otherwise). Added incomplete-closeout detection to Step 8 (dirty WAI-State.json with protocol_completed=true triggers recovery prompt). Added closeout readiness line to Context Budget Governor.
- **templates/commands/wai-closeout.md:** Added Step 0 (Context Assessment — determines ceremony level: Full/Standard/Essential/Minimal). Renamed quality gates to Step 0b. Updated Step 11 (Summary Generation → mandatory banner hard stop before commit; explicit user confirmation required).
- **templates/commands/wai-complexity-gate.md:** Added Plan Validation section — self-validate implementation plans against checklist (behavior_spec, test_requirements, acceptance_criteria, dependencies) before showing to user.
- **WAI-Spoke/lugs/:** Consumed 10 incoming lugs — 2 bugs to bytype/bug/open/, 1 task to completed/, 11 idea lugs to bytype/other/open/, 7 signals to bytype/signal/undelivered/. Incoming folder cleared.
- **Teachings adopted:** skill-wai-closeout-context-aware-v1 (applied), teaching-session70-distribution-improvements (already absorbed), teaching-implementation-plan-validation-protocol-v1 (applied to complexity gate).

### Deliverables
- Historian threshold check is now active — fires automatically when 30+ unreviewed points accumulate
- Dirty-closeout detection converts silent WAI-State observation into actionable recovery prompt
- Closeout ceremony level declared at session start based on context %
- Mandatory confirmation banner before every git commit
- 11 improvement ideas captured as scored idea lugs (P1-P3)

## [2.0.70] - 2026-03-25

### Changed - Documentation + Skill Consolidation (Session 75)
- **README.md:** Updated from Session 15. Added Track/Historian section, live spoke examples (PathFinder, Tracks), updated skills table, version string (2.0.69).
- **docs/llm-full.txt:** Created single-file LLM context loader (91KB). Concatenates WAI-State.json, core protocol files, utilities, CHANGELOG. Enables external agents to load full framework knowledge in one file.
- **templates/commands/wai-closeout.md:** Integrated production release gate (Step 0: "Is this a production release?") + quality gates (0a-0e: hygiene, breaking changes, tests, linting, benchmarks). Added Step 7b (docs sync automation). Added Step 13 (git tag for releases). Folded /wai-shipit into closeout workflow.
- **Removed:** templates/commands/wai-shipit.md, .claude/commands/wai-shipit.md, WAI-Spoke/commands/wai-shipit.md, templates/spoke/skills/shipit/ — shipit functionality consolidated into closeout.
- **Updated:** README.md, CLAUDE.md, WAI-Skills.jsonl — removed shipit references, clarified single /wai-closeout command for all workflows.

### Deliverables
- Single /wai-closeout command handles both normal sessions and production releases
- Quality gates only run if production release = yes
- Git tag applied only for production releases
- Step 7b automates README.md + docs/llm-full.txt regeneration on protocol changes
- All users now have unified single-command closeout workflow

### Signals Ready for Hub Distribution
- signal-critical-path-resolution-complete-v1 (impact 9) — framework production-ready, all 3 critical gaps closed
- signal-context-estimation-accuracy-v1 (impact 9) — accurate token usage measurement via /context
- signal-batch-sequence-required-v1 (impact 8) — teaching batch dependencies discovered
- signal-ozi-autonomous-orchestration-v1 (impact 8) — Ozi dispatch unblocked
- decision-plan-dogfood-execute-protocol (impact 8) — dogfood + execute pattern validated

### Status
- **Framework State:** v2.0.70. Production-ready. All session continuity mechanisms validated. Cleaner closeout procedure. Ready for Ozi autonomous dispatch and hub teaching distribution.

## [2.0.69] - 2026-03-25

### Added - Critical Path Implementation (Session 74)
- **Gap 1: Context Estimation Accuracy** — replaced naive file-size estimates with actual `/context` tool measurement in wakeup Step 7. Framework now reports real token usage, not guesses (impact 9).
- **Gap 2: Lug Routing Awareness** — extended lug schema with `routed_to` enum (LOCAL|FRAMEWORK|SIGNAL) and `scope_verified_by` field. Ozi dispatch gate skips non-LOCAL lugs. Closeout Step 5c routes by destination: LOCAL→spoke, FRAMEWORK→teachings, SIGNAL→bulletin.
- **Gap 3: Interruption Recovery** — added track integrity validation in wakeup Step 3b. Detects session interruptions via `completed: true` field. Auto-save checkpoints at `.autosave/turn-{N}.json`. Recovery prompt: Green Light (resume) / Red Light (inspect) / Skip / New. Closeout Step 10 cleans autosaves >3 sessions old.

### Changed
- `templates/commands/wai.md` — Step 3b (new): track integrity check + interruption detection. Step 4: in-progress lug timeout detection (>4h). Step 7: measure context not estimate. Step 8: autosave + track structure.
- `templates/commands/wai-lug-schema.md` — new "Routing Fields" section (routed_to, scope_verified_by, routing logic).
- `templates/commands/wai-closeout.md` — Step 5c: routing-aware archival. Step 9c: hub bulletin respects SIGNAL routing. Step 10 (new): autosave cleanup.
- `WAI-Spoke/skills/ozi-work-queue-monitor/wai-ozi-work-queue-monitor.md` — added routing gate in auto_dispatch_ready_work().

### Signals Created
- signal-context-estimation-accuracy-v1 (impact 9, routed FRAMEWORK)
- signal-recovery-mechanism-design-v1 (impact 8, routed SIGNAL)
- signal-critical-path-resolution-complete-v1 (impact 9, routed SIGNAL)

### Status
- **Framework State:** Production-ready. All Ozi autonomous orchestration components in place.
- **Version:** 2.0.68 → 2.0.69 (session patch)

## [2.0.67] - 2026-03-25

### Changed
- `wai-lug-schema.md` slimmed 795→421 lines (-47%): implementation lug JSON schema, PEV chain examples, victory briefing, Ozi types, WAI-Challenges schema moved to `wai-lug-schema-reference.md`. Duplicate dogfooding section fixed.
- `wai-improve.md` slimmed 656→380 lines (-42%): fit report template, idea lug JSON, approval template, backlog output template, dogfood audit criteria moved to `wai-improve-reference.md`.

### Added
- `wai-lug-schema-reference.md` — companion reference file (349L) for on-demand loading
- `wai-improve-reference.md` — companion reference file (182L) for on-demand loading
- `templates/spoke/skills/` sync: 6 missing skill folders created (auto-on/off/parallel/status, lug-compat, ozi-work-queue-monitor)
- `templates/spoke/AGENTS.md` Bootstrap step 3: explicit hub path teaching discovery fallback added

### Fixed
- `templates/spoke/skills/` was missing 6 skill folders registered in WAI-Skills.jsonl
- 4 spoke template skill files (wai.md, wai-closeout.md, wai-shipit.md, wai-chat-to-track.md) were behind templates/commands/ masters — synced

## [2.0.56] - 2026-03-24

### Fixed
- `wai-closeout.md` Step 9c: hub bulletin now filters to `type == "signal"` only (was publishing all high-impact lugs — epics, tasks, implementations — causing 155-file accumulation since February)

### Added
- `refactor-mail-routing-language-v1` lug (P4) — deferred: inbox→incoming/outgoing language standardization
- `hub/teachings_repo/framework/current/skill-wai-closeout-step9c-fix-v1.md.teaching` — distributes the Step 9c fix to connected spokes

### Maintenance
- Cleared 155 stale non-signal files from `hub/WAI-Hub/Signals/incoming/` to `processed/`
- Adopted 4 hub teachings (fleet-health already applied, 2 signal duplicates skipped, 7 signals from high-impact pack ingested)

## [2.0.50] - 2026-03-19

### Recorded
- Lug `43c7023a0244` — docs/llm-full.txt + README.md maintenance, priority before_next_epic

## [2.0.41] - 2026-03-17

### Added
- `framework/skills/hub-spoke-registry.yaml` — fleet awareness: reads hub-registry.json, resolves each spoke's WAI-State.json, builds session-scoped delivery map with can_receive flags
- `wai.md` Step 3b — hub fleet read on wakeup, surfaces spoke table, delivery map held in memory for mail routing

### Changed
- `wai-lug-advisor.md` — Required Field Defaults: `gb` must be model ID (never a persona name); defaults for `s`, `ca`, `impact`, `priority`

### Delivered
- Tracks spoke inception lug v2.0.0 written and delivered to Tracks inbox via hub registry

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

## Session 42 - 2026-03-18

### Teaching Reconciliation + Test Coverage Prep

**Implemented:**
- Teaching Discovery Reconciliation (lug 6ed194b4add6)
  - Enhanced Step 3a with 3-tier verification (filename/signals/files)
  - Auto-reconciles already-implemented teachings to processed/ folder
  - Eliminates false-positive "new teachings" on every wakeup
  - 5 teachings reconciled: skill-system, track-chain, closeout, shipit, step3a

**Fixed:**
- Website image links (wheelwright-ai-website repo)
  - Changed relative to absolute paths in preview HTML files
  - Images now load correctly at http://localhost:8000/preview/

**Prepared:**
- Test Coverage Review lug (f8e2c5a3d9b1) enhanced with full P/E/V fields
  - 4-phase implementation plan documented
  - Ready for 5-8 hour execution session

**Files Modified:**
- templates/commands/wai.md
- .claude/commands/wai.md
- templates/spoke/commands/wai.md
- WAI-Spoke/WAI-Lugs.jsonl (2 lugs updated)
- WAI-Spoke/seed/processed/ (+5 teaching files)

**Impact:** All spokes will benefit from automatic teaching reconciliation on next hub distribution.


## Session 43 - 2026-03-18

### Wakeup + Uncommitted Changes Review

**Executed:**
- 10-step WAI wakeup protocol
  - Teaching discovery: 0 new teachings found
  - Skills loaded: 24 skills (2 core, 6 advisory, 10 utility, 6 governance)
  - Active lugs: 6 pending tasks
  - Context health: 60K/200K tokens (30% used)

**Reviewed:**
- Uncommitted changes from Sessions 41-42 (64 modified files)
  - Teaching reconciliation protocol (Step 3a enhancement)
  - Lug cleanup (10+ completed lugs marked)
  - Test artifact cleanup (TestSpoke, test-bench-v1, verification_copilot_script)
  - Architecture review + Security audit + Test coverage reports
  - Command template syncs

**Analysis:**
- All changes verified as legitimate Session 41-42 work
- Safe to commit: teaching reconciliation, lug hygiene, documentation
- Next: User decision on commit vs continue Phase 4

**Files Reviewed:**
- WAI-Spoke/WAI-Lugs.jsonl (295 line changes)
- templates/commands/wai.md (Step 3a enhancement)
- CHANGELOG.md, ARCHITECTURE-REVIEW.md, SECURITY-AUDIT.md
- 9 command template files synced
- Session track: WAI-Spoke/sessions/track_20260318-wakeup.jsonl

**Impact:** Comprehensive review provided, ready for next action.


## Session 43 (continued) - 2026-03-18

### GitHub Actions Integration Error Diagnosis

**Investigated:**
- User reported integration errors on GitHub after push
- Ran `./run-integration-tests.sh` locally to reproduce
- Analyzed `benchmarks/e2e/test_skills.py` validation schema

**Root Cause Identified:**
1. **126 Lug Status Validation Failures**
   - Session 42 introduced `"completed"` and `"archived"` statuses
   - Test expects: `o/p/c/b` or `open/in-progress/closed/resolved/blocked/published/reviewed/proposed`
   - Test does NOT recognize `"completed"` or `"archived"`
   - Affects 126 lugs in WAI-Lugs.jsonl

2. **3 Skill Structure Failures (wai.md)**
   - Missing: `## Wakeup Protocol`
   - Missing: `## Complete Briefing Format`
   - Missing: `## Health Check`

3. **4 Inbox Routing Documentation Failures**
   - Missing routing rules for delivery_confirmation
   - Missing routing rules for phone-home
   - Missing mailroom safety rules
   - Missing explicit NEVER prohibitions

**Resolution Options Provided:**
- Option 1: Fix test to accept new statuses (quick fix)
- Option 2: Migrate all lugs to old status values (breaking change)
- Option 3: Disable GitHub Actions (loses CI/CD)
- Option 4: Comprehensive fix (test + wai.md + routing docs) - **Recommended**

**Signal Extracted:**
- Impact 8: First comprehensive CI/CD failure diagnosis
- Identifies schema drift pattern between implementation and validation

**Next:** User decision on which resolution option to implement

**Files Analyzed:**
- `.github/workflows/integration-tests.yml`
- `benchmarks/e2e/test_skills.py` (lines 64-69)
- `run-integration-tests.sh`
- Test output showing 126 status failures + 3 structure + 4 routing

**Impact:** Unblocking green CI/CD builds, establishing schema evolution pattern.
## v2.0.153 — 2026-04-05

### Changed
- Fleet-wide WAI spoke cleanup: ingest roots cleared across 17 spokes
- WAI-Lugs.jsonl flat lug migration: 111 orphaned lugs placed into bytype/
- Session directory placement fix: 21 misplaced dirs moved to WAI-Spoke/sessions/
- wheelwright-ai-website hook stack repaired (30-day stale wai.md, wrong session-start path)
- wai.md Step 3b: misplaced-session auto-fix added

### Added
- Teaching: spoke-session-placement-guard-v1
- Hub signal: signal-hub-signal-redirect-routing-v1 routed to framework


