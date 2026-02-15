# Teaching Reconciliation Strategy for Wheelwright v3

**Date:** 2026-02-01  
**Status:** Design & Implementation Plan  
**Epic Lug:** `a2f7e9c4b1d6`

---

## Overview

**UPDATED:** Teaching now uses **upgrade-adoption-plan.json** with hub fingerprint verification and context. Hub and spokes use unified teach/learn protocol.

Teaching files (`.teaching` files in `WAI-Spoke/seed/ingest/`) are processed by closeout and matched against **upgrade-adoption-plan.json** - a signed, versioned manifest that tells the spoke (or hub) what changed, why, and whether to adopt it.

---

## Current Flow (v3.0.0)

```
1. User runs: WAI teach
   ↓
2. Framework copies templates to WAI-Spoke/seed/ingest/*.teaching
   ↓
3. User runs: WAI closeout
   ↓
4. Closeout processes:
   - Moves .teaching files to WAI-Spoke/reference/auto/_framework/
   - Cleans ingest folder
   - ✗ Does NOT automatically adopt root files
   ↓
5. Next session:
   - AI sees reference/auto/_framework/ files
   - ✗ No automatic briefing of pending teachings
   - ✗ No adoption prompt
```

**Problem:** Knowledge is taught but not integrated into workflow.

---

## Desired Flow (v3.1+)

```
Teaching Files → Process → Reconcile → Propose Adoption → Integrate
```

### Trigger Points for Reconciliation

#### 1. **On Closeout Completion**
When closeout finishes Step 3 (Seed Folders & Cleanup):

```python
def _process_seed_and_cleanup(self, interactive=True):
    # ... existing code ...
    
    # NEW: Reconcile teachings after processing
    teaching_reconciliation = self._reconcile_teachings(interactive)
    results['teaching_reconciliation'] = teaching_reconciliation
    
    return results
```

**What it does:**
- Scan `reference/auto/_framework/` for taught files
- Compare with current root files (WAI-State.json, WAI-Guide.md, etc.)
- Build adoption manifest:
  - Files to adopt immediately (no conflicts)
  - Files needing manual review (conflicts detected)
  - Files to defer
- Save adoption plan to `WAI-Spoke/teaching-adoption-plan.json`

#### 2. **On Session Start / WAI Wakeup**
In hook: `.claude/hooks/user-prompt-submit.sh` or session-start protocol:

```bash
# Generate Session Focus briefing that includes:
echo "## Pending Teachings"
echo ""
echo "Taught files available for adoption:"
echo "  • WAI-Guide.md (updated 2026-02-01)"
echo "  • WAI-Point.json (new)"
echo ""
echo "Review: WAI-Spoke/teaching-adoption-plan.json"
```

**What it does:**
- Detects `teaching-adoption-plan.json` exists
- Shows pending teachings in Session Focus briefing
- Prompts user: "Review taught files before starting work?"

#### 3. **On New Session with Pending Teachings**
AI sees briefing and prompts:

```
## Pending Teachings (Review Required)

Taught files are ready for adoption:
  ✓ WAI-Guide.md (can adopt immediately - no conflicts)
  ⚠️ WAI-State.json (needs review - version differs)
  • WAI-State.md (waiting for decision)

Would you like to:
1. Review & adopt teachings now
2. Defer to next session
3. Discard teachings

```

---

## Data Structures

### Teaching Adoption Plan (`teaching-adoption-plan.json`)

```json
{
  "generated_at": "2026-02-01T18:30:00Z",
  "teachings": [
    {
      "filename": "WAI-Guide.md",
      "source": "reference/auto/_framework/WAI-Guide.md",
      "destination": "WAI-Spoke/WAI-Guide.md",
      "status": "ready",
      "reason": "Framework template update",
      "conflicts": false,
      "action": "adopt"
    },
    {
      "filename": "WAI-State.json",
      "source": "reference/auto/_framework/WAI-State.json",
      "destination": "WAI-Spoke/WAI-State.json",
      "status": "review_needed",
      "reason": "Local modifications exist",
      "conflicts": true,
      "current_version": "2026-01-31T12:00:00Z",
      "taught_version": "2026-02-01T18:12:00Z",
      "action": "defer"
    }
  ],
  "summary": {
    "total": 2,
    "ready": 1,
    "review_needed": 1,
    "recommended_action": "adopt_ready_files_then_review_conflicts"
  }
}
```

