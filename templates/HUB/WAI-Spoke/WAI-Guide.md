# Hub AI Assistant Guide

**For:** AI assistants managing this Wheelwright hub  
**Version:** 3.0.0  
**Auto-generated from framework**  
**Last Updated:** AUTO_TIMESTAMP

---

## READ THIS FIRST

This hub is a **Wheelwright wheel** that coordinates all other wheels. It has:

1. **WAI-Spoke/** structure (standard wheel files for self-tracking)
2. **Hub-specific files** (registry, learnings, security policy)
3. **Same update protocol** as spokes (receives framework updates via seed/ingest/)

**Critical**: Read [WAI-State.json](WAI-State.json) and [WAI-State.md](WAI-State.md) before any hub operations.

---

## Quick Start Protocol

### On First Load
1. Read [WAI-State.json](WAI-State.json) - Hub configuration and analytics
2. Read [WAI-State.md](WAI-State.md) - Hub identity and current operations
3. Read [hub-registry.json](../hub-registry.json) - Connected wheels
4. Read [hub-security-policy.json](../hub-security-policy.json) - Security settings

### During Session
1. Update `_session_state` in WAI-State.json when making changes
2. Log significant decisions in WAI-State.md evolution log
3. Track hub operations in analytics section

### On Closeout
1. Process seed/ingest/ for framework updates (upgrade-adoption-plan.json)
2. Update WAI-State files with session summary
3. Synchronize analytics and registry

---

## Hub Operations

### 1. Teaching Wheels (Distributing Framework Updates)

**When:** Framework version changes or critical updates available

**Process:**
```bash
cd <framework_path>
./WAI teach <spoke_path> <hub_path> <framework_path>
```

**What happens:**
1. Framework scans templates/WAI/ (spoke templates)
2. Framework scans templates/HUB/ (hub templates)
3. Creates upgrade-adoption-plan.json with:
   - `files` (for spokes)
   - `hub_files` (for hub itself)
   - Signatures and hashes
   - Adoption guidance
4. Distributes to spoke's seed/ingest/
5. Distributes to hub's seed/ingest/ (this hub)

**Hub adopts like any spoke:**
- Verify hub signature
- Verify file hashes
- Review adoption guidance (why_changed, mentions)
- Adopt selected files
- Archive plan in reference/

### 2. Learning from Wheels (Aggregating Knowledge)

**When:** Wheels contribute high-impact learnings (≥8/10)

**Process:**
```python
# Learning arrives from spoke
learning = {
    "id": "uuid",
    "wheel_id": "project-x",
    "category": "architecture",
    "impact_score": 9,
    "pattern": "...",
    "context": "...",
    "applicable_to": ["backend", "api"]
}

# Filter by threshold
if learning["impact_score"] >= 8:
    # Append to category file
    append_to_jsonl(f"learnings/{learning['category']}.jsonl", learning)
    
    # Update index
    update_learning_index(learning)
    
    # Update analytics
    increment_analytics("knowledge_base.categories." + learning["category"])
    increment_analytics("hub_operations.total_learnings_received")
```

**Categories:**
- architecture.jsonl
- performance.jsonl
- testing.jsonl
- security.jsonl
- workflow.jsonl
- tools.jsonl

### 3. Registry Management

**When:** Wheels added, removed, or status changes

**Update hub-registry.json:**
```json
{
  "wheels": [
    {
      "id": "wheel-uuid",
      "name": "project-name",
      "path": "/path/to/project",
      "status": "active",
      "created_at": "timestamp",
      "last_sync": "timestamp",
      "version": "3.0.0",
      "learnings_contributed": 5,
      "last_taught": "timestamp"
    }
  ],
  "teaching_history": [...]
}
```

**Update analytics:**
- Increment/decrement wheel counts
- Track registry update timestamp
- Log teaching operations

### 4. Hub Self-Update (Processing seed/ingest/)

**When:** Hub finds upgrade-adoption-plan.json in seed/ingest/

**Process:**
```python
# During closeout
from wai.spoke_update import SpokeUpdateProcessor

processor = SpokeUpdateProcessor(hub_path)
result = processor.run_update()

# Result contains:
# - ingested: Files absorbed from seed/ingest/
# - archived_reference: Files moved to reference/
# - warnings: Any issues encountered
```

**Special hub handling:**
- Process upgrade-adoption-plan.json (verify signatures)
- Update hub-specific files if in plan.hub_files
- Maintain backward compatibility with existing registry
- Preserve learnings/ directory structure

---

## Hub-Spoke Unification

### The Key Insight

**Hub = Spoke + Hub Features**

Hub uses the **same base structure** as spokes (WAI-Spoke/), enabling:
- Identical update protocol (teach command works for both)
- Self-tracking via WAI-State files
- Session continuity and analytics
- Standard closeout processing

### File Layout

```
~/wheelwright-hub/
├── WAI-Spoke/                    ← Standard spoke structure
│   ├── WAI-State.json           (hub configuration + analytics)
│   ├── WAI-State.md             (hub identity + operations)
│   ├── WAI-Guide.md             (this file, generated)
│   ├── WAI-Lugs.jsonl           (hub maintenance tasks)
│   ├── WAI-File-Index.json      (hub file tracking)
│   ├── seed/
│   │   ├── ingest/              (receives upgrade-adoption-plan.json)
│   │   └── reference/
│   └── reference/               (archived plans and history)
├── hub-registry.json             ← Hub-specific
├── hub-security-policy.json      ← Hub-specific
├── hub-learning-index.md         ← Hub-specific
├── learnings/                    ← Hub-specific
│   ├── architecture.jsonl
│   ├── performance.jsonl
│   └── ...
└── .WAI-registry/                ← Hub-specific
```

### Update Flow

**Framework teaches hub:**
```
Framework v3.1
    ↓
upgrade-adoption-plan.json
    (hub_files: ["hub-security-policy.json", ...])
    ↓
hub/WAI-Spoke/seed/ingest/
    ↓
Hub closeout processes ingest
    ↓
Hub adopts changes (verified + signed)
```

**Same as spokes**, but hub-specific files go to hub root.

---

## Security & Verification

### Hub Fingerprint

All upgrade plans signed with hub fingerprint (SHA256-HMAC):

```json
{
  "verification": {
    "hub_fingerprint": "sha256-hash",
    "created_at": "timestamp",
    "framework_version": "3.0.0"
  }
}
```

### File Integrity

Every file in plan has SHA256 hash:

```json
{
  "name": "WAI-Guide.md",
  "hash": "sha256-file-hash"
}
```

### Verification Steps

1. **Load plan** from seed/ingest/upgrade-adoption-plan.json
2. **Verify hub signature** using hub-security-policy.json
3. **Verify file hashes** before adoption
4. **Reject if tampered** with
5. **Log adoption** in reference/ for audit

---

## Decision Logic

### Should hub teach this to wheels?

✅ **YES** if:
- Framework version changed
- Critical security update
- High-impact pattern (≥8/10)
- Breaking change with migration path

❌ **NO** if:
- Experimental feature
- Hub-only change (doesn't affect spokes)
- Incomplete update

### Should hub share this learning?

✅ **YES** if:
- Impact score ≥ 8
- Applicable across projects
- Architectural insight
- Not project-specific

❌ **NO** if:
- Impact < 8
- Project-specific detail
- Temporary workaround

### Should hub adopt this update?

✅ **YES** if:
- Signature verified
- File hashes match
- safe_to_auto_adopt = true
- OR user approves manual review

❌ **NO** if:
- Signature invalid
- Hash mismatch
- Breaking change without user approval

---

## Analytics Tracking

Update these metrics during hub operations:

### Hub Operations
- `total_teach_operations` - Increment on teach
- `total_wheels_taught` - Count wheels in batch
- `total_learnings_received` - Increment on learning ingest
- `total_learnings_distributed` - Increment on broadcast

### Wheel Registry
- `total_wheels` - Count active + archived
- `active_wheels` - Count status=active
- `last_registry_update` - Timestamp

### Knowledge Base
- `total_patterns` - Sum across categories
- `categories.{name}` - Per-category counts
- `high_impact_patterns` - Count with impact ≥ 9

---

## Common Errors

### "Hub fingerprint verification failed"
- Check hub-security-policy.json exists
- Verify hub key matches framework's teaching key
- Ensure upgrade-adoption-plan.json not tampered

### "File hash mismatch"
- File modified after plan created
- Re-run teach command to regenerate plan
- Check for transmission corruption

### "Wheel not found in registry"
- Run `WAI hub scan` to refresh registry
- Check wheel path still valid
- Update registry manually if needed

---

## Related Files

- **[WAI-State.json](WAI-State.json)** - Hub configuration and analytics
- **[WAI-State.md](WAI-State.md)** - Hub identity and operations
- **[WAI-Lugs.jsonl](WAI-Lugs.jsonl)** - Hub maintenance tasks
- **[../hub-registry.json](../hub-registry.json)** - Wheel tracking
- **[../hub-security-policy.json](../hub-security-policy.json)** - Security settings
- **[../hub-learning-index.md](../hub-learning-index.md)** - Knowledge base
- **[../learnings/](../learnings/)** - Aggregated patterns

---

## Session Protocol

### Session Start
1. Load WAI-State.json (hub configuration)
2. Check for pending updates in seed/ingest/
3. Review current operations in WAI-State.md
4. Load session context from _session_state

### During Work
1. Update _session_state on significant changes
2. Log decisions in WAI-State.md
3. Track analytics in real-time
4. Maintain hub-registry.json as wheels change

### Session Closeout
1. Process seed/ingest/ (run update)
2. Reconcile WAI-State files
3. Archive session logs
4. Update analytics and registry
5. Clear current_session

---

**This file is auto-generated from templates/HUB/AGENTS.md during hub initialization.**
**Manual edits will be overwritten on framework updates.**
**To customize, modify the template in the framework repository.**

---

*Hub Guide for Wheelwright Framework v3.0*
