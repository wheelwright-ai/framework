# Unified Lug System Specification v3.1

**Framework:** Wheelwright  
**Version:** 3.1.0  
**Date:** 2026-02-03  
**Status:** Documented & Ready for Implementation

---

## Executive Summary

A **unified, predictable lug system** for hub-spoke knowledge exchange:
- **Single schema** everywhere (WAI-Lugs.jsonl)
- **Single location** per wheel (no outbound/inbound folders)
- **Push-based routing** (hub routes to spokes during TEACH)
- **Bidirectional flow** (hub ↔ spokes via TEACH/LEARN)

---

## Core Concepts

### Lug

**Definition:** A delivery container for knowledge, tasks, feedback, and signals.

**Purpose:** Enables predictable, structured communication between hub and spokes.

**Single Location Per Wheel:**
```
Spoke: spoke/WAI-Spoke/WAI-Lugs.jsonl
Hub:   hub/WAI-Hub/WAI-Lugs.jsonl
```

### Unified Schema

Every lug, everywhere, follows this structure:

```json
{
  "id": "uuid-unique-lug-identifier",
  "created_at": "2026-02-03T10:00:00Z",
  "source_wheel_id": "project-x or hub",
  "destination_wheel_id": "project-y or hub or null (self-lug)",
  "category": "learning|feedback|task|signal|update",
  "priority": 1-5,
  "content": { "...": "lug-specific content" },
  "status": "pending|in_progress|delivered|processed|archived|rejected",
  "expires_at": "2026-03-01T00:00:00Z or null (keep forever)",
  "metadata": { "custom_field": "value", "related_lug_ids": [...] }
}
```

**Core Fields:**
- `id` - Unique identifier (UUID)
- `created_at` - Timestamp when lug created
- `source_wheel_id` - Origin (spoke name or "hub")
- `destination_wheel_id` - Target (spoke name, "hub", or null for self)
- `category` - Type of content (learning|feedback|task|signal|update)
- `priority` - Importance (1-5, where 5 is critical)
- `content` - Lug-specific payload (varies by category)
- `status` - Current state in lifecycle
- `expires_at` - Optional expiration (null = keep forever)
- `metadata` - Extensible custom fields

---

## Lug Categories

### 1. Learning
**Purpose:** High-impact insights from spokes  
**Threshold:** Impact score ≥ 8/10  
**Processing:** Extracted to hub/learnings/{category}.jsonl  
**Retention:** Permanent (unless expired)

**Example:**
```jsonl
{
  "id": "lug-learning-001",
  "created_at": "2026-02-03T10:00:00Z",
  "source_wheel_id": "project-x",
  "destination_wheel_id": "hub",
  "category": "learning",
  "priority": 5,
  "content": {
    "title": "Caching strategy reduces API calls by 40%",
    "pattern": "Multi-tier cache with TTL invalidation",
    "impact_score": 9,
    "applicable_to": ["backend", "api"],
    "context": "Observed in production over 2 weeks"
  },
  "status": "pending",
  "metadata": { "framework_version": "3.0.0" }
}
```

### 2. Feedback
**Purpose:** Hub notifications, acknowledgments, responses  
**Processing:** Stored in hub/WAI-Hub/WAI-Lugs.jsonl  
**Retention:** Configurable (expires_at)  
**Example:**
```jsonl
{
  "id": "lug-feedback-001",
  "created_at": "2026-02-03T11:00:00Z",
  "source_wheel_id": "hub",
  "destination_wheel_id": "project-x",
  "category": "feedback",
  "priority": 3,
  "content": {
    "regarding_lug_id": "lug-task-123",
    "message": "Your learning contribution was invaluable",
    "action_taken": "Added to architecture.jsonl"
  },
  "status": "pending",
  "expires_at": "2026-02-17T00:00:00Z"
}
```

### 3. Task
**Purpose:** Hub directives for spokes to execute  
**Processing:** Stored in hub/WAI-Hub/WAI-Lugs.jsonl (for hub to track)  
**Retention:** Until status="archived"  
**Example:**
```jsonl
{
  "id": "lug-task-hub-001",
  "created_at": "2026-02-03T11:00:00Z",
  "source_wheel_id": "hub",
  "destination_wheel_id": "project-x",
  "category": "task",
  "priority": 5,
  "content": {
    "action": "adopt_security_policy_v3.1",
    "reason": "Critical fingerprint rotation requirement",
    "deadline": "2026-02-10T00:00:00Z",
    "resources": ["upgrade-adoption-plan.json"]
  },
  "status": "pending",
  "metadata": { "depends_on": ["WAI-Guide.md v3.1"] }
}
```

