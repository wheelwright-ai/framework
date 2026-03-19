# Canonical Wheelwright Migration Guide

This guide covers migration to the canonical Wheelwright object model and behavior.

## Canonical Architecture

The canonical Wheelwright model uses these core objects:

| Component | Purpose | Canonical File |
|-----------|---------|----------------|
| **Wheel** | Top-level network identity | `WAI-State.json` (wheel section) |
| **Hub** | Coordination node | Hub directory with registry |
| **Spoke** | Project-local installation | `WAI-Spoke/` directory |
| **Skills** | Operational protocols | `WAI-Spoke/commands/*.md` |
| **Lugs** | Work/intelligence records | `WAI-Spoke/WAI-Lugs.jsonl` |
| **Sessions** | Bounded work intervals | `WAI-Spoke/sessions/` |
| **Tracks** | Session telemetry | `session-*/track.jsonl` |

## Migration Principles

The canonical migration follows dual-read/single-write compatibility:

1. **Dual-read capability** - Framework can understand both legacy and canonical formats
2. **Single canonical write** - New writes use canonical format only  
3. **Idempotent adoption** - Migration can be safely repeated
4. **Rollback support** - Migration receipts enable safe rollback
5. **Hub visibility** - Hub tracks migration status per spoke

## Migration Process

### Phase 1: Pre-Migration Backup

Create rollback checkpoint before any changes:

```bash
# Create migration checkpoint
cp WAI-Spoke/WAI-State.json WAI-State-pre-canonical-$(date +%Y%m%d-%H%M).json
cp -r WAI-Spoke WAI-Spoke-backup-$(date +%Y%m%d-%H%M)
git add . && git commit -m "Migration checkpoint: pre-canonical state"
```

### Phase 2: Framework Version Verification  

Check framework version compatibility in `WAI-State.json`:

```json
{
  "wheel": {
    "framework_version": "3.0.0",
    "version": "your-project-version"
  }
}
```

**Note:** `framework_version` tracks Wheelwright capability level, `version` tracks your project.

### Phase 3: Migration State Initialization

Add `_migration_state` section to `WAI-State.json` for adoption tracking:

```json
{
  "_migration_state": {
    "_purpose": "Tracks capability adoption and migration receipts for dual-read/single-write compatibility",
    "framework_migrations_applied": [],
    "capability_adoptions": [], 
    "migration_receipts": [],
    "rollback_checkpoints": [],
    "dual_read_capabilities": {
      "state_format": "v3_canonical_with_v1_v2_compat",
      "signal_storage": "canonical_lugs_with_signals_compat",
      "track_storage": "canonical_sessions_with_flat_compat"
    },
    "adoption_markers": {
      "canonical_runtime_baseline": {
        "adopted": false,
        "adopted_at": null,
        "adopted_by": null,
        "receipt_id": null,
        "rollback_checkpoint": null
      },
      "canonical_state_migration": {
        "adopted": false,
        "adopted_at": null,
        "adopted_by": null,
        "receipt_id": null,
        "rollback_checkpoint": null
      }
    },
    "compatibility_notes": "This section enables dual-read during migration while maintaining single canonical write target",
    "last_migration_check": null
  }
}
```

### Phase 4: Signal Migration

**Legacy Pattern:** Separate `WAI-Signals.jsonl` file
**Canonical Pattern:** High-impact lugs (impact >= 8) in `WAI-Lugs.jsonl`

If you have existing signals in `WAI-Signals.jsonl`:

```bash
# Review existing signals
cat WAI-Spoke/WAI-Signals.jsonl

# Each signal becomes a high-impact lug in WAI-Lugs.jsonl
# Manual conversion required - automated tooling pending
```

### Phase 5: Track Storage Migration  

**Legacy Pattern:** Flat `track_*.jsonl` files in `WAI-Spoke/`
**Canonical Pattern:** Session directories `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`

```bash
# Create canonical session directory structure
mkdir -p WAI-Spoke/sessions/

# Move existing tracks (if any) to session directories
# Update WAI-State.json _session_state.track_path accordingly
```

### Phase 6: State Template Migration

**Legacy Pattern:** Mixed schema generations with BRIEF.md/WAI-Manifest.yaml references
**Canonical Pattern:** WAI-State.json with canonical `wheel` section and `_compatibility` section

1. Ensure `wheel` section is primary with proper `framework_version` separation
2. Move legacy fields to `_compatibility` section  
3. Remove references to BRIEF.md, WAI-Manifest.yaml, EXTENSION.md patterns

## Migration Validation

After migration, verify canonical compliance:

1. **State Structure:** `wheel` section is primary, legacy in `_compatibility`
2. **Signal Storage:** High-impact decisions stored as lugs in `WAI-Lugs.jsonl` 
3. **Track Storage:** Session tracks in canonical directory structure
4. **Framework Version:** Properly separated from project version
5. **Migration Receipts:** All adoptions tracked in `_migration_state`

## Rollback Process

If migration issues occur:

```bash
# Restore from checkpoint
cp WAI-State-pre-canonical-YYYYMMDD-HHMM.json WAI-Spoke/WAI-State.json
rm -rf WAI-Spoke/sessions/  # if canonical sessions were created
git reset --hard HEAD~1  # back to migration checkpoint commit
```

## Post-Migration

- Update `_migration_state.adoption_markers` as capabilities are adopted
- Use dual-read capability during transition period
- Monitor `_migration_state.last_migration_check` for compatibility status

## Deprecated Patterns

These patterns are **incompatible** with canonical Wheelwright:

❌ **BRIEF.md as control plane** - Use WAI-State.json `wheel` section
❌ **WAI-Manifest.yaml** - Use WAI-State.json migration tracking  
❌ **EXTENSION.md** - Use skill system (`WAI-Spoke/commands/`)
❌ **Separate WAI-Signals.jsonl** - Use high-impact lugs in WAI-Lugs.jsonl
❌ **Flat track storage** - Use canonical session directories
❌ **CLI teach/learn commands** - Use wakeup/closeout protocol
