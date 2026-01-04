# Wheelwright Framework - Feature Backlog

This document tracks planned features and improvements for future consideration.

---

## High Priority

### 1. Version Detection + Auto-Upgrade in Teach Process
**Status:** Planned
**Priority:** High
**Description:**
Automatically detect spoke structure version and upgrade to latest format during hub sync/teach operations.

**Implementation:**
- Add `detect_spoke_version()` to check folder structure (.WAI vs WAI-Spoke)
- Add `upgrade_spoke_structure()` to migrate old formats
- Hook into `WAI teach` command
- Log upgrades to WAI-State.json decisions
- Update WAI-File-Index.json version field

**Benefits:**
- No manual migration needed after initial setup
- Spokes stay current automatically
- Seamless evolution of framework structure

**Design Spec:**
```python
# In WAI CLI teach command:
def teach_with_auto_upgrade(spoke_path: Path):
    version = detect_spoke_version(spoke_path)
    if version < CURRENT_VERSION:
        print(f"Upgrading spoke from v{version} to v{CURRENT_VERSION}")
        upgrade_spoke_structure(spoke_path, version)
    sync_learnings(spoke_path)
```

**Acceptance Criteria:**
- [ ] Detects .WAI vs WAI-Spoke structure
- [ ] Renames old file names (wheel-signals.jsonl → WAI-Signals.jsonl)
- [ ] Creates WAI-File-Index.json if missing
- [ ] Logs upgrade decision to WAI-State.json
- [ ] Handles edge cases (partial migrations, permission errors)

---

## Medium Priority

### 2. Hub Auto-Discovery of Projects (MOVED TO COMPLETED)
**Status:** Complete (2025-12-30)
See "Completed" section below.

### 3. Spoke Extensibility System
**Status:** Deferred (partially implemented, not integrated)
**Priority:** Medium
**Description:**
Plugin system allowing custom "spokes" (specialized AI capabilities) to extend wheel functionality.

**Previous Implementation:**
- Code existed in `WAI-Spokes/` folder (removed during cleanup)
- Included: BaseSpoke class, spoke loader, registry system
- Sample spokes: code_review, document_analysis, meta_consultation

**Reason for Deferral:**
- Never integrated into WAI CLI
- No active usage in framework
- Complexity vs value unclear

**Future Considerations:**
- Do we need extensibility? Or is core framework sufficient?
- If yes: Design simpler plugin interface
- Consider: Python entry points vs custom loader
- Evaluation: User demand should drive this feature

**Decision Point:** Re-evaluate after v2.0 when core framework is stable.

---

## Low Priority

### 4. Web Dashboard for Hub
**Status:** Idea
**Priority:** Low
**Description:**
Visual web interface to view hub status, manage spokes, and browse consolidated knowledge.

**Features:**
- Project health overview
- Learning signals timeline
- Knowledge graph visualization
- Spoke registration management

**Technology:** Could use simple static site generator or lightweight Flask/FastAPI app.

**Decision Point:** Wait for user feedback - is CLI sufficient?

---

### 5. Multi-Hub Synchronization
**Status:** Idea
**Priority:** Low
**Description:**
Allow multiple hubs to share learnings across organizations or teams.

**Use Case:**
- Team hub + personal hub
- Dev hub + prod hub
- Cross-organization knowledge sharing

**Challenges:**
- Security (what should be shared?)
- Privacy (PII in learnings)
- Conflict resolution
- Trust model

**Decision Point:** Wait for multi-user adoption.

---

## Research / Exploration

### 6. Integration with Git Hooks
**Status:** Exploration
**Priority:** Research
**Description:**
Automatic logging of development milestones via git hooks.

**Ideas:**
- Pre-commit: Log decision if commit message indicates architectural change
- Post-merge: Update WAI-State.json with integration notes
- Pre-push: Trigger hub sync

**Questions:**
- Too invasive?
- Would users want this?
- Conflicts with existing git workflows?

---

### 7. AI Model-Specific Optimizations
**Status:** Exploration
**Priority:** Research
**Description:**
Optimize WAI-Guide.md instructions per AI model (Claude, GPT-4, Gemini, etc.).

**Current:** Single CLAUDE.md works for all models with some token inefficiency.

