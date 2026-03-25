# Implementation Plan: Ozi Work Queue Orchestration Suite

**User Story:** "I'll build the queue of lugs. Ozi works through it. I get UAT + implementation notes in track. Approve auto mode and it chains: implement → closeout → load next item, minimal context, repeat until queue empty or I stop it."

**Scope:** 3 interdependent epics (19-27 steps total)
- epic-ozi-routing-awareness-v1 (6-8 steps)
- epic-ozi-work-queue-orchestration-v1 (10-15 steps)
- epic-ozi-queue-auto-discovery-v1 (3-4 steps)

**What Changes:**
1. WAI-State.json: new `_work_queue` section with priority queue + readiness states
2. Lug schema: add `routed_to`, `queue_state`, `estimated_steps`, `blocker_list` fields
3. Wakeup process: new Step 9 to display work queue status + offer Work/Review/Auto options
4. Closeout process: new Step 10 to mark completed, archive, prep next item
5. Ozi skill: routing gate before lug creation (LOCAL | FRAMEWORK | SIGNAL)
6. Track schema: new `implementation_notes` + `uat_recording` + `queue_context` fields
7. New optional Ozi auto-mode skill: enables autonomous job chaining with minimal context

**What Does NOT Change:**
- Existing lug storage or retrieval (bytype/ structure stays)
- Session continuity (wakeup/closeout protocol unchanged at core)
- Single-model assumptions (multi-AI support unaffected)
- Teaching discovery pipeline (priority 1 in queue, but discovery logic stays same)

---

## Phase 1: Routing Awareness (Prerequisite)

Enables correct lug scoping before work queue processes them.

### Step 1.1: Extend Lug Schema
- Add `routed_to` field (enum: LOCAL | FRAMEWORK | SIGNAL | null)
- Add `scope_verified_by` field (string: who decided routing)
- Update lug-schema.md reference to document these fields

**Files touched:**
- `WAI-Spoke/lugs/reference/lug-schema.md` (reference docs)
- Examples in lug-advisor skill

### Step 1.2: Create Ozi Routing Gate Skill
- **NEW SKILL:** `wai-ozi-routing-gate.md` — Ozi's routing decision logic
- Before dispatching lug creation, Ozi invokes routing gate
- Routing gate asks: "LOCAL (this spoke) | FRAMEWORK (hub distribution) | SIGNAL (broadcast to other spokes)?"
- Record user's choice or Ozi's assessment in `routed_to` field
- Announce: "Creating [type] {title} → [destination]"

**Files touched:**
- `templates/commands/wai-ozi-routing-gate.md` (NEW — routing gate skill for Ozi)

### Step 1.3: Update Closeout Lug Archival
- Closeout Step 5c (lug status sync): filter completed lugs by `routed_to`
- LOCAL lugs → move to `bytype/{type}/completed/`
- FRAMEWORK lugs → move to `bytype/{type}/completed/` AND copy to hub teachings
- SIGNAL lugs → move to `bytype/signal/delivered/` AND copy to hub signal bulletin

**Files touched:**
- `templates/commands/wai-closeout.md` Step 5c

### Step 1.4: Update Wakeup Briefing
- Show routing info for active lugs in briefing table
- Example: "epic-hub-evolution (FRAMEWORK, in_progress)" vs "task-test-ozi (LOCAL, open)"

**Files touched:**
- `templates/commands/wai.md` Step 7 briefing output

### Step 1.5: Update Lug Advisor Reference
- Document routing decisions in lug-advisor examples
- Show how to determine LOCAL vs FRAMEWORK vs SIGNAL for different work types

**Files touched:**
- `WAI-Spoke/lugs/reference/lug-advisor-reference.md`

**Acceptance:** Lugs created during Phase 1-3 implementation have `routed_to` field populated and visible in briefing.

---

## Phase 2: Work Queue Orchestration (Core)

Implements queue management, ready/needs_refinement states, job chaining.

### Step 2.1: Extend WAI-State.json with Queue Section
Add `_work_queue` section:
```json
{
  "_work_queue": {
    "current_job_id": null,
    "current_job_priority": null,
    "auto_mode_enabled": false,
    "queue": [
      {
        "id": "{lug_id}",
        "type": "{epic|task|feature|bug|signal}",
        "title": "{title}",
        "priority": 1-4,
        "state": "ready|needs_refinement|blocked|done",
        "estimated_steps": N,
        "blocker_ids": [],
        "created_at": "ISO",
        "started_at": null,
        "completed_at": null
      }
    ],
    "completed_this_session": [],
    "blocked_reasons": {}
  }
}
```