### 4. Signal
**Purpose:** Operational events, notifications, alerts  
**Processing:** Logged in WAI-State.md  
**Retention:** Audit trail (permanent)  
**Example:**
```jsonl
{
  "id": "lug-signal-001",
  "created_at": "2026-02-03T12:00:00Z",
  "source_wheel_id": "project-x",
  "destination_wheel_id": "hub",
  "category": "signal",
  "priority": 4,
  "content": {
    "event": "adoption_complete",
    "target": "upgrade-adoption-plan.json v3.0.0",
    "details": "All files adopted successfully"
  },
  "status": "logged"
}
```

### 5. Update
**Purpose:** Framework/tool updates to distribute  
**Processing:** Included in next TEACH cycle  
**Retention:** Until processed  
**Example:**
```jsonl
{
  "id": "lug-update-001",
  "created_at": "2026-02-03T13:00:00Z",
  "source_wheel_id": "hub",
  "destination_wheel_id": "project-y",
  "category": "update",
  "priority": 4,
  "content": {
    "component": "WAI-Lugs system",
    "version": "3.1.0",
    "type": "feature",
    "description": "Unified lug routing"
  },
  "status": "pending"
}
```

---

## Data Flow

### TEACH Flow (Hub → Spokes)

```
Hub creates/updates lug
    ↓
hub/WAI-Hub/WAI-Lugs.jsonl (destination_wheel_id="project-x")
    ↓
TEACH command triggered
    ↓
Find all lugs: destination_wheel_id="<spoke-name>" AND status="pending"
    ↓
Append to spoke/WAI-Spoke/WAI-Lugs.jsonl
    ↓
Mark status="delivered" in hub/WAI-Hub/WAI-Lugs.jsonl
    ↓
Spoke receives lugs + upgrade-adoption-plan.json in seed/ingest/
    ↓
Spoke processes lugs by category
    ↓
Creates response lugs (destination_wheel_id="hub")
```

### LEARN Flow (Spokes → Hub)

```
Spoke processes/responds to hub lugs
    ↓
Creates new lugs: destination_wheel_id="hub"
    ↓
Stores in spoke/WAI-Spoke/WAI-Lugs.jsonl
    ↓
Next WAI wake or explicit LEARN command
    ↓
Hub finds: source_wheel_id="<spoke>" AND destination_wheel_id="hub"
    ↓
Process by category:
  - learning (≥8) → hub/learnings/{category}.jsonl
  - feedback → hub/WAI-Hub/WAI-Lugs.jsonl
  - task → hub/WAI-Hub/WAI-Lugs.jsonl
  - signal → WAI-State.md log
    ↓
Append processed lugs to hub/WAI-Hub/WAI-Lugs.jsonl
    ↓
Mark status="processed" (or "delivered" for audit)
```

---

## Lug Lifecycle

### States

```
pending
  ↓ (processing begins)
in_progress
  ↓ (processing complete or delivered)
delivered (for routed lugs) / processed (for hub lugs)
  ↓ (cleanup cycle)
archived
  ↓ (optional)
rejected (if validation fails)
```

### Reconciliation Cycle

Hub reconciliation triggered on:
1. **Closeout** (end of session)
2. **Explicit command:** `WAI hub reconcile`
3. **Automated:** On schedule (configurable)

**Reconciliation Steps:**
1. Scan hub/WAI-Hub/WAI-Lugs.jsonl for pending lugs
2. Route spoke-bound lugs (destination_wheel_id="<spoke-name>")
3. Append to spoke/WAI-Spoke/WAI-Lugs.jsonl
4. Mark status="delivered"
5. Pull spoke contributions (source_wheel_id="<spoke>")
6. Process by category
7. Update hub-registry.json
8. Log in WAI-State.md

---

## Decision Logic

### Should this lug be routed to a spoke?

✅ **YES** if:
- Lug has `destination_wheel_id` matching an active spoke
- Status is "pending" (not yet delivered)
- Not expired (`expires_at` is null or future timestamp)
- Hub has routing authority for this lug type

❌ **NO** if:
- destination_wheel_id is null (self-lug) or "hub"
- Spoke not found in hub-registry.json
- Lug expired
- Status already "delivered" or "archived"

### Should hub accept this spoke-contributed lug?

