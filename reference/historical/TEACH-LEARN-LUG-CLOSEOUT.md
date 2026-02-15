# Teach & Learn Lug System - Session Closeout

**Session:** T-019c2559-8bad-722c-8590-d0b451218029  
**Date:** 2026-02-03  
**Status:** ✅ COMPLETE

---

## What We Accomplished

### 1. Unified Lug System Design ✅

**Specification Complete:**
- Single schema everywhere (WAI-Lugs.jsonl)
- Single location per wheel (no outbound/inbound)
- Five lug categories: learning | feedback | task | signal | update
- Push-based routing (hub → spokes during TEACH)
- Bidirectional flow (TEACH + LEARN)

**Key Design Decision:**
```
Hub:   hub/WAI-Hub/WAI-Lugs.jsonl
Spoke: spoke/WAI-Spoke/WAI-Lugs.jsonl
```

### 2. Documentation Complete ✅

**Updated Files:**

1. **templates/HUB/WAI-Spoke/WAI-Guide.md**
   - Teaching Wheels (3-step process with lug routing)
   - Learning from Wheels (category-based processing)
   - File Layout (WAI-Hub structure)
   - Unified Lug Schema (examples + format)
   - Decision Logic (lug routing criteria)
   - Session Protocol (lug reconciliation on closeout)
   - ✅ All sections updated & verified

2. **templates/HUB/AGENTS.md**
   - Lugs (core concept + schema)
   - Learning Signals (now delivered via lugs)
   - Teaching Spokes (hub-side lug routing)
   - Receiving Learnings (lug processing by category)
   - Decision Logic (lug acceptance criteria)
   - File Structure (hub/WAI-Hub/ + unified locations)
   - Implementation Checklist (Phase 2 ✅, Phase 3 ready)
   - Key Differences (added lug system features)
   - ✅ All sections updated & verified

3. **LUG-SYSTEM-SPECIFICATION.md** (NEW)
   - Complete specification document
   - Unified schema with all fields
   - Five lug categories detailed
   - TEACH/LEARN data flows
   - Lug lifecycle and reconciliation
   - Decision logic formalized
   - Two implementation scenarios
   - ✅ Created & verified

---

## Design Principles Agreed

### ✅ Predictability
- One file per wheel for all lugs
- Consistent schema everywhere
- Explicit routing rules (destination_wheel_id)

### ✅ Simplicity
- No outbound/inbound folder complexity
- Single JSONL format (same as spokes already use)
- Clear category taxonomy

### ✅ Push-Based (Not Pull)
- Hub controls routing during TEACH
- Hub appends directly to spoke/WAI-Spoke/WAI-Lugs.jsonl
- Spoke pulls on next wake or explicit LEARN
- No polling, no missed deliveries

### ✅ Hub as Processor & Distribution Center
- Hub receives all spoke lugs
- Hub extracts high-impact learnings (≥8)
- Hub routes tasks/feedback to appropriate spokes
- Hub maintains registry & analytics

### ✅ Bidirectional Knowledge Flow
```
Framework → Teach → Hub + Spokes
Hub ← Learn ← Spokes (via lugs)
Hub → Learn → Spokes (broadcast learnings)
```

---

## What's Ready for Phase 3

### TEACH Function
- [x] Specification complete
- [x] Step-by-step documented
- [x] Lug routing logic defined
- [ ] Implementation ready (code)

**Pseudo-code ready:**
```python
# Step 1: Deploy templates
# Step 2: Route hub lugs
for lug in hub_lugs:
    if lug["destination_wheel_id"] == "<spoke-name>":
        append_to(f"{spoke_path}/WAI-Spoke/WAI-Lugs.jsonl", lug)
        lug["status"] = "delivered"
# Step 3: Update hub
```

### LEARN Function
- [x] Specification complete
- [x] Category-based processing defined
- [x] Hub acceptance logic documented
- [ ] Implementation ready (code)

