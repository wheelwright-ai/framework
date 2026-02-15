# Migration Guide: v1 to v2

This guide covers migrating from WAI v1 (CLI-based) to v2 (file-based protocol).

## What Changed

### Architecture Shift

| Aspect | v1 (CLI) | v2 (File Protocol) |
|--------|----------|-------------------|
| Commands | `wai status`, `wai teach` | Skills (YAML files) |
| State | WAI-State.json | WAI-Manifest.yaml + BRIEF.md |
| Signals | Separate system | Lugs with impact >= 8 |
| Backpressure | Explicit signals | Skills (advisor role) |
| Communication | CLI prompts | File-based (read/write) |

### Why the Change

On 2026-02-10, the v1 CLI accidentally destroyed the Hub folder during a file restructuring operation. The CLI had too much power without adequate safeguards.

v2 enforces:
- **File-based communication** - No destructive CLI commands
- **WAI-Integrity.md** - Data protection contract
- **safe-refactor** - Git checkpoint before structural changes
- **Append-only files** - Lugs and ledgers only grow

## Migration Steps

### Step 1: Backup v1 Data

```bash
cp -r WAI-Spoke WAI-Spoke-v1-backup
cp WAI-State.json WAI-State-v1.json
cp WAI-State.md WAI-State-v1.md
```

### Step 2: Create v2 Structure

```bash
# Create new v2 files
touch BRIEF.md
touch EXTENSION.md
mkdir -p WAI-Spoke

# Create v2 manifest
cat > WAI-Spoke/WAI-Manifest.yaml << 'EOF'
node_type: spoke
node_path: "your-org/your-project"
framework_version: "2.0.0"
template_versions:
  lugs: 2
  brief: 1
  guide: 1
hub_lug_cursor: null
skills_loaded:
  - safe-refactor
  - session-observer
last_session: null
outbound_pending: []
EOF
```

### Step 3: Migrate BRIEF Rules

Extract behavioral rules from v1 state files into BRIEF.md:

**v1 WAI-State.json:**
```json
{
  "rules": {
    "always": ["Run tests before commit"],
    "never": ["Deploy without approval"]
  }
}
```

**v2 BRIEF.md:**
```markdown
# BRIEF — your-project

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md

## Always
- Run tests before commit

## Never
- Deploy without approval
```

### Step 4: Create EXTENSION.md

Define your spoke's identity:

```markdown
# your-project Extension

## Identity

**Role:** [Your role from v1 wheel.role]
**Lens:** [What you focus on]

**Primary Focus:**
- [Key responsibility 1]
- [Key responsibility 2]

## Skills Loaded

- safe-refactor (guardian)
- session-observer (watcher)
```

### Step 5: Migrate Lugs

v1 Lugs should already be in WAI-Lugs.jsonl. Verify format:

**v1 format:**
```json
{"id": "lug-001", "type": "diagnosis", "title": "Bug found", ...}
```

**v2 format (same, but verify fields):**
```json
{"id": "lug-001", "type": "diagnosis", "title": "Bug found", "status": "published", "impact": 7, "node": "your-org/your-project", ...}
```

If missing v2 fields, run migration script:
```bash
python3 framework/archive/scripts/migrate_lugs_v2.py WAI-Spoke/WAI-Lugs.jsonl
```

### Step 6: Create Session Ledger

```bash
cat > WAI-Spoke/WAI-Ledger.jsonl << 'EOF'
# WAI Session Ledger
# CRITICAL: This file is append-only per WAI-Integrity.md

EOF
```

### Step 7: Remove v1 CLI (Optional)

If you were using the `wai` CLI command:

```bash
# Check if wai CLI is installed
which wai

# Remove from PATH if present
# (depends on how you installed it)
```

v2 doesn't use a CLI. Skills are YAML files that agents read and execute.

### Step 8: Verify Migration

Run this prompt in your project:

```
Verify WAI v2 migration:
1. Does BRIEF.md exist with cascade mention?
2. Does EXTENSION.md exist with role and lens?
3. Does WAI-Spoke/WAI-Manifest.yaml exist with framework_version: "2.0.0"?
4. Does WAI-Spoke/WAI-Ledger.jsonl exist?
5. Are Lugs in WAI-Lugs.jsonl valid (have id, type, status, impact)?
```

## Handling Signals

### v1 Signals
In v1, signals were a separate system with their own flow.

### v2 Signals
In v2, signals are just Lugs with `impact >= 8`:

```json
{
  "id": "lug-001",
  "type": "observation",
  "title": "Security pattern applicable across projects",
  "impact": 9,  // >= 8 makes it a signal
  "outbound_submitted_to": "hub/intake",
  "outbound_submitted_at": "2026-02-14T00:00:00Z"
}
```

Migrate v1 signals by converting them to high-impact Lugs.

## Handling Backpressure

### v1 Backpressure
Explicit backpressure signals to slow down conductors.

### v2 Backpressure
Skills with advisor role:
- `complexity-advisor` - Warns when task is complex
- `context-advisor` - Warns when context is filling up
- `stewardship-advisor` - Warns about scope drift

These are defined in YAML, not sent as explicit signals.

## Common Issues

### "Framework files not found"
**Cause:** Agent looking for v1 file structure
**Solution:** Ensure WAI-Manifest.yaml exists with `framework_version: "2.0.0"`

### "Skills not running"
**Cause:** v1 expected CLI commands
**Solution:** Skills are YAML files that agents read and execute automatically

### "Hub connection failed"
**Cause:** v1 used different hub path
**Solution:** Update hub_path in WAI-State.json (if used) or configure hub connection

## Rollback

If migration fails:

```bash
# Restore v1 backup
rm -rf WAI-Spoke
mv WAI-Spoke-v1-backup WAI-Spoke
mv WAI-State-v1.json WAI-State.json
mv WAI-State-v1.md WAI-State.md
rm BRIEF.md EXTENSION.md
```

## Post-Migration

After successful migration:

1. **Remove v1 backups** (after verification)
2. **Update .gitignore** to exclude v1 artifacts
3. **Test wakeup and closeout** with new structure
4. **Create decision Lug** documenting the migration
