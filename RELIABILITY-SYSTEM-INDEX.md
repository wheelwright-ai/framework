# System Reliability Index

**Your complete guide to bulletproof automation**

---

## 📋 Documents (In Reading Order)

### 1. **SYSTEM-RELIABILITY-PROTOCOL.md** ⭐ START HERE
**15 min read**

Understand the three-layer foundation:
- Enhanced Closeout Skill (git mandatory, fail signals)
- Observation & Verification System (trust but verify)
- SSH Key Facts (wheel-wide defaults)

Diagrams showing how layers work together in real scenarios.

### 2. **WAI-OBSERVATION-SYSTEM.md**
**20 min read**

Complete specification of the observation system:
- Observation log structure (JSONL format)
- Observation categories (git, file, state ops)
- Verification protocol (before/execute/after)
- Idempotency & multi-agent safety
- Session integration & playback
- Size management (<0.5 MB per session)

### 3. **WAI-OBSERVATION-IMPLEMENTATION.md**
**20 min read**

Step-by-step implementation guide:
- Phase 1: Create observations.jsonl
- Phase 2: Update closeout skill
- Phase 3: Add idempotency checks
- Phase 4: SSH verification
- Phase 5: Session playback
- Phase 6: Multi-agent coordination
- Phase 7: Integrate with all skills

Code examples for every phase.

### 4. **.claude/commands/wai-closeout-enhanced.md**
**15 min read**

The enhanced closeout skill specification:
- 4-phase execution model
- Mandatory git operations
- Critical fail signals (🚨)
- Version bumping support
- Dry-run mode
- Error handling & remediation

---

## 🎯 Quick Reference

### Core Principle
```
Execute → Observe → Verify → Log

Never:
❌ Assume action succeeded
❌ Continue on unexpected result
❌ Work without verification

Always:
✅ Capture actual result
✅ Compare to expected
✅ Alert on mismatch
✅ Log for audit
```

### SSH Key Facts
```
Location:    ~/.ssh/id_ed25519
Test:        ssh -T git@github.com
Success:     Exit code 1 + "authenticated"
```

### Observation Log
```
File:        WAI-Spoke/observations.jsonl
Format:      JSONL (one JSON object per line)
Size:        <0.5 MB per session
Retention:   Current + 5 previous sessions
```

### Multi-Agent Rule
```
Before any action:
  1. Read observations.jsonl
  2. Check if already done
  3. If yes & idempotent: skip
  4. If yes & not idempotent: alert
  5. If no: proceed with observation
```

---

## 🚀 Implementation Checklist

### Next Session (Immediate)
- [ ] Read SYSTEM-RELIABILITY-PROTOCOL.md (15 min)
- [ ] Create WAI-Spoke/observations.jsonl
- [ ] Fix SSH key issue
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
  # Add public key to GitHub Settings > SSH Keys
  ```
- [ ] Retry closeout to complete git push
  ```bash
  closeout
  ```

### This Sprint (This Week)
- [ ] Read WAI-OBSERVATION-SYSTEM.md (20 min)
- [ ] Read WAI-OBSERVATION-IMPLEMENTATION.md (20 min)
- [ ] Implement Phase 1-3 (observations, closeout update, idempotency)
- [ ] Test with simple manual action

### Next Sprint (Phase Implementation)
- [ ] Implement Phase 4-7 (all skills use observations)
- [ ] Build session playback in briefing
- [ ] Test multi-agent coordination
- [ ] Archive old observations

---

## 📊 Three Layers Explained

### Layer 1: Enhanced Closeout
**What:** Skill that executes closeout with guarantees  
**Where:** `.claude/commands/wai-closeout-enhanced.md`  
**Guarantees:**
- Git is mandatory
- Fail signals (🚨) stop execution
- All 4 phases verified before complete

### Layer 2: Observation System
**What:** Records every action + verification  
**Where:** `WAI-OBSERVATION-SYSTEM.md` + `WAI-OBSERVATION-IMPLEMENTATION.md`  
**Guarantees:**
- No assumptions (every action observed)
- No silent failures (alerts on mismatch)
- No duplicate work (idempotency support)
- Complete audit trail (playback available)

### Layer 3: SSH Facts
**What:** Wheel-wide defaults for authentication  
**Where:** Both specification docs  
**Guarantees:**
- Consistent SSH setup approach
- Clear recovery procedure
- Verified in observations

---

## 🔄 How Recovery Works

### Scenario: Git Push Failed (SSH Issue)

**Session 1: Claude**
```
obs-001 ✅ lugs.reconcile
obs-002 ✅ state.update
obs-003 ✅ git.add
obs-004 ✅ git.commit
obs-005 ❌ ssh.verify → Permission denied
obs-006 ⏭️  git.push → SKIPPED (SSH failed)

Result: CLOSEOUT INCOMPLETE
Blocker: obs-005 (fix SSH, then retry)
```

**Session 2: Gemini**
```
obs-007 ✅ ssh.verify → FIXED (SSH key now working)
obs-008 ✅ git.push RETRY → Succeeds
obs-009 ✅ git.log.verify

Result: CLOSEOUT COMPLETE
Recovery: SSH fixed, git push succeeded
```

**Guarantees:**
- ✅ Work not duplicated (obs-001-004 skipped)
- ✅ Blocker identified (obs-005)
- ✅ Fix verified (obs-007)
- ✅ Complete audit (all observations logged)
- ✅ Idempotent (safe to retry)

---

## 🛡️ Safety Guarantees

### For Solo Agent
```
If something fails:
  → Fail signal shows exactly what
  → Remediation steps provided
  → Safe to retry (idempotent)
```

### For Multi-Agent
```
If agents work in parallel:
  → observations.jsonl is shared
  → Each agent checks before acting
  → Duplicate work prevented
  → Conflicts avoided
```

### For All Sessions
```
Every action has:
  → Recorded intent (plan)
  → Expected result
  → Actual result
  → Verification status
  → Remediation if failed
  
Complete playback available for any session.
```

---

## 📖 When to Read Each Document

**You want to...**

| Goal | Read |
|------|------|
| Understand overall approach | SYSTEM-RELIABILITY-PROTOCOL.md |
| Learn observation spec | WAI-OBSERVATION-SYSTEM.md |
| Implement observations | WAI-OBSERVATION-IMPLEMENTATION.md |
| Use closeout skill | wai-closeout-enhanced.md |
| Quick fact lookup | This document (RELIABILITY-SYSTEM-INDEX.md) |

---

## ⚡ TL;DR

**Three layers ensure bulletproof automation:**

1. **Enhanced Closeout** → Git mandatory, fail signals loud
2. **Observations** → Every action observed & verified
3. **SSH Facts** → Wheel-wide defaults for consistency

**Key guarantee:** 
```
Never silently fail.
Never duplicate work.
Always alert on unexpected results.
Always provide recovery path.
```

**Next step:** Read SYSTEM-RELIABILITY-PROTOCOL.md (15 min)

---

**Status:** ✅ All three systems documented and committed  
**SSH Issue:** Awaiting user's manual fix (fix SSH key, then retry closeout)  
**Next:** Start implementation checklist when ready