**Files touched:**
- `WAI-Spoke/WAI-State.json`

### Step 2.2: Extend Lug Schema for Queue Fields
Add to every lug (epic, task, feature, bug, signal):
- `status`: "open" | "in_progress" | "completed" (actual work state)
- `queue_state`: "ready" | "needs_refinement" | "blocked" | "done" | null (queue position state)
- `estimated_steps`: number
- `blocker_list`: [lug_ids]
- Update lug examples to show these fields

**Files touched:**
- `WAI-Spoke/lugs/reference/lug-schema.md`

### Step 2.3: Add Queue Status to Wakeup
New Wakeup Step 9 (before ready check):
```
## Step 9: Work Queue Status

If `_work_queue` exists and not empty:
- Count ready items
- Count needs_refinement items
- Count blocked items
- Display:
  "Work Queue: {X} ready, {Y} need refinement, {Z} blocked
   [Work next ready] [Review refinement] [Auto-chain enabled] [Skip]"
```

**Files touched:**
- `templates/commands/wai.md` add Step 9

### Step 2.4: Implement Queue Job Loader
New internal logic (in Ozi skill or wai-queue utility):
- Load next ready item from queue
- Minimal context: WAI-State core + named lug + prev 2 turns track
- ~15-20k tokens (vs full wakeup ~46k)

**Files touched:**
- `templates/commands/wai-auto-on.md` (minimal context loading)

### Step 2.5: Extend Track Schema
Add to track.jsonl every turn:
- `implementation_notes`: what was built/changed
- `uat_recording`: testing done, issues, acceptance
- `queue_context`: which job (id, priority), what's next
- `lug_status_change`: if lug moved to done/blocked, why

**Files touched:**
- `templates/commands/wai-track-generate.md` schema documentation

### Step 2.6: Add Closeout Step 10 (Job Completion)
New Closeout Step 10 (after lug archival, Step 5c):
```
## Step 10: Work Queue Update

If `_work_queue` exists:
1. Find current_job_id in queue
2. If completed (lug.status == done): mark queue item done, update completed_at
3. If blocked (lug.status == blocked): update blocker_reasons
4. If auto_mode_enabled: load next ready item, update current_job_id
5. Display: "[Job X/Y done] [Next: Job Y — {title}] [Auto-chain paused for UAT]"
```

**Files touched:**
- `templates/commands/wai-closeout.md` add Step 10

### Step 2.7: Implement Auto-Mode Job Chaining (Full Auto-Chain Mode)
- User enables `/wai-auto-on` for session-local auto mode
- Once approved, full auto-chain: implement → closeout → load next → repeat (no per-job interruptions)
- Each job runs with minimal context
- Closeout Step 10 auto-loads next ready item if enabled
- Stops on: queue empty, blocker hit, error, user cancel
- Token budget verification happens at closeout (Ozi checks: "Token budget OK for next run?" before auto-loading)

**Files touched:**
- `templates/commands/wai-auto-on.md`
- `templates/commands/wai-auto-status.md`
- `templates/commands/wai-closeout.md` (add Step 10 token budget check)

**Acceptance:**
- Work queue displays at wakeup with ready/needs_refinement distinction
- User can Work Next / Review Refinement / Auto-Chain
- Track captures implementation_notes + uat_recording
- Auto-mode chains jobs with 57% context reduction (46k → 20k)

---

## Phase 3: Queue Auto-Discovery (Bootstrap)

Initializes queue from existing lugs on first run.

### Step 3.1: Add Queue Detection to Wakeup Step 4
New Wakeup Step 4.5 (after loading active lugs):
```
## Step 4.5: Work Queue Bootstrap

If `_work_queue` missing from WAI-State.json:
  Trigger auto-discovery (see below)
Else:
  Continue to Step 5
```

**Files touched:**
- `templates/commands/wai.md` add Step 4.5

### Step 3.2: Implement Queue Auto-Discovery Logic
Scan lugs in priority order:
1. Hub teachings in `seed/ingest/` → priority 1
2. Inbound lugs (hub deliveries) → priority 2
3. Signals undelivered → priority 3
4. Local lugs open → priority 4 (assess ready vs needs_refinement)

