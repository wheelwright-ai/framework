# Phase 2-3 Integration Status

**Date:** 2026-02-01  
**Framework Version:** 3.0.0  
**Status:** Phase 2 Complete, Ready for Phase 3

---

## Phase 2 Completion Checklist ✅

### Hub Templates (templates/HUB/)
- [x] `hub-profile.json` - Hub identity, config, learning philosophy
- [x] `hub-registry.json` - Wheel tracking, teaching history
- [x] `hub-learning-index.md` - Knowledge base index, learning categories
- [x] `hub-security-policy.json` - Verification, trust model, compliance
- [x] `AGENTS.md` - Hub AI assistant instructions

### Teach Command Update
- [x] Rewritten to use UpgradeAdoptionPlanBuilder
- [x] Generates `upgrade-adoption-plan.json` (not `.teaching` files)
- [x] Includes spoke files (templates/WAI/)
- [x] Includes hub files (templates/HUB/)
- [x] Signs with hub fingerprint
- [x] Computes SHA256 hashes
- [x] Provides adoption guidance
- [x] Removed old helper functions

### Integration with Phase 1
- [x] Uses UpgradeAdoptionPlanBuilder
- [x] Uses sign_upgrade_plan()
- [x] Uses save_upgrade_plan()
- [x] File hashing implemented
- [x] Verification functions available

---

## What Each Hub Template Does

### hub-profile.json
**Purpose:** Hub configuration and preferences  
**Key Sections:**
- `user` - Developer identity
- `work_style` - Project preferences
- `hub_config` - Framework location, version
- `learning_philosophy` - When to share (threshold: 8/10)

### hub-registry.json
**Purpose:** Auto-managed registry of connected wheels  
**Key Sections:**
- `wheels[]` - Array of connected projects
- `teaching_history[]` - Timeline of teach events
- `statistics` - Aggregate metrics

### hub-learning-index.md
**Purpose:** Knowledge base index  
**Key Features:**
- 6 learning categories (architecture, performance, testing, security, workflow, tools)
- Impact scoring system (8/10 threshold)
- Learning contribution rules
- Admin commands for managing learnings

### hub-security-policy.json
**Purpose:** Security and verification settings  
**Key Sections:**
- `verification` - SHA256-HMAC algorithm
- `trust_model` - Hub fingerprint and key rotation
- `file_integrity` - Hash verification requirements
- `knowledge_distribution` - Who gets what
- `audit_logging` - Event tracking

### AGENTS.md
**Purpose:** AI assistant instructions for hub management  
**Key Content:**
- Hub-spoke unification concept
- Core concepts (UAP, learning signals)
- Common tasks and decision logic
- Monitoring and health checks
- Implementation checklist

---

## Teach Command Transformation

### Before (v3.0.x)
```python
# Created .teaching files
dst = teach_manager.ingest_dir / f"{template_name}.teaching"
dst.write_text(content)

# Created manifest with old structure
teach_manager.create_manifest(files_taught, ...)
```

### After (v3.1)
```python
# Build upgrade adoption plan
builder = UpgradeAdoptionPlanBuilder(framework_version, spoke_structure_version)

# Add spoke files with context
builder.add_file(
    name='WAI-Guide.md',
    changed_from='2.1.0',
    why_changed='Enhanced session start protocol',
    mentions=['session-start', 'teaching'],
    applies_to=['spoke', 'hub']
)

# Add hub files
builder.add_hub_file(
    name='hub-profile.json',
    why_changed='Added teaching history and learning index'
)

# Generate and sign
plan = builder.build()
plan = sign_upgrade_plan(plan, hub_key)
save_upgrade_plan(plan, spoke_path / 'upgrade-adoption-plan.json')
```

---

## Example: Teaching a Spoke

### Command
```bash
cd /path/to/framework
./WAI teach /path/to/spoke /path/to/hub /path/to/framework
```

### Output
```
Generating Upgrade Adoption Plan...
  [OK] WAI-Guide.md
  [OK] WAI-State.json
  [OK] WAI-State.md
  [OK] hub-profile.json
  [OK] hub-registry.json
  [OK] hub-learning-index.md
  [OK] hub-security-policy.json
  [OK] AGENTS.md

  [OK] Generated upgrade-adoption-plan.json
    Spoke files: 3
    Hub files: 5
    Total: 8 files
    [SECURE] Signed with hub fingerprint
    [NEXT] Agent will verify and adopt on next session
```

### Generated File (upgrade-adoption-plan.json)
```json
{
  "metadata": {
    "version": "3.0.0",
    "framework_version": "3.0.0",
    "spoke_structure_version": "3.0",
    "created_at": "2026-02-01T...",
    "source": "framework",
    "target_type": "universal"
  },
  "verification": {
    "hub_fingerprint": "sha256:...",
    "hash_algorithm": "sha256-hmac",
    "signed_by": "wheelwright-framework-3.0.0",
    "verification_required": true
  },
  "files": [
    {
      "name": "WAI-Guide.md",
      "path": "WAI-Spoke/WAI-Guide.md",
      "hash": "sha256:...",
      "version": "3.0.0",
      "changed_from": "2.1.0",
      "why_changed": "Enhanced session start protocol, added teaching reconciliation section",
      "safe_to_auto_adopt": true,
      "mentions": ["session-start", "teaching", "reconciliation"],
      "applies_to": ["spoke", "hub"],
      "action": "adopt"
    },
    ...
  ],
  "hub_files": [
    {
      "name": "hub-profile.json",
      "path": "hub-profile.json",
      "applies_to": ["hub"],
      "action": "adopt"
    },
    ...
  ],
  "adoption_guidance": {
    "for_spoke": {...},
    "for_hub": {...}
  }
}
```

