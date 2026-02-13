# Cross-Node Signal Propagation Protocol

**Purpose:** Enable spokes to share high-impact learnings across the Wheelwright ecosystem
**Version:** 1.0.0 (Phase 6)
**Framework:** Wheelwright v2.0.0

---

## Overview

Cross-node signals allow spokes to publish discoveries, patterns, and learnings to a central hub where other spokes can discover and adopt them. This creates a **collective learning system** where insights propagate across the ecosystem.

```
┌─────────────┐
│   Spoke A   │──┐
│ (discovers) │  │
└─────────────┘  │
                 ├──> ┌──────────┐      ┌─────────────┐
┌─────────────┐  │    │   Hub    │      │   Spoke B   │
│   Spoke B   │──┼──> │ /intake/ │ ──> │  (adopts)   │
│ (discovers) │  │    └──────────┘      └─────────────┘
└─────────────┘  │           │
                 │           ↓
┌─────────────┐  │    ┌──────────┐
│   Spoke C   │──┘    │/archive/ │
│ (discovers) │       └──────────┘
└─────────────┘
```

---

## Signal Lifecycle

### 1. Creation (Spoke Side)

**Trigger:** High-impact decision or observation (impact >= 8)

**wai-signal-advisor Skill:**
```
Decision/Observation created (impact >= 8)
  ↓
wai-signal-advisor evaluates signal worthiness
  ↓
Check: cross_node_signals enabled in manifest?
  ↓
Check: Pattern applicable beyond this spoke?
  ↓
Check: Duplicate signal already in hub/intake/?
  ↓
Create signal file: hub/intake/{signal-id}.lug.json
  ↓
Update hub/health.yaml: intake_pending++
```

**Signal criteria:**
- Impact >= 8 (high-impact threshold)
- Applicable beyond current spoke (architecture, pattern, lesson)
- Not spoke-specific implementation detail
- Not temporary workaround

### 2. Discovery (Other Spokes)

**Trigger:** Session start

**hub-watcher Skill:**
```
session_start event fires
  ↓
hub-watcher checks hub/health.yaml
  ↓
intake_pending > 0?
  ↓
Scan hub/intake/ for signal files
  ↓
Notify agent: "{N} signals in hub/intake/"
  ↓
List: Signal titles, impacts, source spokes
  ↓
Suggest: "Run /wai-learn to review signals"
```

**Discovery output:**
```
Hub Status:
  Framework: v2.0.0 (current)
  Pending Signals: 3

Signals Available:
  1. JWT refresh strategy (impact: 9, from: auth-service)
  2. Co-located tests pattern (impact: 8, from: framework)
  3. Race condition fix (impact: 8, from: payment-service)

Run /wai-learn to review and acknowledge.
```

### 3. Review (User Action)

**Trigger:** User runs `/wai-learn`

**wai-learn command:**
```
User: /wai-learn
  ↓
List signals in hub/intake/
  ↓
For each signal:
  - Display: title, body, PEV, impact, source_spoke
  - Ask: "Adopt this pattern?" or "Acknowledge only?"
  ↓
User chooses:
  - Adopt: Create local Lug referencing signal
  - Acknowledge: Just mark as reviewed
  ↓
Move signal: hub/intake/ → hub/archive/{YYYY-MM}/
  ↓
Update hub/health.yaml: intake_pending--
```

**Review interface:**
```
Signal 1 of 3:
─────────────────────────────────────────────────
Title: JWT refresh strategy reduces auth overhead 40%
Source: auth-service
Impact: 9/10
Created: 2026-02-12

Body:
Discovered efficient JWT refresh pattern using sliding window
refresh (15min token, 7day refresh token). Reduced auth overhead
from 200+ refresh calls/hour to 120/hour (40% reduction).

PEV:
  Perspective: JWT tokens expiring too frequently caused UX issues
  Evidence: User complaints about re-login, metrics showed spikes
  Verdict: Sliding window refresh eliminated re-login issues

Actions:
  [A] Adopt this pattern (create local Lug)
  [K] Acknowledge only (mark reviewed)
  [S] Skip (keep in queue)
  [Q] Quit review

Choice:
```

### 4. Archive (Post-Review)

**Trigger:** Signal acknowledged or adopted

**Archive structure:**
```
hub/archive/
├── 2026-02/
│   ├── signal-jwt-refresh-2026-02-12.lug.json
│   ├── signal-colocated-tests-2026-02-10.lug.json
│   └── signal-race-condition-2026-02-08.lug.json
├── 2026-01/
│   └── ...
└── README.md
```

