# Extension Identity: Wheelwright Framework

**Extension ID:** wheelwright-framework
**Type:** framework
**Framework Version:** 2.0.0

---

## Purpose

The Wheelwright Framework is the foundational extension that provides:
- **Session continuity** through observations and Lugs
- **Skills system** for guardian/advisor/reviewer/watcher/worker behaviors
- **Registry architecture** for Hub-Project-Spoke hierarchy
- **Template cascade** for framework updates
- **Machine-aware optimization** via AI-AGENT-MACHINE-PROTOCOL
- **Cross-node communication** through signals

This is the **meta-extension** - it defines how Wheelwright itself works.

---

## Structure

```
framework/
├── wai/                    # Python implementation
│   ├── __init__.py
│   ├── schema.py          # Lug schema definitions
│   ├── session_hook.py    # Briefing and wakeup
│   ├── closeout_validator.py  # Session end checks
│   └── hooks.py           # Machine status, IDE integration
├── skills/                # Built-in Skills (8 total)
│   ├── safe-refactor.yaml
│   ├── qc-check.yaml
│   ├── hub-watcher.yaml
│   ├── framework-updater.yaml
│   ├── brief-advisor.yaml
│   ├── session-observer.yaml
│   ├── file-audit.yaml
│   └── integration-check.yaml
├── templates/             # Spoke/project templates
│   ├── WAI-Manifest.yaml.template
│   ├── WAI-Lugs.jsonl.template
│   ├── BRIEF.md.template
│   ├── EXTENSION.md.template
│   └── PROJECT.md.template
├── docs/                  # Framework documentation
├── EXTENSION.md          # This file
└── WAI-Manifest.yaml     # Framework registry entry
```

---

## Scope

### What the framework does:
- Defines Lug Contract Specification (observations, decisions, signals)
- Provides 8 built-in Skills (guardian, reviewer, advisor, watcher, worker)
- Implements session hooks (briefing, closeout, validation)
- Manages template cascade (hub → project → spoke updates)
- Tracks machine profiles and IDE optimization status
- Enables cross-node communication via Hub registry

### What the framework does NOT do:
- Project-specific work (that's for spokes)
- Business logic (framework is infrastructure only)
- IDE implementation (framework integrates with Claude Code, not replaces it)

---

## Integration

### Skills Loaded (Framework Built-ins)

**Guardian Skills:**
- **safe-refactor** - Git checkpoint before structural changes
- **integration-check** - IDE environment verification on wakeup

**Reviewer Skills:**
- **qc-check** - Quality gates (tests, startup, coverage)
- **file-audit** - Sprawl detection and organization health

**Advisor Skills:**
- **brief-advisor** - BRIEF alignment + apprenticeship learning

**Watcher Skills:**
- **hub-watcher** - Hub framework updates and signal detection
- **session-observer** - Event recording and session synthesis

**Worker Skills:**
- **framework-updater** - Template cascade when framework changes

---

## Machine Optimization

Framework supports machine-aware development:

**Classification:**
- HIGH-PERFORMANCE (32GB+ RAM): Aggressive features, parallel execution
- STANDARD (16-31GB RAM): Balanced features, moderate parallelism
- LOW-POWER (<16GB RAM): Conservative features, sequential execution

**Optimization:**
- Machine profiles stored in `hub/machines/{hostname}.lug.json`
- IDE settings auto-configured on session start
- Skills adjust recommendations based on machine class

See: **AI-AGENT-MACHINE-PROTOCOL.md** for complete protocol.

---

## Lifecycle

### Session Start (Wakeup Sequence)
1. **integration-check** verifies Wheelwright is detectable
2. **get_session_start_briefing()** displays:
   - Machine environment (hardware, optimization status)
   - Recent work summary (last session)
   - Failed observations requiring remediation
   - Incomplete Lugs to continue
3. **hub-watcher** checks for framework updates and signals
4. **Load WAI context:** State, BRIEF, Skills

### During Session
Skills fire automatically based on events:
- **pre_refactor** → safe-refactor creates checkpoint
- **pre_commit** → qc-check runs quality gates
- **pre_decision** → brief-advisor checks alignment
- **significant_event** → session-observer logs observation

### Session End (Closeout)
1. **session-observer** synthesizes session summary
2. **closeout_validator** verifies:
   - Git status clean (or explains uncommitted files)
   - Observations logged
   - Framework detectable
   - Machine profile exists
3. Optional: **/shipit** commits with co-author attribution
4. Session Lug created for next briefing

---

## Template Cascade

When framework version updates:
1. Hub updates framework version in `hub/WAI-Manifest.yaml`
2. Spokes' **hub-watcher** detects version mismatch on session_start
3. User runs `/framework-update` in spoke
4. **framework-updater** compares templates:
   - Auto-update if no local modifications
   - Human gate if spoke modified template
5. Spoke `WAI-Manifest.yaml` updated to new framework version

**Template files:**
- WAI-Manifest.yaml (structure changes)
- BRIEF.md (hub policy additions)
- WAI-Lugs.jsonl (schema examples)
- EXTENSION.md (identity updates)
- PROJECT.md (project-level coordination)

---

## Cross-Node Communication

Framework enables signal propagation:

**Signal Flow:**
1. Spoke creates high-impact Lug (impact >= 8, type: signal)
2. **wai-signal-advisor** writes to `hub/intake/`
3. Other spokes' **hub-watcher** detects on session_start
4. Signals acknowledged or adopted across spokes

**Use cases:**
- Authentication pattern discovered in spoke A → propagates to spoke B
- Performance optimization in spoke C → all spokes notified
- Bug pattern and fix → prevents recurrence elsewhere

---

## Skill Overrides

Spokes can override framework Skills:

**Example: Custom QC gates**
Create `spoke/skills/qc-check.yaml`:
```yaml
# Override framework qc-check with custom commands
custom_commands:
  - "npm run lint"
  - "npm test"
  - "npm run type-check"
coverage_threshold: 85
startup_command: "node server.js --help"
```

Framework qc-check loads spoke override if present.

---

## Version History

**v2.0.0 (Current):**
- Registry architecture (Hub-Project-Spoke)
- Skills directory (8 built-in Skills with use cases)
- Template cascade system
- Machine-aware optimization protocol
- PEV fields in Lug schema
- BRIEF cascade (Hub → Project → Spoke)

**v1.x (Legacy):**
- Backpressure file (migrated to qc-check)
- WAI-Rules.md (absorbed into Skills)
- Single-level architecture (no Hub/registry)

---

## Related Documents

- **CLAUDE.md** - Priority 0 instructions for Claude Code
- **AI-AGENT-MACHINE-PROTOCOL.md** - Machine optimization protocol
- **REGISTRY-STRUCTURE.md** - Hub registry architecture
- **LUG-CONTRACT-SPECIFICATION.md** - Lug schema details
- **SKILL-CONTRACT-SPECIFICATION.md** - Skill structure and roles

---

## Maintenance

**Framework Updates:**
Run from any spoke when hub-watcher notifies:
```bash
/framework-update
```

**Health Checks:**
```bash
/wai-status                          # Extension health
python -m wai.closeout_validator --check   # Closeout readiness
```

**Hub Maintenance:**
```bash
python -m wai.hub.health_check       # Ecosystem health
python -m wai.hub.archive_signals    # Move processed signals to archive
```

---

**Last Updated:** 2026-02-12 (Phase 3 - Skills directory created)
**Next Milestone:** Phase 4 - BRIEF cascade formalized
