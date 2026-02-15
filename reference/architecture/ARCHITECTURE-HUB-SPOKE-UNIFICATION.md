# Hub-Spoke Unification Architecture

**Date:** 2026-02-01  
**Decision:** Make hub and spokes use identical teach/learn protocol  
**Impact:** Transforms framework from hub-centric to network-centric

---

## The Insight

**Current Design:**
- Framework → Teaches to Spokes (one-way)
- Spokes → Learn to Hub (separate protocol)
- Hub is special; spokes are leaf nodes

**Problem:** Different protocols, duplicated logic, limited knowledge flow

**New Design:**
- Hub = Spoke + Hub Features (same base)
- Universal teach/learn protocol
- Bidirectional knowledge flow
- Network of peers, not hub-and-spoke topology

---

## Three Architectural Changes

### 1. **Upgrade Adoption Plan (Security + Context)**

**File:** `upgrade-adoption-plan.json` (signed, versioned manifest)

```
teach command
    ↓
Creates upgrade-adoption-plan.json with:
  • Hub fingerprint (security)
  • File hashes (integrity)
  • Why changed (AI context)
  • Mentions (AI decisions)
  • Applies to (hub/spoke/universal)
    ↓
Distribute to spoke/hub
    ↓
Spoke/Hub verifies signature
    ↓
AI sees context, proposes adoption
    ↓
Bidirectional knowledge flow
```

**Key:** No guessing. File tells AI everything it needs to decide.

### 2. **Hub Templates Directory**

**New:** `templates/HUB/` alongside `templates/WAI/` and `templates/wheel/`

```
templates/
├── WAI/              (spoke core templates)
│   ├── WAI-Guide.md
│   ├── WAI-State.json
│   └── WAI-State.md
├── HUB/              (hub-specific NEW)
│   ├── hub-profile.json
│   ├── hub-registry.json
│   ├── hub-learning-index.md
│   ├── hub-security-policy.json
│   └── AGENTS.md
└── wheel/            (existing)
```

**Effect:** Hub can now self-improve via teach, just like spokes.

### 3. **Universal Protocol**

**Before:**
```
Framework → teach → Spokes
Hub ←----- learn -← Spokes (different mechanism)
```

**After:**
```
        Framework v3.0.0
              ↓
    Upgrade Adoption Plan
        ↙        ↘
      Spokes    Hub
        ↓        ↓
   (same logic for adoption)
        ↓        ↓
   Knowledge ← Shared State → Knowledge
        ↓        ↓
      Hub learns from all
```

---

## Why This Matters

### For Users:
- **Hub learns continuously** from all spokes
- **Spokes improve automatically** from hub improvements
- **No special cases** - hub and spoke code paths identical
- **Knowledge network** instead of centralized distribution

### For AI:
- **Single teach/learn pattern** to learn
- **Signed upgrades** mean trust
- **Context in adoption plan** means intelligent decisions
- **Bidirectional flow** means knowledge actually compounds

### For Architecture:
- **Standardization** - one protocol, not two
- **Scalability** - can add more hubs, all peers
- **Resilience** - knowledge doesn't centralize
- **Evolution** - hub/spoke distinction becomes implementation detail

---

## Implementation Roadmap

### v3.1 (Next Release)

**Sprint 1: Upgrade Adoption Plan**
- Spec: ✓ UPGRADE-ADOPTION-PLAN-SPEC.md created
- Lug: `g5h8j2k9m3n7` (High priority)
- Implement teach command with fingerprinting
- Add verify-upgrade command
- Update closeout to verify before adopting

**Sprint 2: Hub Templates**
- Spec: Create templates/HUB/ structure
- Lug: `p2q6r9s4t8u1` (High priority)
- Implement hub-profile.json template
- Implement hub-registry.json template
- Implement hub-learning-index.md template

**Sprint 3: Universal Protocol**
- Lug: `v3w7x1y5z9a4` (High priority)
- Update teach to handle hub files
- Update hub adoption logic (same as spoke)
- Bidirectional learning setup
- End-to-end testing