**Archive metadata:**
```json
{
  "archived_at": "2026-02-12T16:00:00Z",
  "reviewed_by": "spoke-framework",
  "action_taken": "adopted",  // or "acknowledged"
  "local_lug_id": "decision-adopt-jwt-refresh-2026-02-12"
}
```

---

## Signal File Format

### Structure

```json
{
  "lug_id": "signal-{topic}-{date}",
  "type": "signal",
  "timestamp": "2026-02-12T15:30:00Z",
  "title": "Brief signal title (< 80 chars)",
  "body": "Detailed explanation of pattern/learning",
  "tags": ["category1", "category2"],
  "pev": {
    "perceive": "Context/problem statement",
    "execute": "Data/observations supporting the learning",
    "verify": "Solution/conclusion"
  },
  "impact": 8-10,
  "status": "published",
  "source_spoke": "wheelwright/{spoke-name}",
  "destination": "hub",
  "cross_node": true,
  "created_by": "agent-{spoke}"
}
```

### Naming Convention

**Format:** `signal-{topic-slug}-{YYYY-MM-DD}.lug.json`

**Examples:**
- `signal-jwt-refresh-2026-02-12.lug.json`
- `signal-race-condition-fix-2026-02-10.lug.json`
- `signal-colocated-tests-2026-02-08.lug.json`
- `signal-caching-architecture-2026-02-05.lug.json`

**Topic slug rules:**
- Lowercase, hyphen-separated
- 2-4 words max
- Descriptive but concise
- No dates, versions, or spoke names in slug

---

## Signal Categories

### Architecture Patterns

**Examples:**
- "Hexagonal architecture for microservices"
- "Event sourcing for audit trail"
- "CQRS for read-heavy workloads"

**Impact:** Typically 8-9

### Performance Optimizations

**Examples:**
- "Caching layer reduces DB load 60%"
- "Lazy loading improves page load 2x"
- "Connection pooling eliminates timeout errors"

**Impact:** Typically 8-9

### Bug Lessons

**Examples:**
- "Race condition in concurrent writes"
- "Memory leak from event listener cleanup"
- "SQL injection via unescaped user input"

**Impact:** Typically 8-10 (critical bugs)

### Development Patterns

**Examples:**
- "Co-located tests reduce maintenance burden"
- "Feature flags enable gradual rollout"
- "Pre-commit hooks prevent secret leaks"

**Impact:** Typically 7-8 (may not always reach signal threshold)

---

## Integration with Skills

### wai-signal-advisor (Creation)

**Role:** Advisor
**Trigger:** post_decision (impact >= 8), post_observation (impact >= 8)

**Behavior:**
1. Check if signal-worthy (impact, applicability, not duplicate)
2. Extract Lug content (title, body, PEV)
3. Create signal file in hub/intake/
4. Update hub/health.yaml

### hub-watcher (Discovery)

**Role:** Watcher
**Trigger:** session_start

**Behavior:**
1. Check hub/health.yaml for intake_pending count
2. Scan hub/intake/ for signal files
3. Notify agent about pending signals
4. Suggest running /wai-learn

### /wai-learn (Review)

**Role:** User command
**Trigger:** on_demand

**Behavior:**
1. List signals in hub/intake/
2. Display each signal with details
3. Prompt user: Adopt, Acknowledge, or Skip
4. Move acknowledged/adopted signals to archive/
5. Create local Lug if adopted

---

## Configuration

### Spoke-Level (WAI-Manifest.yaml)

```yaml
signals:
  cross_node_signals: true  # Enable signal participation
  auto_publish: true        # Auto-publish impact >= 8
  review_on_start: false    # Prompt /wai-learn on session_start
```

**cross_node_signals:**
- `true`: Spoke publishes and receives signals (default)
- `false`: Spoke opts out of cross-node participation (privacy)

**auto_publish:**
- `true`: wai-signal-advisor publishes automatically (default)
- `false`: Require manual approval before publishing

**review_on_start:**
- `false`: Hub-watcher notifies, user runs /wai-learn manually (default)
- `true`: Session start prompts immediate signal review (aggressive)

### Hub-Level (hub/health.yaml)

```yaml
intake:
  pending_count: 0          # Auto-updated by Skills
  oldest_pending: null      # Timestamp of oldest signal
  max_pending: 20           # Warning threshold

maintenance:
  cleanup_frequency: "weekly"
  archive_after_days: 90    # Move to archive after 90 days if unreviewed
```

---

## Hub Maintenance

### Automatic Cleanup

**Trigger:** Weekly (or when intake_pending > 50)

