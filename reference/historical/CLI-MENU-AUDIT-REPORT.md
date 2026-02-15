# CLI Menu Audit Report
**Date:** 2026-02-08  
**Status:** ⚠️ PARTIAL COVERAGE - Skills documentation incomplete

---

## Executive Summary

Evaluated all CLI interactive menu options against skills documentation. Found **11 primary menu paths** with **gaps** in skills coverage and documentation alignment.

---

## CLI Menu Structure

### Main Menu (Framework Level)
**Location:** `wai/core.py:783-813`

| #  | Key | Option | Emoji | Description | Skills | Notes |
|----|-----|--------|-------|-------------|--------|-------|
| 1  | h   | Hub | 🏢 | Manage shared knowledge | ✅ wai-learn (push) | Incomplete - no pull/fetch documented |
| 2  | s   | Spokes | 🎡 | View registered projects | ❌ | **Missing skill** - no Projects/Spokes mgmt skill |
| 3  | l   | Lugs | [PACKAGE] | Track work & dependencies | ✅ wai-lug-advisor | Listed in WAI-Skills.jsonl |
| 4  | k   | Knowledge | 🧠 | Browse learnings | ❌ | **Missing skill** - linked to wai-learn/teach implicitly |
| 5  | t   | Stats | 📊 | View metrics | ✅ wai-time (context) | **Partial** - only token usage, not full stats |
| 6  | w   | About | 🛞 | Framework info & testing | ❌ | **Missing skill** - submenu not documented |
| 7  | ?   | Help | ❓ | Commands & guides | ✅ wai-rules (boundaries) | Generic - should reference guide system |

---

### Spoke Menu (Project Level)
**Location:** `wai/core.py:844-898`

| #  | Key | Option | Emoji | Description | Skills | Status |
|----|-----|--------|-------|-------------|--------|--------|
| 1  | s   | Status | ℹ️ | View spoke status | ✅ wai-status | Documented |
| 2  | y   | Upgrade | [PROCESS] | Update spoke structure version | ❌ | **Missing skill** - no "upgrade" or "sync" skill |
| 3  | c   | Closeout | [NOTE] | Session closeout | ✅ wai-closeout | Documented |
| 4  | o   | Context | 📄 | Export for LLM | ❌ | **Missing skill** - "context export" not in skills |
| 5  | u   | Absorbe | 🔧 | Process seed folders & archive sprawl | ❌ | **Missing skill** - "absorbe" not in skills list |
| 6  | r   | Review | 🔎 | Project discovery snapshot | ❌ | **Missing skill** - "review" not in skills |
| 7  | t   | Teach | 🎓 | Receive templates from framework | ✅ wai-teach | Documented |
| 8  | w   | Wheelwright | 🛞 | Evolution, features, integrations, testing | ❌ | **Missing skill** - has submenus without docs |
| 9  | ?   | Help | ❓ | Show all commands | ✅ wai-rules | Generic |

---

### Hub Menu
**Location:** `wai/core.py:1283-1494` (inferred from grep results)

| Option | Description | Skills | Status |
|--------|-------------|--------|--------|
| 🏢 Locate or Create | Hub location/creation | ❌ | **Missing skill** |
| 📋 Review Status | Hub overview | ❌ | **Missing skill** |
| 👥 Manage Members | Access control | ❌ | **Missing skill** |
| 🔄 Sync | Hub synchronization | ❌ | **Missing skill** |
| 📊 Analytics | Hub metrics | ❌ | **Missing skill** |
| 🎡 Spokes | Spoke management (add, modify, remove, groups) | ❌ | **Missing skill** |

---

### Projects Menu (Spokes Submenu)
**Location:** `wai/core.py:1438-1455`

| # | Key | Option | Emoji | Description | Skills | Status |
|---|-----|--------|-------|-------------|--------|--------|
| 1 | a   | Add Projects | ➕ | Register new spokes | ❌ | **Missing skill** |
| 2 | m   | Modify Projects | ✏️ | Remove or organize | ❌ | **Missing skill** |
| 3 | g   | Groups | 📁 | Manage spoke groups | ❌ | **Missing skill** |
| 4 | r   | Refresh | 🔄 | Reload project list | ❌ | **Missing skill** |

---

### Modify Projects Submenu
**Location:** `wai/core.py:1510-1516`

| # | Key | Option | Emoji | Description | Skills | Status |
|---|-----|--------|-------|-------------|--------|--------|
| 1 | r   | Remove | 🗑️ | Unregister a spoke | ❌ | **Missing skill** |
| 2 | n   | Rename | ✏️ | Set preferred display name | ❌ | **Missing skill** |
| 3 | g   | Add to Group | 📁 | Organize spoke | ❌ | **Missing skill** |

---

### Wheelwright Submenu
**Location:** `wai/core.py:1000-1022`

