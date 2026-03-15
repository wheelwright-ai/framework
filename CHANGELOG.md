
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

