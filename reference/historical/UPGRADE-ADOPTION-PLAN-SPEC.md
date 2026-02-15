# Upgrade Adoption Plan Specification

**Version:** 1.0  
**Date:** 2026-02-01  
**Purpose:** Secure, verified, contextual knowledge distribution

---

## Overview

`upgrade-adoption-plan.json` replaces generic teaching with **verified, versioned, contextual upgrades**.

Instead of "here are some files", it says: "Here's what changed, why, when, and whether you should adopt it for your specific project needs."

---

## File Structure

```json
{
  "metadata": {
    "version": "3.0.0",
    "framework_version": "3.0.0",
    "spoke_structure_version": "3.0",
    "created_at": "2026-02-01T18:12:00Z",
    "source": "hub",
    "target_type": "universal",
    "description": "Framework templates for universal distribution to hubs and spokes"
  },
  
  "verification": {
    "hub_fingerprint": "sha256-abc123...",
    "spoke_signature": null,
    "hash_algorithm": "sha256-hmac",
    "signed_by": "wheelwright-framework-v3.0.0",
    "verification_key": "public-key-rotation-id"
  },

  "files": [
    {
      "name": "WAI-Guide.md",
      "path": "WAI-Spoke/WAI-Guide.md",
      "size": 17910,
      "hash": "sha256:abc123def456",
      "source_path": "reference/auto/_framework/WAI-Guide.md",
      "version": "3.0.0",
      "changed_from": "2.1.0",
      "why_changed": "Enhanced session start protocol, added teaching reconciliation section",
      "breaking_changes": false,
      "safe_to_auto_adopt": true,
      "requires_review": false,
      "mentions": ["session-start", "teaching", "reconciliation"],
      "applies_to": ["spoke", "hub"],
      "status": "ready",
      "action": "adopt"
    },
    {
      "name": "WAI-State.json",
      "path": "WAI-Spoke/WAI-State.json",
      "size": 20387,
      "hash": "sha256:def789ghi012",
      "source_path": "reference/auto/_framework/WAI-State.json",
      "version": "3.0.0",
      "changed_from": "2.0.1",
      "why_changed": "Structure version 3.0, added teaching-adoption-plan schema",
      "breaking_changes": false,
      "safe_to_auto_adopt": false,
      "requires_review": true,
      "merge_strategy": "merge_sections",
      "sections_to_preserve": [
        "_session_state",
        "_project_foundation",
        "decisions",
        "analytics"
      ],
      "sections_to_update": [
        "wheelwright.structure_version",
        "wheelwright.version",
        "_file_meta"
      ],
      "mentions": ["structure", "version", "state-management"],
      "applies_to": ["spoke", "hub"],
      "status": "review_needed",
      "action": "review"
    }
  ],

  "hub_files": [
    {
      "name": "hub-profile.json",
      "path": "hub-profile.json",
      "size": 8234,
      "hash": "sha256:hub123hub456",
      "source_path": "reference/auto/_hub/hub-profile.json",
      "version": "3.0.0",
      "changed_from": "2.0.0",
      "why_changed": "Added teaching history and learning index",
      "breaking_changes": false,
      "safe_to_auto_adopt": true,
      "requires_review": false,
      "mentions": ["hub-profile", "teaching", "learning"],
      "applies_to": ["hub"],
      "status": "ready",
      "action": "adopt"
    }
  ],

  "adoption_guidance": {
    "for_spoke": {
      "recommended_order": [
        "WAI-Guide.md (adopt immediately - no conflicts)",
        "WAI-State.json (review merge strategy)"
      ],
      "post_adoption": "Run: WAI sync to process updated structure"
    },
    "for_hub": {
      "recommended_order": [
        "hub-profile.json (adopt immediately)",
        "hub-registry.json (review if modified)"
      ],
      "post_adoption": "Run: WAI hub status to verify"
    }
  },

  "checksums": {
    "all_files_hash": "sha256:total-manifest-hash",
    "verification_required": true,
    "verification_command": "wai verify-upgrade upgrade-adoption-plan.json"
  }
}
```

---

## Security Features

### 1. Hub Fingerprint
```json
"hub_fingerprint": "sha256-abc123..."
```
- Hub signs the plan with its key
- Spoke verifies signature before adopting
- Prevents MITM tampering with upgrade plan
- Establishes trust chain

### 2. File Hashes
```json
"hash": "sha256:abc123def456"
```
- Each file has content hash
- Spoke verifies downloaded file matches
- Detects corruption or tampering

### 3. Version Context
```json
"version": "3.0.0",
"changed_from": "2.1.0",
"applies_to": ["spoke", "hub"]
```
- AI knows what version it applies to
- Understands impact (breaking vs non-breaking)
- Knows if file is relevant to this project

---

## Why This Design

### 1. **Verification without Overheads**
- Hash allows quick integrity check
- Hub fingerprint proves source
- No need for external PKI

### 2. **AI-Friendly**
- `mentions` tells AI what changed (no need to parse files)
- `why_changed` explains intent
- `requires_review` guides adoption decision
- `applies_to` filters irrelevant files

### 3. **Security**
- Spoke can verify upgrade before adoption
- Detects man-in-the-middle
- Prevents malicious modifications

### 4. **Context Preservation**
- `merge_strategy` tells how to integrate
- `sections_to_preserve` protects local work
- `sections_to_update` applies improvements

