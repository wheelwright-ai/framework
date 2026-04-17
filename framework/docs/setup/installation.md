# Installation & Setup

## Prerequisites

- Git repository (local or remote)
- AI coding agent (Claude Code, Cursor, etc.)
- Basic familiarity with YAML and JSONL formats

## Quick Setup (New Project)

### 1. Install WAI Framework

Clone the Wheelwright framework:

```bash
git clone https://github.com/wheelwright-ai/framework.git
cd framework
```

### 2. Create Your Spoke

```bash
mkdir -p /path/to/your-project/WAI-Spoke
cd /path/to/your-project
```

Copy spoke templates:

```bash
cp framework/templates/WAI-Spoke/* ./WAI-Spoke/
cp framework/templates/BRIEF.md ./BRIEF.md
cp framework/templates/EXTENSION.md ./EXTENSION.md
```

### 3. Configure Your Spoke

Edit `WAI-Spoke/WAI-Manifest.yaml`:

```yaml
node_type: spoke
node_path: "your-org/your-project"
framework_version: "2.0.0"
hub_lug_cursor: null
skills_loaded:
  - safe-refactor
  - session-observer
last_session: null
outbound_pending: []
```

Edit `EXTENSION.md`:

```markdown
## Identity

**Role:** [Your role - CTO, PM, QA, etc.]
**Lens:** [Your perspective - what you focus on]

**Primary Focus:**
- [Key responsibility 1]
- [Key responsibility 2]
```

Edit `BRIEF.md`:

```markdown
# BRIEF — your-project

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md

## Always
- [Non-negotiable rule 1]
- [Non-negotiable rule 2]

## Never
- [Prohibited action 1]
- [Prohibited action 2]

## When Uncertain
- [Clarification source 1]
- [Clarification source 2]
```

### 4. Connect to Hub (Optional)

If you have a central hub for cross-project learning:

Edit `WAI-Spoke/WAI-State.json` (if exists) or create it:

```json
{
  "hub_path": "/path/to/wheelwright-hub",
  "subscriptions": ["hub:framework:*", "hub:pattern:*"]
}
```

### 5. Load Framework in Your IDE

Add to `.cursorrules`, `CLAUDE.md`, or equivalent:

```markdown
# Wheelwright Framework

Load WAI context on session start:
1. Read BRIEF.md (behavioral rules)
2. Read EXTENSION.md (role and lens)
3. Read WAI-Spoke/WAI-Manifest.yaml (framework config)
4. Check WAI-Spoke/WAI-Ledger.jsonl for open commitments

Skills auto-fire based on triggers. Let them run.

Create Lugs as you work (diagnosis, prescription, decision).
```

## Hub Setup (Optional - For Cross-Project Learning)

### 1. Create Hub Directory

```bash
mkdir -p /path/to/wheelwright-hub
cd /path/to/wheelwright-hub
```

### 2. Initialize Hub Structure

```bash
cp -r framework/hub/* ./
```

This creates:
- `hub/BRIEF.md` (wheel-wide policies)
- `hub/WAI-Integrity.md` (data protection contract)
- `hub/registry.yaml` (all registered nodes)
- `hub/health.yaml` (hub health status)
- `hub/intake/` (pending signals from spokes)
- `hub/WAI-Lugs.jsonl` (hub learning log)

### 3. Register Your Spokes

Edit `hub/registry.yaml`:

```yaml
nodes:
  - path: "wheelwright/hub"
    type: hub
    status: active
    framework_version: "2.0.0"
    description: "Central Hub"

  - path: "your-org/project-1"
    type: spoke
    status: active
    framework_version: "2.0.0"
    description: "Project 1 description"

  - path: "your-org/project-2"
    type: spoke
    status: active
    framework_version: "2.0.0"
    description: "Project 2 description"
```

## Verification

After setup, verify WAI is working:

### Spoke Verification

Run this prompt in your spoke project:

```
Verify WAI v2 working:
1. Does BRIEF.md mention cascade or hub inheritance?
2. What's my role AND lens from EXTENSION.md?
3. What's my node_path from WAI-Manifest.yaml?
4. Does WAI-Ledger.jsonl exist and is it append-only?
5. Does skills/ directory exist?
6. Create a test ledger entry and show it
```

Expected output: All checks pass, test entry created.

### Hub Verification (if using hub)

Run this in hub project:

```
Hub health check:
1. Does hub/registry.yaml exist with all spokes listed?
2. Does hub/BRIEF.md exist with wheel-wide policies?
3. Does hub/WAI-Integrity.md exist with data protection rules?
4. Does hub/intake/ directory exist?
5. How many spokes are registered?
```

Expected output: All files exist, registry shows your spokes.

## Troubleshooting

### "Framework files not found"

**Symptom:** Agent can't find templates or skills
**Solution:** Verify `framework_version` in WAI-Manifest.yaml matches installed version

### "Hub not accessible"

**Symptom:** hub-watcher reports connection failure
**Solution:** Check `hub_path` in WAI-State.json points to correct absolute path

### "Skills not firing"

**Symptom:** safe-refactor doesn't run before changes
**Solution:** Verify skills are listed in WAI-Manifest.yaml `skills_loaded` array

### "Documentation drift flagged"

**Symptom:** Closeout warns about doc updates needed
**Solution:** This is expected - update docs before closing session

## Next Steps

- Read [core-concepts.md](../start-here/core-concepts.md) to understand Skills and Lugs
- Explore [skills documentation](../skills/built-in/) to see available skills
- Check [use-cases.md](./use-cases.md) for common scenarios
- Review [hub-architecture.md](../hub/architecture.md) if using cross-project learning