✅ **YES** if:
- Source wheel found in hub-registry.json
- Category recognized (learning|feedback|task|signal|update)
- Status is "pending" or "in_progress"
- Content valid for processing

❌ **NO** if:
- Source wheel unknown
- Malformed content
- Status already processed
- Does not match hub's acceptance criteria

### Should we extract this learning to learnings/*.jsonl?

✅ **YES** if:
- Category is "learning"
- Impact score ≥ 8
- Applicable across projects
- Not project-specific

❌ **NO** if:
- Impact < 8
- Project-specific workaround
- Temporary fix (not architectural)
- Sensitive business logic

---

## Implementation Checklist

### Phase 2 Complete ✅
- [x] Define unified lug schema
- [x] Document lug categories
- [x] Document TEACH/LEARN flows
- [x] Document decision logic
- [x] Update WAI-Guide.md
- [x] Update HUB/AGENTS.md

### Phase 3 (Next)
- [ ] Implement TEACH lug routing (hub → spokes)
- [ ] Implement LEARN lug processing (spokes → hub)
- [ ] Implement `WAI hub reconcile` command
- [ ] Implement lug reconciliation on closeout
- [ ] Add lug validation (schema, content)
- [ ] Add lug expiration handling

### Phase 4
- [ ] Implement spoke-side lug processing
- [ ] Test end-to-end bidirectional lug flow
- [ ] Add monitoring/analytics for lug flow
- [ ] Create lug debugging tools
- [ ] Document troubleshooting guide

---

## Example Scenarios

### Scenario 1: Hub Distributes Security Task

```
1. Hub creates lug (category=task):
   {
     "id": "lug-sec-001",
     "source_wheel_id": "hub",
     "destination_wheel_id": "project-x",
     "category": "task",
     "content": { "action": "rotate_fingerprints_v3.1" },
     "status": "pending"
   }

2. Appends to hub/WAI-Hub/WAI-Lugs.jsonl

3. On next TEACH:
   - Hub finds this lug
   - Appends to project-x/WAI-Spoke/WAI-Lugs.jsonl
   - Marks status="delivered"

4. Project-x AI assistant wakes:
   - Reads project-x/WAI-Spoke/WAI-Lugs.jsonl
   - Finds task lug
   - Executes task
   - Creates feedback lug (destination_wheel_id="hub")
   - Marks status="in_progress"

5. On next LEARN:
   - Hub finds feedback from project-x
   - Processes feedback
   - Marks original task status="archived"
```

### Scenario 2: Spoke Contributes Learning

```
1. Project-x AI learns something valuable (impact=9):
   {
     "id": "lug-learn-001",
     "source_wheel_id": "project-x",
     "destination_wheel_id": "hub",
     "category": "learning",
     "content": {
       "title": "Async pattern reduces latency",
       "impact_score": 9,
       "applicable_to": ["api", "backend"]
     },
     "status": "pending"
   }

2. Appends to project-x/WAI-Spoke/WAI-Lugs.jsonl

3. On next TEACH (hub → project-x):
   - Also pulls project-x's pending destination_wheel_id="hub" lugs
   - Appends to hub/WAI-Hub/WAI-Lugs.jsonl
   - OR waits for explicit LEARN

4. On LEARN:
   - Hub finds learning lug (impact ≥ 8)
   - Extracts to hub/learnings/performance.jsonl
   - Updates hub-learning-index.md
   - Marks lug status="processed"
   - Increments analytics

5. Next TEACH to all spokes:
   - Hub creates feedback lug thanking project-x
   - Other spokes can now see learning in hub/learnings/
```

---

## Benefits

| Aspect | Benefit |
|--------|---------|
| **Predictability** | Single location per wheel, consistent schema everywhere |
| **Simplicity** | No outbound/inbound folders, single file per wheel |
| **Push-based** | Hub controls routing during TEACH (no pulling) |
| **Bidirectional** | Hub ↔ Spokes can exchange any content type |
| **Extensibility** | Metadata field allows custom properties |
| **Auditability** | Every lug tracked with status and timestamps |
| **Expiration** | Optional cleanup via expires_at |
| **Categorization** | Clear routing logic based on category |

---

## Status

✅ **Specification Complete**  
✅ **Documentation Complete (WAI-Guide.md + HUB/AGENTS.md)**  
⏳ **Implementation Ready for Phase 3**

---

*Unified Lug System v3.1 - Wheelwright Framework*  
*Simple | Predictable | Powerful*