---

## Adoption Workflow

### Spoke Side (v3.1)

```python
# On closeout:
def _reconcile_teachings(self):
    plan = load_upgrade_adoption_plan()
    
    # 1. Verify signature
    if not verify_hub_signature(plan):
        raise SecurityError("Invalid hub signature")
    
    # 2. Verify file hashes
    for file in plan['files']:
        if not verify_file_hash(file):
            raise IntegrityError(f"Hash mismatch: {file['name']}")
    
    # 3. Build adoption decisions
    adoptions = []
    for file in plan['files']:
        if file['safe_to_auto_adopt']:
            adoptions.append(("adopt", file))
        elif file['requires_review']:
            adoptions.append(("review", file))
        else:
            adoptions.append(("defer", file))
    
    return adoptions

# On session start:
def show_upgrade_briefing():
    plan = load_upgrade_adoption_plan()
    
    print("## Pending Upgrades")
    print(f"Framework v{plan['metadata']['framework_version']}")
    print()
    for file in plan['files']:
        if file['applies_to'] in ['universal', 'spoke']:
            print(f"• {file['name']}")
            print(f"  Changed from: {file['changed_from']} → {file['version']}")
            print(f"  Why: {file['why_changed']}")
            print(f"  Action: {file['action'].upper()}")
```

### Hub Side (v3.1)

Hub creates upgrade plan for distribution:

```python
def create_upgrade_adoption_plan(framework_version):
    # Gather files from templates/
    spoke_files = scan_spoke_templates()
    hub_files = scan_hub_templates()
    
    # Sign with hub fingerprint
    hub_sig = sign_with_hub_key(spoke_files + hub_files)
    
    # Create plan
    plan = {
        "metadata": {
            "version": framework_version,
            "framework_version": get_framework_version(),
            "source": "hub",
            "target_type": "universal"
        },
        "verification": {
            "hub_fingerprint": hub_sig,
            "signed_by": get_hub_id()
        },
        "files": [
            # spoke files with mentions, why_changed, etc.
        ],
        "hub_files": [
            # hub-specific files
        ]
    }
    
    return plan

# In teach command:
def teach_command(spoke_path, hub_path, framework_path):
    plan = create_upgrade_adoption_plan(FRAMEWORK_VERSION)
    
    # Copy files to spoke
    for file in plan['files']:
        copy_file(source, spoke_path)
    
    # Save plan
    save_json(plan, spoke_path / "upgrade-adoption-plan.json")
```

---

## Hub Templates (New)

Create `templates/HUB/` directory:

```
templates/HUB/
├── hub-profile.json          # Hub identity, fingerprint, config
├── hub-registry.json         # Project registry (auto-managed)
├── hub-learning-index.md     # Knowledge base index
├── hub-security-policy.json  # Hub security settings
└── AGENTS.md                 # Hub-specific agent instructions
```

These are distributed to hubs via teach, giving hubs same upgrade workflow as spokes.

---

## Universal Teach/Learn Protocol

### Current (v3.0.0)
```
Framework → Teach → Spokes
Hub ←→ Learn ← Spokes (separate mechanism)
```

### Future (v3.1)
```
Framework + Hub Templates → Universal Upgrade Plan
                          ↓ (teach command)
                    ↙            ↘
                Spokes          Hub
                (both apply same adoption logic)
                    ↓            ↓
              Adoption Decisions (AI-guided)
                    ↓            ↓
              Knowledge Flows Back → Learn
              (Hub learns from all spokes)
```

**Benefit:** Hub and spokes communicate in same language.

---

## Implementation Plan

### Phase 1: Upgrade Plan Schema (v3.1)
- [ ] Define upgrade-adoption-plan.json spec
- [ ] Add `mentions`, `why_changed`, `applies_to` fields
- [ ] Implement hub fingerprint signing
- [ ] Update teach command to generate plan

### Phase 2: Hub Templates (v3.1)
- [ ] Create templates/HUB/ directory
- [ ] Implement hub-profile.json template
- [ ] Implement hub-registry.json template
- [ ] Implement hub-learning-index.md template

### Phase 3: Spoke Verification (v3.2)
- [ ] Implement verify-upgrade command
- [ ] Add signature verification
- [ ] Add hash verification
- [ ] Update closeout to verify before adopting

### Phase 4: Universal Teaching (v3.2)
- [ ] Teach to hubs (using upgrade plan)
- [ ] Hub adoption workflow (same as spoke)
- [ ] Hub learning back to framework
- [ ] Test hub↔spoke knowledge flow

---

## Success Criteria

✓ Upgrade plan is signed (security)  
✓ Upgrade plan includes context (AI-friendly)  
✓ Files include version and reasoning  
✓ Spokes can verify before adopting  
✓ Hubs receive hub-specific templates  
✓ Hub and spoke use same teach/learn protocol  
✓ All knowledge flows bidirectionally  

---

## Related Decisions

- Replaces: `teaching-adoption-plan.json` 
- Renamed to: `upgrade-adoption-plan.json` (better semantics)
- Adds: Hub templates (`templates/HUB/`)
- Enables: Universal teach/learn across hub and spokes
- Security: Fingerprint-based verification

---

*Specification for upgrade adoption plan (architecture improvement, 2026-02-01)*
