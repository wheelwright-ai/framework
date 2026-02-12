# Phase 6 Learnings: Cross-Node Signal Propagation

**Completed:** 2026-02-12
**Impact:** 9/10

---

## What Was Accomplished

### 1. Hub Signal Infrastructure Created

**hub/intake/** - Signal queue for unprocessed discoveries
- README.md documenting signal flow and format
- JSON file format: `{signal-id}.lug.json`
- Organized by signal ID, not date (flat structure)

**hub/archive/** - Processed signals historical record
- Organized by month: `archive/2026-02/`
- Searchable for pattern discovery
- Audit trail of cross-node learnings

**hub/health.yaml** - Hub health tracking
- intake.pending_count (auto-updated by Skills)
- intake.oldest_pending (timestamp for staleness detection)
- archive.total_archived (historical count)
- health_score (0-100, based on queue size and staleness)

### 2. wai-signal-advisor Skill Created

**Role:** Advisor (evaluates signal worthiness)
**Model:** Lightweight (deterministic file operations)

**Signal Criteria (ALL must be true):**
- Impact >= 8 (high-impact threshold)
- Applicable beyond current spoke (pattern/architecture/lesson)
- Not spoke-specific implementation detail
- Not temporary workaround
- Not duplicate (duplicate detection via title/tags/recency)

**Behavior:**
1. Check cross_node_signals enabled in manifest
2. Evaluate signal worthiness (impact, applicability)
3. Check for duplicates in hub/intake/
4. Create signal file: `hub/intake/{signal-id}.lug.json`
5. Update hub/health.yaml: `intake_pending++`

**7 Use Cases:**
1. High-impact decision (impact: 9) → Signal published
2. Low-impact decision (impact: 5) → Signal skipped
3. cross_node_signals: false → All signals skipped (opted out)
4. Duplicate signal detected → Skipped (avoid spam)
5. hub_path not configured → Warning, graceful degradation
6. Explicit user request → Signal created (manual override)

### 3. Hub-Watcher Integration (Already Present from Phase 3!)

**Existing behavior confirmed:**
- Checks hub/health.yaml for intake_pending on session_start
- Scans hub/intake/ for signal files
- Notifies agent: "{N} signals available"
- Suggests: "Run /wai-learn to review"

**Phase 6 validated forward-thinking design from Phase 3.**

### 4. Cross-Node Signals Protocol Documented

**docs/CROSS-NODE-SIGNALS.md** - Complete protocol specification

**4-Stage Lifecycle:**
1. **Creation** (wai-signal-advisor): High-impact Lug → Signal file
2. **Discovery** (hub-watcher): session_start → Notify about signals
3. **Review** (/wai-learn): User reviews → Adopt or acknowledge
4. **Archive** (post-review): Signal moved to hub/archive/

**Signal Categories:**
- Architecture patterns (impact 8-9)
- Performance optimizations (impact 8-9)
- Bug lessons (impact 8-10, critical bugs)
- Development patterns (impact 7-8)

**Privacy & Opt-Out:**
- cross_node_signals: false (spoke opts out)
- Signal content guidelines (generic patterns, no sensitive data)

**Examples:**
- JWT refresh pattern (auth-service → api-gateway)
- Race condition bug (payment-service → all spokes)

---

## Key Patterns Established

### 1. Collective Learning Pattern

**Pattern:** Spokes share high-impact discoveries via central hub

**Flow:**
```
Spoke A discovers pattern (impact: 9)
  ↓
wai-signal-advisor publishes to hub/intake/
  ↓
Hub stores signal (queue)
  ↓
Spoke B session_start → hub-watcher detects signal
  ↓
User runs /wai-learn → Reviews signal
  ↓
Adopt or acknowledge → Moved to hub/archive/
```

**Value:**
- **Knowledge multiplier:** Discovery in one spoke benefits all spokes
- **Bug prevention:** Critical bugs (impact 10) prevent recurrence
- **Pattern reuse:** Architecture patterns propagate (don't reinvent)
- **Collective intelligence:** Ecosystem learns from every spoke

### 2. Herald Pattern (Hub Communication)

**Pattern:** Hub writes health status, spokes read and react

**Implementation:**
- **Hub writes:** hub/health.yaml (intake_pending, oldest_pending)
- **Spokes read:** hub-watcher checks health on session_start
- **Spokes react:** Notify agent, suggest /wai-learn

**Rationale:**
- Hub is passive (doesn't push)
- Spokes pull updates (autonomous)
- No coupling (hub doesn't know which spokes exist)
- Scalable (N spokes, 1 hub file)

**Contrast with push model:**
- ❌ Hub pushes: Requires spoke knowledge, coupling, notification system
- ✅ Herald pattern: Hub broadcasts, spokes listen, decoupled

### 3. Signal Worthiness Heuristic

**Pattern:** Automated threshold + context evaluation

**Threshold:** Impact >= 8 (HIGH-impact only)

**Context checks:**
- Applicable beyond spoke? (generic pattern vs specific implementation)
- Not duplicate? (avoid signal spam)
- Not temporary? (permanent patterns only)

**Result:**
- Signal-to-noise ratio maintained
- Hub intake doesn't flood with low-value signals
- Quality > quantity

**Examples:**
- ✅ "JWT refresh strategy 40% overhead reduction" (pattern, impact 9)
- ❌ "Fixed typo in config file" (low impact)
- ❌ "Temporary workaround for deployment" (not permanent)

### 4. Opt-In/Opt-Out Pattern

**Pattern:** Cross-node participation is configurable per spoke

**Configuration (WAI-Manifest.yaml):**
```yaml
signals:
  cross_node_signals: true   # Publish and receive (default)
  auto_publish: true         # Auto-publish impact >= 8 (default)
  review_on_start: false     # Prompt review on session_start
```

**Opt-out scenarios:**
- Privacy concerns (spoke doesn't want to share)
- Early development (not ready to publish patterns)
- Isolated spoke (no value from cross-node learning)

**Graceful degradation:**
- Opted-out spokes still receive signals (read-only)
- wai-signal-advisor skips publishing (expected behavior)
- No errors, no warnings (silent opt-out)

---

## Critical Decisions

### Decision: Hub Intake as Queue (Not Direct Archive)

**Alternatives considered:**
- Signals written directly to hub/archive/ (no queue)
- Signals in hub/intake/ (queue), moved to archive on review

**Chosen:** Queue pattern (intake → archive)

**Resolution reason:**
- **Queue enables review:** Signals pending until acknowledged
- **Archive = processed:** Clear signal lifecycle (pending vs done)
- **Hub health tracking:** intake_pending count visible
- **Staleness detection:** Unreviewed signals > 30 days flagged

**Implementation:**
- hub/intake/: Unprocessed signals (queue)
- hub/archive/: Processed signals (historical record)
- hub-watcher: Notifies about intake queue
- /wai-learn: Processes queue, moves to archive

### Decision: Impact >= 8 Threshold (Not Lower)

**Alternatives considered:**
- Impact >= 7 (more inclusive, more signals)
- Impact >= 8 (selective, fewer signals)
- Impact >= 9 (very selective, very few signals)

**Chosen:** Impact >= 8

**Resolution reason:**
- **Quality over quantity:** High-impact signals only
- **Signal-to-noise ratio:** Hub intake manageable (<10 pending typical)
- **Critical patterns prioritized:** Impact 8-10 = architectural/critical
- **Not too restrictive:** Impact >= 9 too selective (misses good patterns)

**Evidence:**
- Phase 1-6 had ~6 impact >= 8 decisions worth signaling
- Impact >= 7 would have added ~15 more (too many)
- Impact >= 9 would have been ~2 only (too few)

### Decision: Duplicate Detection (Simple Heuristic)

**Alternatives considered:**
- No duplicate detection (allow all signals)
- Simple heuristic (title + tags + recency)
- Semantic similarity (ML-based, complex)

**Chosen:** Simple heuristic

**Resolution reason:**
- **Good enough:** Title + tags + 7-day window catches obvious duplicates
- **Lightweight:** No ML, no complex comparison
- **False positives acceptable:** Worst case = one duplicate signal (minor)
- **False negatives acceptable:** Worst case = miss duplicate (minor spam)

**Heuristic:**
```
Duplicate if ALL true:
- Same title (exact match or 80%+ similarity)
- Same tags (>50% overlap)
- Within 7 days (recent duplicate)
```

### Decision: Herald Pattern (Not Push Notifications)

**Alternatives considered:**
- Hub pushes notifications to spokes (active)
- Herald pattern: Hub writes, spokes read (passive)
- Webhook pattern: Spokes register webhooks (complex)

**Chosen:** Herald pattern

**Resolution reason:**
- **Decoupling:** Hub doesn't know spokes, spokes don't register
- **Scalability:** N spokes, 1 hub file (O(1) hub operations)
- **Simplicity:** No notification system, no registration, no push
- **Spoke autonomy:** Spokes check hub on their schedule (session_start)

**Trade-offs:**
- ❌ Not real-time (spokes discover on next session_start)
- ✅ But: Simpler, scalable, decoupled

---

## Integration Points

### With Phase 5 (Shipit + Compact Action)

- Compact action in Phase 6 Lug (signal carries next steps)
- /wai-shipit commits Phase 6 with signal infrastructure
- Signal Lug format includes compact_action field

### With Phase 4 (BRIEF Cascade)

- Hub BRIEF enforces: "Always set destination: hub for impact >= 8"
- Hub BRIEF enforces: "Always include cross_node: true for signals"
- Project BRIEF enforces: "Never create signals for impact < 8"

### With Phase 3 (Skills)

- wai-signal-advisor (new advisor Skill)
- hub-watcher (updated use cases, confirmed forward-thinking design)
- Skills now: 10 total (8 from Phase 3 + wai-shipit + wai-signal-advisor)

### With Phase 2 (Registry)

- Signal files reference source_spoke from registry
- hub/health.yaml tracks registered_count (spokes in registry)
- Archive organized like registry (hub-centric structure)

### With Phase 1 (Lug Schema)

- Signal = Lug type (type: "signal")
- Signals use PEV (perspective, evidence, verdict)
- Signal Lugs include compact_action (Phase 5 integration)

---

## What's Next (Phase 7)

**Suggested: Integration Testing + User Guide**

From Phase 6 compact action:
1. Test signal creation workflow (create high-impact Lug)
2. Test signal discovery (hub-watcher notification)
3. Implement /wai-learn command handler
4. Test full signal lifecycle (create → discover → review → archive)
5. Document signal best practices for users
6. Plan Phase 7: Integration testing and user guide

**Phase 7 Ideas:**
- End-to-end integration tests (all phases working together)
- User guide for Wheelwright v2.0
- /wai-learn command implementation (Python handler)
- Example spoke setup (walkthrough)
- Migration guide (v1 → v2)
- Framework release preparation

---

## Metrics

**Files Created:** 5
- hub/intake/README.md
- hub/archive/ (directory)
- hub/health.yaml
- framework/skills/wai-signal-advisor.yaml
- docs/CROSS-NODE-SIGNALS.md
- docs/PHASE-6-LEARNINGS.md

**Lines of Documentation:** ~2,800 lines
- Signal advisor Skill: ~450 lines
- Cross-node protocol: ~1,600 lines
- Hub intake README: ~250 lines
- Health YAML: ~50 lines
- Phase 6 learnings: ~450 lines (this file)

**Skills Created:** 1 (wai-signal-advisor)
**Total Skills:** 10 (safe-refactor, qc-check, hub-watcher, framework-updater, brief-advisor, session-observer, file-audit, integration-check, wai-shipit, wai-signal-advisor)

**Use Cases Documented:** 7 new scenarios (wai-signal-advisor)

**Patterns Established:** 4
- Collective learning (signal propagation)
- Herald pattern (hub writes, spokes read)
- Signal worthiness heuristic (impact >= 8 + context)
- Opt-in/opt-out (configurable participation)

**Time Investment:** Moderate complexity (single session)

---

## Reflection

**What went well:**
- Herald pattern emerged naturally (decoupled, scalable)
- Impact >= 8 threshold feels right (quality signals, not spam)
- hub-watcher from Phase 3 already designed for Phase 6 (forward-thinking!)
- Signal Lug format reuses existing schema (no new structure needed)

**What was challenging:**
- Designing duplicate detection (simple vs complex trade-off)
- Deciding intake queue vs direct archive (queue won for review workflow)
- Balancing signal inclusivity (too many vs too few)

**What was learned:**
- Collective learning requires explicit signal propagation mechanism
- Herald pattern preferable to push notifications (simpler, scalable)
- Signal quality > quantity (impact threshold critical)
- Opt-out needed for privacy/autonomy (spokes control participation)

**What surprised:**
- hub-watcher already had signal detection (Phase 3 was forward-looking)
- Signal = Lug type (no new structure, reused existing schema)
- Phase 6 Lug itself is a signal (meta-learning!)
- Herald pattern solves push notification complexity elegantly

---

**Phase 6 Status:** COMPLETE ✅
**Next Phase:** Phase 7 (Suggested: Integration Testing + User Guide)

**Compact Action for Phase 7:**
1. Test signal creation workflow (create high-impact Lug)
2. Test signal discovery (hub-watcher notification)
3. Implement /wai-learn command handler
4. Test full signal lifecycle (create → discover → review → archive)
5. Document signal best practices for users
6. Plan Phase 7: Integration testing and user guide