### v3.2 (Following Release)

- Full test coverage (spoke + hub)
- Performance optimization
- Security hardening (fingerprint rotation, revocation)
- Documentation

---

## File Changes Required

### New Files:
```
templates/HUB/
  ├── hub-profile.json
  ├── hub-registry.json
  ├── hub-learning-index.md
  ├── hub-security-policy.json
  └── AGENTS.md

UPGRADE-ADOPTION-PLAN-SPEC.md (✓ created)
ARCHITECTURE-HUB-SPOKE-UNIFICATION.md (this file)
```

### Modified Files:
```
wai/commands/teach.py
  - Generate upgrade-adoption-plan.json (not .teaching)
  - Sign with hub fingerprint
  - Include context fields

wai/closeout.py
  - Load upgrade-adoption-plan.json
  - Verify hub signature
  - Verify file hashes
  - Show adoption guidance

.claude/hooks/user-prompt-submit.sh
  - Detect upgrade-adoption-plan.json
  - Show pending upgrades (not just teachings)
  - Include context in briefing

CLAUDE.md
  - Update session start to mention upgrades
```

### Templates:
```
templates/WAI/AGENTS.md
  - Add mention of upgrade-adoption-plan.json
  - Note about verification

templates/HUB/
  - Create all 5 hub templates
  - Hub can teach itself
```

---

## Security Model

### Trust Chain:
```
Hub creates upgrade-adoption-plan.json
    ↓ signs with hub fingerprint
Spoke receives signed plan
    ↓ verifies signature
Spoke verifies file hashes
    ↓ confirms integrity
Spoke checks applies_to (hub/spoke/universal)
    ↓ ensures relevance
Spoke adopts with confidence
```

### Verification:
```bash
wai verify-upgrade upgrade-adoption-plan.json
  → Checks hub signature
  → Verifies all file hashes
  → Reports trustworthiness
  → Shows adoption guidance
```

---

## Knowledge Flow Example

**Day 1: Framework improves**
```
Framework team: "We improved WAI-Guide.md"
    ↓
teach command (creates upgrade-adoption-plan.json)
    ↓ signs with hub fingerprint
Hub distributes to all spokes
```

**Day 2: Spoke sees upgrade**
```
Spoke closeout: Loads upgrade-adoption-plan.json
    ↓ verifies signature ✓
    ↓ verifies hashes ✓
Session start: "New upgrade available"
AI: "Looks safe, should we adopt?"
User: "Yes"
    ↓
Spoke adopts improved WAI-Guide.md
```

**Day 3: Hub learns back**
```
Spoke: "We customized WAI-State.json locally"
    ↓ learn command
Hub: Receives learned state
    ↓
Hub learns: "Spoke customized this section"
    ↓
Next teach includes: "Preserve customizations"
    ↓
Universal knowledge compound
```

---

## Related Epics & Lugs

| ID | Title | Phase | Status |
|----|-------|-------|--------|
| `c7f2e9a4b1d6` | CLI Reimplementation | v3.2+ | Design |
| `a2f7e9c4b1d6` | Teaching Reconciliation | v3.1 | Plan |
| `g5h8j2k9m3n7` | Upgrade Adoption Plan | v3.1 | Epic |
| `p2q6r9s4t8u1` | Hub Templates | v3.1 | Epic |
| `v3w7x1y5z9a4` | Universal Protocol | v3.1 | Epic |

---

## Success Criteria

✓ Hub and spoke use identical teach/learn  
✓ upgrade-adoption-plan.json is verified before adoption  
✓ Hub templates work same as spoke templates  
✓ Bidirectional learning works end-to-end  
✓ Knowledge compounds across sessions  
✓ AI understands context (why_changed, mentions)  
✓ Full test coverage (hub + spoke scenarios)  

---

## Why Now?

**v3.0.0** is proof-of-concept: teach works, adoptions need guidance

**v3.1** makes it production-grade: verified, contextual, bidirectional

**By v4** we have a knowledge network that improves itself over time

---

*Architectural decision: Hub-Spoke Unification (2026-02-01)*