For each lug, determine readiness:
- **ready:** has acceptance_criteria + estimated_steps + no unclear blockers
- **needs_refinement:** missing criteria OR blocker list unclear OR plan incomplete (if lug didn't pass dogfooding/improvement process, default to needs_refinement)

Create `_work_queue` in WAI-State.json with discovered items in priority order.

**Files touched:**
- `templates/commands/wai.md` Step 4.5 or new wai-queue-discovery.md utility

### Step 3.3: Present Queue to User
Show discovered queue:
```
"Built queue from 47 items:
 Priority 1 (Teachings): 3 ready
 Priority 2 (Inbound): 2 need refinement
 Priority 3 (Signals): 5 ready
 Priority 4 (Local): 37 ready, 8 need refinement

 [Work it] [Review refinements first] [Adjust queue manually]"
```

Allow user to:
- Start working (use queue as-is)
- Review refinements before starting
- Manually adjust priority/readiness

**Files touched:**
- `templates/commands/wai.md` Step 4.5 output

**Acceptance:**
- First wakeup auto-builds queue from current lug state
- Queue respects batch sequence (teachings → inbound → signals → local)
- Readiness assessment accurate enough for ~90% of cases
- User can adjust before starting

---

## Implementation Order

**Critical Path (blocking):**
1. Phase 1 (Routing) — 6-8 steps
2. Phase 2.1-2.2 (Queue schema) — 2 steps
3. Phase 2.3-2.6 (Wakeup/Closeout steps) — 4 steps
4. Phase 3 (Auto-discovery) — 3 steps
5. Phase 2.4-2.7 (Minimal context + auto-mode) — 3-4 steps

**Optional/High-Value:**
- Phase 2.7 (auto-mode job chaining) — depends on 1-4, high user value

**Test/Validation:**
- Dogfood: test queue discovery with current 47-item lug state
- Test: ready vs needs_refinement assessment
- Test: auto-mode chains 2-3 jobs successfully
- Test: minimal context load is actually ~20k tokens

---

## Files to Modify (Summary)

**Core**
- `WAI-Spoke/WAI-State.json` — add `_work_queue` section
- `templates/commands/wai.md` — add Steps 4.5, 9
- `templates/commands/wai-closeout.md` — add Step 10, modify Step 5c
- `templates/commands/wai-ozi-work-queue-monitor.md` — add routing gate

**Reference / Documentation**
- `WAI-Spoke/lugs/reference/lug-schema.md` — document new fields
- `WAI-Spoke/lugs/reference/lug-advisor-reference.md` — routing examples
- `templates/commands/wai-track-generate.md` — document track extensions
- `templates/commands/wai-auto-on.md` — minimal context loading

**New (Optional)**
- `templates/commands/wai-queue-discovery.md` — auto-discovery logic (or include in wai.md)

**No changes needed:**
- Lug storage structure
- Session continuity core
- Teaching discovery pipeline
- Multi-AI support

---

## Assumptions & Constraints

- Single user, sequential job execution (not parallel)
- Blocker list is simple: [lug_ids] that must complete first
- Readiness heuristics: check fields, not deep code analysis
- Auto-mode runs in same session (not cross-session auto-chains)
- Context budget: minimal context ~20k tokens (verified by Ozi at closeout before next job load)
- Lugs that don't pass dogfooding/improvement process default to needs_refinement (no skip/error)
- Routing gate is Ozi responsibility (new skill, called before lug creation)
- Full auto-chain mode: no per-job checkpoints (one approval enables chain-to-completion)

---

## Success Criteria

1. ✅ User can `Work next ready item` at wakeup
2. ✅ User can `Review items needing refinement` separately
3. ✅ Auto-mode chains jobs: implement → minimal closeout → load next
4. ✅ Track captures implementation_notes + uat_recording
5. ✅ First run auto-discovers 47-item queue, user can adjust
6. ✅ Ready/needs_refinement distinction prevents false starts
7. ✅ Minimal context load is ~57% reduction from full wakeup

---

## Dogfood Validation Checklist

Before approval, subagent should verify:
- [ ] Plan is self-contained (no missing context)
- [ ] File list is complete (no forgotten files)
- [ ] Schema changes are backward compatible
- [ ] Wakeup/Closeout steps fit naturally
- [ ] Queue logic is implementable without framework redesign
- [ ] Auto-discovery heuristics are sound (readiness check, dogfood fallback)
- [ ] Track schema extensions don't break existing tracks
- [ ] Minimal context loader respects existing session structure
- [ ] Routing gate (new skill) doesn't block normal workflows
- [ ] Status vs queue_state distinction is clear and implementable
- [ ] Token budget check at closeout is implementable (not invasive)