---

## Hub-Spoke Unification Achieved

### Unified Protocol

Both hub and spokes now:
1. Receive signed `upgrade-adoption-plan.json`
2. Verify hub fingerprint
3. Verify file hashes
4. See adoption guidance (why changed, mentions)
5. Make adoption decisions (adopt/review/defer)
6. Implement adoptions using same logic
7. Return learnings to hub

### Identical Files
- Both receive spoke files (WAI-Guide.md, WAI-State.json, etc.)
- Hub also receives hub files (hub-profile.json, hub-registry.json, etc.)
- Same adoption logic for both

### Bidirectional Knowledge Flow
- Hub teaches spokes improvements
- Spokes contribute learnings to hub
- Hub aggregates and re-teaches
- Knowledge compounds across sessions

---

## What Happens in Phase 3

### Phase 3: Spoke-Side Verification
When a spoke receives `upgrade-adoption-plan.json`:

1. **Load Plan**
   ```python
   plan = load_upgrade_plan(spoke_path / 'upgrade-adoption-plan.json')
   ```

2. **Verify Hub Signature**
   ```python
   if not verify_hub_signature(plan, hub_key):
       raise SecurityError("Invalid hub signature")
   ```

3. **Verify File Hashes**
   ```python
   for file in plan['files']:
       if not verify_file_hash(file_content, file['hash']):
           raise IntegrityError(f"Hash mismatch: {file['name']}")
   ```

4. **Show Adoption Guidance**
   ```
   Pending Upgrades (Framework v3.0.0)
   
   • WAI-Guide.md
     Changed from: 2.1.0 → 3.0.0
     Why: Enhanced session start protocol
     Action: ADOPT
   
   • WAI-State.json
     Changed from: 2.0.1 → 3.0.0
     Why: Structure version 3.0
     Action: REVIEW (merge strategy)
   ```

5. **Execute Adoptions**
   - Auto-adopt safe files
   - Review files with user
   - Merge sections if needed
   - Preserve local customizations

### New Command: verify-upgrade
```bash
WAI verify-upgrade upgrade-adoption-plan.json
# Checks hub signature
# Verifies all file hashes
# Reports trustworthiness
# Shows adoption guidance
```

### Integration Points
- **closeout.py** - Load and verify on session close
- **session_start.sh** - Show pending upgrades
- **CLAUDE.md** - Brief AI on upgrades
- **adoption logic** - Merge/apply/reject files

---

## Architecture Overview

```
Framework (v3.0.0)
    ↓
teach_command()
    ├─ Load spoke templates (templates/WAI/)
    ├─ Load hub templates (templates/HUB/)
    ├─ Create UpgradeAdoptionPlanBuilder
    ├─ Add files with context (why_changed, mentions)
    ├─ Build plan with hashes
    ├─ Sign with hub fingerprint
    └─ Save upgrade-adoption-plan.json
         ↓
    Spoke receives plan
         ↓
    [Phase 3] Spoke verifies
         ├─ Check hub signature
         ├─ Check file hashes
         ├─ Show adoption guidance
         └─ Execute adoptions
         ↓
    Hub can also receive
         └─ Adopts hub files
         └─ Learns from spokes
         └─ Improves itself
```

---

## Files in Place

### New (Phase 2)
```
templates/HUB/
├── hub-profile.json              (85 lines)
├── hub-registry.json             (65 lines)
├── hub-learning-index.md         (180 lines)
├── hub-security-policy.json      (70 lines)
└── AGENTS.md                     (390 lines)

Documentation:
├── PHASE2-HUB-TEMPLATES-COMPLETE.md
├── PHASE2-SUMMARY.txt
└── PHASE-2-3-INTEGRATION-STATUS.md (this file)
```

### Modified (Phase 2)
```
wai/commands/teach.py             (194 lines)
- Uses UpgradeAdoptionPlanBuilder
- Generates upgrade-adoption-plan.json
- Includes hub templates
- Signs and hashes files
```

### Unchanged (Phase 1)
```
wai/upgrade_adoption.py           (335 lines)
- UpgradeAdoptionPlanBuilder (core logic)
- sign_upgrade_plan()
- verify_hub_signature()
- verify_file_hash()
- load/save functions
```

---

## Success Metrics

### Phase 1 ✅
- [x] UpgradeAdoptionPlanBuilder implemented
- [x] 16 tests passing
- [x] Hashing and signing working
- [x] Infrastructure complete

### Phase 2 ✅
- [x] Hub templates created (5 files)
- [x] Teach command updated
- [x] Upgrade plan generation working
- [x] File hashing and signing working
- [x] Hub-spoke unification protocol ready

### Phase 3 🚀
- [ ] Spoke verification command
- [ ] Closeout integration
- [ ] File adoption logic
- [ ] Merge strategy support
- [ ] Session start briefing

---

## Next Immediate Steps

1. **Create verify-upgrade command** (Phase 3)
   - Load upgrade-adoption-plan.json
   - Verify hub signature
   - Verify file hashes
   - Show adoption guidance

2. **Update closeout.py** (Phase 3)
   - Detect upgrade-adoption-plan.json
   - Run verify-upgrade
   - Propose adoptions

3. **Implement adoption logic** (Phase 3)
   - Auto-adopt safe files
   - Show merge strategy for reviewed files
   - Preserve local customizations

4. **Test end-to-end** (Phase 4)
   - teach → verification → adoption cycle
   - Hub template distribution
   - Learning flow from spokes to hub

---

*Integration status: Phase 2 complete, Phase 3 ready to begin (2026-02-01)*