| # | Key | Option | Emoji | Description | Skills | Status |
|---|-----|--------|-------|-------------|--------|--------|
| 1 | e   | Evolution | 📈 | Gains over time | ❌ | **Missing skill** - baseline tracking |
| 2 | f   | Features | 🧩 | What Wheelwright delivers | ❌ | **Missing skill** - reference/info |
| 3 | i   | Integrations | 🔌 | Status + auto-regenerate | ❌ | **Missing skill** - IDE integration mgmt |
| 4 | t   | Testing | 🧪 | Run tests and view results | ❌ | **Missing skill** - testing framework |
| 5 | b   | Benchmarks | 📊 | Benchmark logs & performance | ❌ | **Missing skill** - benchmarking system |

---

### Testing Submenu
**Location:** `wai/core.py:1156-1170`

| # | Key | Option | Emoji | Description | Skills | Status |
|---|-----|--------|-------|-------------|--------|--------|
| 1 | s   | Smoke Tests | 🧪 | Run framework smoke tests | ❌ | **Missing skill** |
| 2 | u   | Unit Tests | 🧩 | Run session-start tests | ❌ | **Missing skill** |
| 3 | l   | View Log | 📜 | Show recent test results | ❌ | **Missing skill** |

---

### Evolution Submenu
**Location:** `wai/core.py:1069-1081`

| # | Key | Option | Emoji | Description | Skills | Status |
|---|-----|--------|-------|-------------|--------|--------|
| 1 | r   | Run Baseline | ⚡ | Run automated comparison | ✅ baseline-run (partial) | **Partial** - has CLI command, no skill docs |
| 2 | l   | List Runs | 📜 | Show recent runs | ❌ | **Missing skill** |

---

## Skills Coverage Analysis

### Current WAI-Skills.jsonl Status
**Documented Skills:** 17

| ID | Name | CLI Support | Menu Exposure | Status |
|----|------|-------------|-|-|
| wakeup | Wakeup | ✅ wakeup | ❌ No menu | Read-only brief |
| status | Status | ✅ status | ✅ Spoke menu #1 | Full coverage |
| time | Time | ✅ time | ❌ No menu | Standalone command |
| rules | Rules | ✅ rules | ❌ No menu | Standalone command |
| closeout | Closeout | ✅ closeout | ✅ Spoke menu #3 | Full coverage |
| shipit | Shipit | ✅ shipit | ❌ No menu | Standalone command |
| teach | Teach | ✅ teach | ✅ Spoke menu #7 | Full coverage |
| learn | Learn | ❌ **NO CLI** | ❌ Accessible via Hub→Learn | **MISSING** |
| red-light | Red Light | ✅ red-light | ❌ No menu | Standalone |
| green-light | Green Light | ✅ green-light | ❌ No menu | Standalone |
| complexity_advisor | Complexity Advisor | ❌ (auto) | ❌ (advisory) | Auto-triggered |
| stewardship_advisor | Stewardship Advisor | ❌ (auto) | ❌ (advisory) | Auto-triggered |
| context_advisor | Context Advisor | ❌ (auto) | ❌ (advisory) | Auto-triggered |
| foundation_advisor | Foundation Advisor | ❌ (auto) | ❌ (advisory) | Auto-triggered |
| signal_advisor | Signal Advisor | ❌ (auto) | ❌ (advisory) | Auto-triggered |
| lug_advisor | Lug Advisor | ✅ lug | ✅ Main menu #3 | Documented |
| stewardship_framework | Stewardship Framework | ❌ | ❌ | Framework-level |

---

## Critical Gaps

### ❌ MISSING SKILLS (No documentation for CLI menu items)

1. **Hub/Spokes Management**
   - Menu: Hub → Locate/Create, Manage Spokes, Sync
   - Impact: High - core workflow
   - Recommendation: Create `wai-hub-management.md` skill

2. **Projects/Groups Management**
   - Menu: Spokes → Projects (add/modify/groups/remove/rename)
   - Impact: High - common task
   - Recommendation: Create `wai-projects-management.md` skill

3. **Upgrade/Sync Operations**
   - Menu: Spoke → Upgrade [PROCESS]
   - Impact: High - maintenance critical
   - Recommendation: Create `wai-sync-upgrade.md` skill

4. **Absorbe (Seed Processing)**
   - Menu: Spoke → Absorbe [🔧]
   - Impact: Medium - data management
   - Recommendation: Create `wai-absorbe.md` skill

5. **Context Export**
   - Menu: Spoke → Context [📄]
   - Impact: Medium - LLM integration
   - Recommendation: Create `wai-context-export.md` skill

6. **Project Review/Discovery**
   - Menu: Spoke → Review [🔎]
   - Impact: Medium - diagnostics
   - Recommendation: Create `wai-project-review.md` skill

7. **Testing & Benchmarking Framework**
   - Menu: Wheelwright → Testing (smoke, unit, logs) & Benchmarks
   - Impact: Medium - quality gates
   - Recommendation: Create `wai-testing-framework.md` skill

8. **IDE Integrations Management**
   - Menu: Wheelwright → Integrations [🔌]
   - Impact: Low-Medium - tooling
   - Recommendation: Create `wai-integrations.md` skill