**Actions:**
1. Archive signals older than 30 days (unreviewed)
2. Update hub/health.yaml
3. Report cleanup summary

**Command:**
```bash
python -m wai.hub.archive_signals
```

### Health Checks

**Trigger:** On-demand or scheduled

**Checks:**
- Intake queue size (warn if > 20)
- Oldest pending signal (warn if > 30 days)
- Archive organization (monthly directories exist)
- Spoke connectivity (all registered spokes active)

**Command:**
```bash
python -m wai.hub.health_check
```

---

## Privacy & Opt-Out

### Spoke Opt-Out

Spokes can disable cross-node participation:

```yaml
# WAI-Manifest.yaml
signals:
  cross_node_signals: false
```

**Effect:**
- wai-signal-advisor skips signal publication
- hub-watcher still notifies about signals (read-only mode)
- Spoke can review signals but doesn't publish

### Signal Content Guidelines

**Do include:**
- Architecture patterns (generic)
- Bug lessons learned (sanitized)
- Performance optimization techniques
- Development workflow improvements

**Don't include:**
- Sensitive business logic
- Customer data or PII
- Proprietary algorithms
- Security vulnerabilities (until patched)

---

## Examples

### Example 1: JWT Refresh Pattern

**Spoke A (auth-service) discovers pattern:**
```json
{
  "lug_id": "signal-jwt-refresh-2026-02-12",
  "type": "signal",
  "title": "JWT refresh strategy reduces auth overhead 40%",
  "body": "Sliding window refresh: 15min token, 7day refresh token",
  "pev": {
    "perceive": "Frequent token expiration caused UX issues",
    "execute": "200+ refresh calls/hour, user complaints",
    "verify": "Sliding window reduced to 120 calls/hour, zero complaints"
  },
  "impact": 9,
  "source_spoke": "wheelwright/auth-service"
}
```

**Spoke B (api-gateway) discovers via hub-watcher:**
```
Hub Status:
  Pending Signals: 1
  - JWT refresh strategy (impact: 9, from: auth-service)

Run /wai-learn to review.
```

**Spoke B reviews via /wai-learn:**
```
User: /wai-learn

Signal 1 of 1:
  Title: JWT refresh strategy reduces auth overhead 40%
  Source: auth-service
  [Details shown...]

Action: [A]dopt
  → Created local Lug: decision-adopt-jwt-refresh
  → Archived signal: hub/archive/2026-02/
```

### Example 2: Race Condition Bug

**Spoke C (payment-service) discovers bug:**
```json
{
  "lug_id": "signal-race-condition-2026-02-10",
  "type": "signal",
  "title": "Race condition in concurrent payment processing",
  "body": "Two simultaneous requests could charge user twice",
  "pev": {
    "perceive": "Reports of duplicate charges",
    "execute": "Race condition in payment state check + update",
    "verify": "Added transaction lock, eliminated duplicates"
  },
  "impact": 10,
  "tags": ["bug", "concurrency", "critical"],
  "source_spoke": "wheelwright/payment-service"
}
```

**All spokes review (critical bug, impact: 10):**
- Spoke A: Checks auth service for similar pattern → Not applicable
- Spoke B: Checks API gateway → Found similar race condition, fixed
- Spoke D: Checks inventory service → Not applicable

**Result:** Spoke B avoids production bug by learning from Spoke C's experience.

---

## Metrics & Success Criteria

### Signal Quality

- **Publication rate:** 1-5 signals/month per active spoke
- **Impact distribution:** 80% impact 8-9, 20% impact 10
- **Adoption rate:** >50% of signals adopted or acknowledged within 30 days

### Hub Health

- **Intake queue:** < 10 pending signals at any time
- **Staleness:** No signal > 30 days unreviewed
- **Archive organization:** Monthly directories, searchable

### Cross-Node Learning

- **Pattern reuse:** Same pattern adopted by 2+ spokes
- **Bug prevention:** Critical bugs (impact 10) prevent similar issues in other spokes
- **Knowledge transfer:** New spokes benefit from archived signals

---

## Related Documents

- **hub/intake/README.md** - Signal queue documentation
- **framework/skills/wai-signal-advisor.yaml** - Signal creation Skill
- **framework/skills/hub-watcher.yaml** - Signal detection Skill
- **docs/COMMAND-MAPPING.md** - /wai-learn command specification
- **hub/health.yaml** - Hub health status

---

**Created:** Phase 6 - Cross-node signal propagation
**Version:** 1.0.0
**Framework:** Wheelwright v2.0.0