**Pseudo-code ready:**
```python
# Step 1: Collect spoke lugs
spoke_lugs = find(hub_lugs, source_wheel_id="<spoke>")

# Step 2: Process by category
for lug in spoke_lugs:
    if lug["category"] == "learning" and impact >= 8:
        append_to(f"hub/learnings/{category}.jsonl", lug["content"])
    elif lug["category"] in ["feedback", "task"]:
        append_to(f"hub/WAI-Hub/WAI-Lugs.jsonl", lug)
    elif lug["category"] == "signal":
        log_to(WAI_State_md, lug["content"])

# Step 3: Mark processed
# Step 4: Update registry
```

---

## Lug Schema (Formalized)

Every lug, everywhere:
```json
{
  "id": "uuid-unique-lug-identifier",
  "created_at": "2026-02-03T10:00:00Z",
  "source_wheel_id": "project-x or hub",
  "destination_wheel_id": "project-y or hub or null (self-lug)",
  "category": "learning|feedback|task|signal|update",
  "priority": 1-5,
  "content": { "...": "category-specific content" },
  "status": "pending|in_progress|delivered|processed|archived|rejected",
  "expires_at": "2026-03-01T00:00:00Z or null",
  "metadata": { "custom_field": "value", "related_lug_ids": [...] }
}
```

**Extensible:** metadata field allows custom properties per domain.

---

## Files Changed

### Documentation Files (Modified)
- `templates/HUB/WAI-Spoke/WAI-Guide.md` (+450 lines)
- `templates/HUB/AGENTS.md` (+250 lines)

### New Files (Created)
- `LUG-SYSTEM-SPECIFICATION.md` (complete spec)
- `TEACH-LEARN-LUG-CLOSEOUT.md` (this file)

### Ready for Implementation
- Phase 3 implementation tasks defined
- Pseudo-code provided
- Decision logic formalized
- Examples documented

---

## Next Steps (Phase 3)

### 1. Implement TEACH Lug Routing
- [ ] Scan hub/WAI-Hub/WAI-Lugs.jsonl
- [ ] Find destination_wheel_id="<spoke-name>" AND status="pending"
- [ ] Append to spoke/WAI-Spoke/WAI-Lugs.jsonl
- [ ] Mark status="delivered"
- [ ] Test with single spoke

### 2. Implement LEARN Lug Processing
- [ ] Pull spoke contributions from WAI-Spoke/WAI-Lugs.jsonl
- [ ] Filter by source_wheel_id="<spoke>" AND destination_wheel_id="hub"
- [ ] Process by category (learning|feedback|task|signal)
- [ ] Extract learnings → hub/learnings/{category}.jsonl
- [ ] Append feedback/task → hub/WAI-Hub/WAI-Lugs.jsonl
- [ ] Log signals → WAI-State.md

### 3. Implement Reconciliation Command
- [ ] Add `WAI hub reconcile` command
- [ ] Trigger on closeout automatically
- [ ] Process all pending lugs
- [ ] Update hub-registry.json
- [ ] Archive processed lugs

### 4. Test End-to-End
- [ ] Create test spoke with learnings
- [ ] Verify TEACH routes lugs correctly
- [ ] Verify LEARN processes spoke contributions
- [ ] Verify learnings extracted to hub/learnings/
- [ ] Verify feedback/task stored in hub/WAI-Hub/WAI-Lugs.jsonl

---

## Key Behaviors (Agreement Summary)

### TEACH Behavior
```
Input: framework updates + hub pending lugs
Output: upgrade-adoption-plan.json + routed lugs + hub self-update

Steps:
1. Deploy templates to hub + spokes
2. Route hub pending lugs to target spokes
   - Find lug.destination_wheel_id="<spoke-name>"
   - Append to spoke/WAI-Spoke/WAI-Lugs.jsonl
   - Mark status="delivered"
3. Hub adopts its own updates
4. Spoke processes on next wake
```