### Session Focus Briefing (from wai-briefing.sh)

```markdown
## Pending Teachings

**2 files waiting for adoption:**

| File | Status | Action |
|------|--------|--------|
| WAI-Guide.md | ✓ Ready | Adopt |
| WAI-State.json | ⚠️ Review | Decide |

**Next step:** Say "Review teachings" to see detailed comparison
```

---

## Implementation Plan

### Phase 1: Closeout Reconciliation (v3.1)
- [ ] Implement `_reconcile_teachings()` in closeout.py
- [ ] Generate `teaching-adoption-plan.json`
- [ ] Test with sample teachings
- [ ] Update closeout results to show teaching summary

### Phase 2: Session Start Briefing (v3.2)
- [ ] Update wai-briefing.sh to include pending teachings section
- [ ] Update CLAUDE.md session start protocol
- [ ] Add teaching adoption prompt to hook injection message

### Phase 3: Adoption Workflow (v3.3)
- [ ] Add "review-teachings" command
- [ ] Implement adoption decision logic
- [ ] Add conflict resolution UI
- [ ] Update WAI-Guide.md with adoption patterns

### Phase 4: Testing & Hardening (v3.4)
- [ ] Integration tests for teach→closeout→adoption cycle
- [ ] Test conflict detection
- [ ] Test multi-file adoption
- [ ] Security audit of file operations

---

## Related Lugs

| ID | Title | Status |
|----|-------|--------|
| `c7f2e9a4b1d6` | Reimplement WAI CLI | Blocked by test coverage |
| `f8e2c5a3d9b1` | Test Coverage Review | In progress |
| `d4a7f1b6e8c2` | Architecture Review | In progress |
| `a2f7e9c4b1d6` | Teaching Reconciliation | This epic |

---

## Files Affected

### Modified:
- `wai/closeout.py` - Add `_reconcile_teachings()`
- `.claude/hooks/user-prompt-submit.sh` - Add pending teachings briefing
- `CLAUDE.md` - Document adoption workflow

### New:
- `WAI-Spoke/teaching-adoption-plan.json` - Generated by closeout
- `wai/commands/teach-adoption.py` - Adoption workflow implementation

### Updated Docs:
- This file
- WAI-Guide.md (adoption patterns section)

---

## Success Criteria

✓ Users can teach from framework  
✓ Closeout processes and reconciles teachings  
✓ Session start shows pending teachings  
✓ AI prompts for adoption decisions  
✓ Adoptions tracked in WAI-Lugs.jsonl  
✓ Full test coverage for teach→adoption cycle  

---

## WAI-State Files Status

**NOT DEPRECATED.** WAI-State.json and WAI-State.md are core project files:
- **WAI-State.json**: Machine-readable project state, decisions, analytics
- **WAI-State.md**: Human-readable strategic vision and evolution

Both are **versioned templates** in `templates/WAI/` and distributed via teach.

Teaching allows framework improvements to flow to all spokes via:
```
Framework v3.0.0 (templates/WAI/)
    ↓ teach command
All spokes (WAI-Spoke/reference/auto/_framework/)
    ↓ reconciliation
Adopted into root WAI-Spoke/
```

---

## Next Session

When user opens new session:
1. Hook detects `teaching-adoption-plan.json`
2. Briefing shows "2 pending teachings"
3. AI prompts for adoption before other work
4. User decides: adopt, review, or defer
5. Adopted files are integrated; plan is archived

---

*Strategy document for teaching reconciliation epic (a2f7e9c4b1d6)*