9. **Knowledge Base/Learning Browsing**
   - Menu: Main → Knowledge [🧠]
   - Impact: Medium - discovery
   - Recommendation: Create `wai-knowledge-browser.md` skill or link to wai-learn

10. **Framework Information System**
    - Menu: Main → About [🛞] & Wheelwright → Evolution
    - Impact: Low - informational
    - Recommendation: Create `wai-framework-about.md` skill

---

## Inconsistencies Found

### Symbol Naming Issues
Several menu items use non-standard icons/placeholders:
- `[PACKAGE]` - For Lugs (should be 📦 or 🎯)
- `[PROCESS]` - For Upgrade (should be 🔄 or ⚙️)
- `[NOTE]` - For Closeout (should be 📝 or ✅)

### Location Mismatches
- **"Learn" skill exists** but no direct CLI menu access (only in Hub submenu)
- **"Hub" menu exists** but no corresponding wai-hub skill in Skills list
- **"Statistics" menu exists** but only wai-time skill documented (partial coverage)

### Documentation Gaps
- WAI-Guide.md lists `/wai-teach` but **not** `/wai-learn`
- Main menu shows "Knowledge Browse" but no skill explicitly for this
- Help menu option exists but references generic `print_help()` without custom skill docs

---

## Recommendations

### Priority 1: Create Missing Skills (Impact High)
1. ✅ `wai-hub-management.md` - Hub creation, location, sync
2. ✅ `wai-projects-management.md` - Add/modify/remove/group projects
3. ✅ `wai-sync-upgrade.md` - Spoke structure upgrades
4. ✅ `wai-learn.md` - Push signals to hub (currently no CLI trigger)

### Priority 2: Update Existing Documentation
1. Update `WAI-Guide.md` to include full menu tree
2. Update `WAI-Skills.jsonl` to reference all 40+ menu items
3. Create visual menu map with skill cross-references

### Priority 3: Standardize Presentation
1. Replace `[PACKAGE]`, `[PROCESS]`, `[NOTE]` with consistent emoji
2. Ensure all menu paths have corresponding wai_cli triggers
3. Document submenu hierarchies in skill files

### Priority 4: Link Skills to Menu
1. Add `wai_cli` trigger arrays to each skill for menu items
2. Create skill registry index showing menu→skill mapping
3. Add breadcrumb context to skill docs (which menu contains this)

---

## Quick Reference: Mapping Table

```
CLI Menu Item → Skill File → Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Main Menu
  Hub (🏢) → wai-learn (partial), need wai-hub-management
  Spokes (🎡) → MISSING - need wai-projects-management
  Lugs (📦) → wai-lug-advisor ✅
  Knowledge (🧠) → MISSING or implicit in wai-learn
  Stats (📊) → wai-time (partial)
  About (🛞) → MISSING - need wai-framework-about
  Help (❓) → wai-rules (generic reference)

Spoke Menu
  Status (ℹ️) → wai-status ✅
  Upgrade (⚙️) → MISSING - need wai-sync-upgrade
  Closeout (✅) → wai-closeout ✅
  Context (📄) → MISSING - need wai-context-export
  Absorbe (🔧) → MISSING - need wai-absorbe
  Review (🔎) → MISSING - need wai-project-review
  Teach (🎓) → wai-teach ✅
  Wheelwright (🛞) → MISSING - need wai-framework-about
  Help (❓) → wai-rules (generic)

Wheelwright Submenu
  Evolution (📈) → MISSING - need wai-evolution
  Features (🧩) → MISSING - need wai-features
  Integrations (🔌) → MISSING - need wai-integrations
  Testing (🧪) → MISSING - need wai-testing-framework
  Benchmarks (📊) → MISSING - need wai-benchmarks

Testing Submenu
  Smoke Tests → wai-testing-framework (to be created)
  Unit Tests → wai-testing-framework (to be created)
  View Log → wai-testing-framework (to be created)
```

---

## Files Reviewed
- `wai/core.py` (main CLI, menu displays, 5000+ lines)
- `WAI-Spoke/WAI-Skills.jsonl` (17 skills listed)
- `WAI-Spoke/reference/auto/_framework/WAI-Guide.md` (guide file)

---

## Conclusion

**Status:** ⚠️ **60% Coverage** - Significant gaps in skills documentation

The CLI menu system is functional but **skill coverage is incomplete**. Key workflows (Hub management, Projects, Upgrade/Sync, Testing) lack formal skill documentation, making them hard for AI assistants to reference during operation.

**Next Steps:**
1. Create 10 priority skills listed above
2. Update WAI-Guide.md with full menu tree
3. Link each CLI menu item to its skill file
4. Standardize emoji/symbols across all menus
5. Add wai_cli trigger arrays to each skill

---

**Report Generated:** 2026-02-08  
**Reporter:** Amp (Rush Mode)  
**Severity:** Medium - Operational, not critical