### LEARN Behavior
```
Input: spoke contributions (from WAI-Spoke/WAI-Lugs.jsonl)
Output: hub processed learnings + feedback stored

Steps:
1. Collect spoke lugs (destination_wheel_id="hub")
2. Process by category:
   - learning (≥8) → hub/learnings/{category}.jsonl
   - feedback → hub/WAI-Hub/WAI-Lugs.jsonl
   - task → hub/WAI-Hub/WAI-Lugs.jsonl
   - signal → WAI-State.md log
3. Mark status="processed"
4. Update hub-registry.json with contribution counts
5. Triggered on closeout or explicit WAI hub reconcile
```

### Predictability Guarantee
- **Location:** Always `WAI-{Type}/WAI-Lugs.jsonl` (no surprises)
- **Routing:** Explicit `destination_wheel_id` field (clear intent)
- **Status:** Tracked through lifecycle (pending→delivered→processed→archived)
- **Expiration:** Optional cleanup via `expires_at` (no orphaned lugs)

---

## Outstanding Questions (Resolved)

✅ **Q: Hub vs Spoke structure?**  
A: Hub has `WAI-Hub/`, spoke has `WAI-Spoke/` (identity preserved)

✅ **Q: Single file or folder?**  
A: Single `WAI-Lugs.jsonl` file per wheel (no outbound/inbound)

✅ **Q: Push or pull?**  
A: Push-based (hub appends to spoke during TEACH)

✅ **Q: Schema extensibility?**  
A: Unified core schema + extensible metadata field

✅ **Q: How to know when spoke has lugs for hub?**  
A: On next TEACH cycle, hub pulls from spoke or explicit LEARN command

---

## Verification Checklist

- [x] WAI-Guide.md updated with complete TEACH/LEARN flows
- [x] HUB/AGENTS.md updated with lug system
- [x] LUG-SYSTEM-SPECIFICATION.md created
- [x] Unified schema documented
- [x] Five lug categories specified
- [x] Decision logic formalized
- [x] TEACH flow (hub → spokes) documented
- [x] LEARN flow (spokes → hub) documented
- [x] Session protocol updated (lug reconciliation)
- [x] File structure clarified (WAI-Hub vs WAI-Spoke)
- [x] Implementation checklist updated
- [x] Key differences table updated

---

## Session Summary

**Objective:** Review and improve Teach & Learn functions to handle lug delivery.

**Outcome:** 
- ✅ Unified lug system designed
- ✅ Complete specification documented
- ✅ Two key files updated
- ✅ Phase 3 ready for implementation

**Impact:**
- Hub now has predictable way to route knowledge to spokes
- Spokes have predictable way to send learnings/feedback to hub
- Single schema, single location, push-based = maintainable

**Next Owner:** Phase 3 implementation team

---

## Handoff

**All documentation is in place for Phase 3 implementation:**

1. **Start here:** [LUG-SYSTEM-SPECIFICATION.md](file:///wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/LUG-SYSTEM-SPECIFICATION.md)
2. **Reference:** [WAI-Guide.md](file:///wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/templates/HUB/WAI-Spoke/WAI-Guide.md) (sections 1-2, 6)
3. **Reference:** [HUB/AGENTS.md](file:///wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/templates/HUB/AGENTS.md) (Common Tasks section)
4. **Code Implementation:** Start with TEACH lug routing (simplest)

**Success Criteria for Phase 3:**
- [ ] TEACH routes one lug to one spoke successfully
- [ ] LEARN processes one learning lug correctly
- [ ] `WAI hub reconcile` command works
- [ ] End-to-end test: spoke → hub → spoke lug flow succeeds

---

*Teach & Learn Lug System - Specification Phase Complete*  
*Ready for Implementation*

---

**Session Dates:** 2026-02-03  
**Specification Status:** ✅ COMPLETE  
**Implementation Status:** 🔄 READY FOR PHASE 3