**Future:** Detect AI model and serve optimized instructions.

**Challenges:**
- Model detection
- Maintenance of multiple instruction sets
- Drift between versions

---

### 8. Hub Recommendations Engine (Cross-Project)
**Status:** Exploration
**Priority:** Research
**Description:**
Hub-level analysis that synthesizes WAI KB, spokes' state, and trusted external sources (TBD) to recommend higher-order improvements across projects (architecture, UX, analytics, resource usage, operational efficiency).

**Scope Ideas:**
- Cross-project insights, not just local optimizations
- Evidence-backed recommendations with confidence/impact scoring
- Optional external sources with explicit allowlist and prompts

**Questions:**
- What signals are required before issuing recommendations?
- How to prevent generic advice and keep it project-specific?
- What trusted sources should be allowed and how to attribute them?
- How should the CLI present and store reports?

---

## Completed

### ✓ Folder Structure Migration
**Completed:** 2025-12-29
**Description:** Migrated `.WAI/` → `WAI-Spoke/` with consistent `WAI-*` file naming.

### ✓ Hub Registry Structure
**Completed:** 2025-12-29
**Description:** Created `/hub/registry/` structure for spoke registration.

### ✓ Bidirectional File Index
**Completed:** 2025-12-29
**Description:** Added `WAI-File-Index.json` with spoke_path metadata for bidirectional attribution.

### ✓ Hub Auto-Discovery of Projects + CLI Redesign
**Completed:** 2025-12-30
**Description:** Complete CLI redesign with intelligent hub discovery and project management.

**Implemented Features:**
- **Framework-First Initialization:** Run in framework folder → init framework → discover/create hub → add projects
- **Intelligent Hub Discovery:** Auto-scan parent folder (../hub, ../WAI-Hub, ../*hub*) with scoring algorithm
  - Environment variable: `$WHEELWRIGHT_HUB_PATH` (highest priority)
  - Scoring factors: hub-profile.json (+10), registry (+5), recent modification (+2), name match (+1)
  - Cross-platform path support (WSL/Windows/macOS)
- **Interactive Project Selection:** Enhanced project discovery with y/n checklist per project
  - Detects: WAI-Spoke/, .git, package.json, pyproject.toml, Cargo.toml, go.mod, etc.
  - Commands: y/n, all, none, quit
  - Priority sorting (WAI-enabled > Git repos > other projects)
- **Groups Management:** Manual CRUD for organizing projects
  - `WAI group create <name> [--description]`
  - `WAI group list [--verbose]`
  - `WAI group add-spoke <group> <spoke>`
  - `WAI group remove-spoke <group> <spoke>`
  - `WAI group delete <name> [--force]`
- **Modular Architecture:** Refactored from monolithic WAI script to wai_cli/ package
  - `wai_cli/core.py` - Main CLI entry
  - `wai_cli/init.py` - Framework-first initialization
  - `wai_cli/hub.py` - Hub discovery and management
  - `wai_cli/projects.py` - Project discovery and selection
  - `wai_cli/groups.py` - Groups CRUD operations
  - `wai_cli/upgrader.py` - Version upgrade logic
  - `wai_cli/utils/` - Cross-platform utilities (paths, input, registry, exceptions)
- **Comprehensive Error Handling:** KeyboardInterrupt support, validation, safe input
- **Updated Templates:** wheel-projects.json v2.0 with groups field

**Benefits Realized:**
- Easier onboarding for users with many projects (interactive selection)
- Reduced manual hub setup (auto-discovery with defaults)
- Better UX (no confusing role selection, framework-first workflow)
- Cross-platform compatibility (WSL/Windows/macOS path handling)
- Extensible foundation for future features

---

## Backlog Management

**Adding Items:**
1. Describe feature clearly
2. Note priority (High/Medium/Low/Research)
3. Include rationale and use cases
4. List implementation considerations
5. Define acceptance criteria (for high priority items)

**Review Schedule:**
- High priority: Monthly
- Medium priority: Quarterly
- Low priority: Bi-annually
- Research: Ad-hoc

**Prioritization Criteria:**
1. User demand (based on feedback/issues)
2. Foundational value (enables other features)
3. Maintenance burden (low is better)
4. Alignment with core vision

---

*Last Updated: 2026-01-02*
