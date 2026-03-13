# WAI Teach

**Push Distribution Protocol — send your templates and lugs to a target node.**

```
teach = PUSH (active, sender-initiated)
learn = PULL (passive, automatic on wakeup)
```

---

## Execution Context

- **Nodes:** spoke (when teaching hub), hub (when teaching spokes)
- **Exposure:** spoke.chat:local
- **Trigger:** User runs `/wai-teach [target]`

## When to Use

- After completing work worth sharing (impact >= 8)
- After updating skills or protocols in `templates/commands/`
- To deliver lugs from your outbox to a target spoke or hub
- To initialize a new project as a spoke (auto-detects and creates structure)
- When hub sync is > 7 days old (flagged in wakeup briefing)

---

## Concept

Teaching is the act of **pushing what you know to another node**. The sender (you) places files and lugs into the target's inbox. The target learns them automatically on their next wakeup.

**Auto-detects spoke status**: If the target directory is not a spoke (no `WAI-Spoke/WAI-State.json`), teaching automatically initializes it with the complete spoke template structure before distributing files.

```
YOUR NODE                           TARGET NODE
┌──────────────┐                    ┌──────────────┐
│  outbox/     │ ──[/wai-teach]──►  │  inbox/      │
│  templates/  │                    │  seed/ingest/│
└──────────────┘                    └──────────────┘
```

---

## What Gets Distributed

### 1. Template Files (Skills and Protocols)

Framework template files are distributed **with `.teaching` extension** into the target's `seed/ingest/` directory:

```
templates/commands/wai-closeout.md  →  target/WAI-Spoke/seed/ingest/wai-closeout.md.teaching
templates/commands/wai-teach.md     →  target/WAI-Spoke/seed/ingest/wai-teach.md.teaching
```

The `.teaching` extension signals that the file requires **verification before adoption** (the teach verification ceremony).

**Exception:** Hub-specific files (hub-registry.json, hub-security-policy.json) are distributed WITHOUT the `.teaching` extension for immediate adoption.

### 2. Lugs from Outbox

Lugs in your `WAI-Spoke/lugs/outbox/` that have a `destination_wheel_id` matching the target are copied to the target's `WAI-Spoke/lugs/inbox/`:

```
your outbox/task-for-basher.jsonl  →  basher/WAI-Spoke/lugs/inbox/task-for-basher.jsonl
```

**Routing rule:** Only lugs where `destination_wheel_id` matches the target node name or spoke name are delivered. Non-matching lugs are skipped and left in outbox.

**After delivery:** The original lug remains in outbox; a delivery confirmation lug is sent to the hub's inbox (unless self-delivering).

### 3. Upgrade Adoption Plan

An `upgrade-adoption-plan.json` is generated and saved in the target root. This plan:
- Lists all files being distributed
- Records framework version (`wheel.version`)
- Marks each file's `safe_to_auto_adopt` flag (true = automatic, false = requires review)
- Is signed with hub fingerprint (HMAC via hub-profile.json → `hub_config.fingerprint`)

Schema:
```json
{
  "metadata": {
    "framework_version": "2.0.7",
    "spoke_structure_version": "3.0",
    "generated_at": "ISO-8601",
    "source": "framework"
  },
  "verification": {
    "hub_fingerprint": "sha256-hash",
    "signature": "hmac-sha256-value"
  },
  "files": [
    {
      "name": "wai-closeout.md",
      "path": "WAI-Spoke/seed/ingest/wai-closeout.md.teaching",
      "version": "2.0.7",
      "changed_from": "2.0.6",
      "why_changed": "Removed deliver_outbox_lugs() reference",
      "safe_to_auto_adopt": true,
      "requires_review": false,
      "applies_to": ["spoke", "hub"]
    }
  ]
}
```

---

## Hub Registry Update

After teaching, update the hub registry (`hub-registry.json`) to record the teach event:

- `wheel.taught_at` — timestamp
- `wheel.taught_version` — framework version taught
- `wheel.last_sync` — same timestamp
- `teaching_history` — append event with `{event_id, timestamp, framework_version, wheels_taught, spokes_taught, files_per_spoke, status}`
- `statistics.last_teach`, `statistics.total_wheels`, `statistics.taught_wheels`

---

## Spoke Detection

Before teaching, determine if target is a spoke:

### Detection Steps

1. **Get target path**:
   - From `WAI-State.json` → `wheel.hub_path` (when teaching hub)
   - Or user-provided target path (when teaching a spoke)

2. **Check for spoke marker**:
   ```bash
   if [ -f "$target_path/WAI-Spoke/WAI-State.json" ]; then
     # Is a spoke - proceed to teach
   else
     # Not a spoke - initialize first
   fi
   ```

### Detection Decision Tree

| Condition | Action |
|-----------|--------|
| `target_path/WAI-Spoke/WAI-State.json` exists | Proceed to [Teach Protocol Steps](#teach-protocol-steps) |
| Target directory exists but no WAI-Spoke/ | Proceed to [Spoke Initialization](#spoke-initialization) |
| Target directory does not exist | Ask user: "Target path does not exist. Create it?" |

---

## Spoke Initialization

When target is not a spoke, initialize it from `templates/spoke/` template.

### Init Steps

#### 1. Identify Framework Path

Determine where the `templates/` directory lives:

```bash
# Check current WAI-State.json for framework path
framework_path=$(jq -r '.wheelwright.framework_path' WAI-Spoke/WAI-State.json)

# If null, prompt user
if [ "$framework_path" == "null" ]; then
  echo "Framework path not found in WAI-State.json"
  echo "Enter path to Wheelwright framework (where templates/ lives):"
  read framework_path
fi
```

#### 2. Initialize Spoke Structure

Copy the complete spoke template to target:

```bash
# Copy all files including hidden files
cp -r "$framework_path/templates/spoke/"* "$target_path/"
cp -r "$framework_path/templates/spoke/".* "$target_path/" 2>/dev/null || true

# Create required directories if missing
mkdir -p "$target_path/WAI-Spoke/seed/ingest"
mkdir -p "$target_path/WAI-Spoke/lugs/inbox"
mkdir -p "$target_path/WAI-Spoke/lugs/outbox"
mkdir -p "$target_path/WAI-Spoke/sessions"
```

#### 3. Configure WAI-State.json with Smart Defaults

Update the target's `WAI-Spoke/WAI-State.json`:

```bash
# Extract smart defaults
project_name=$(basename "$target_path")
framework_version=$(jq -r '.wheel.version' WAI-Spoke/WAI-State.json)
spoke_id=$(echo -n "$project_name" | sha256sum | cut -c1-12)

# Check if it's a git repo
if [ -d "$target_path/.git" ]; then
  repo_url=$(cd "$target_path" && git remote get-url origin 2>/dev/null || echo "unknown")
else
  repo_url=null
fi

# Update target WAI-State.json
jq --arg name "$project_name" \
   --arg version "$framework_version" \
   --arg spoke_id "$spoke_id" \
   --arg repo "$repo_url" \
   '.wheel.name = $name |
    .wheel.version = $version |
    .wheel.spoke_id = $spoke_id |
    .wheel.repository = $repo' \
   "$target_path/WAI-Spoke/WAI-State.json" > "$target_path/WAI-Spoke/WAI-State.json.tmp" \
   && mv "$target_path/WAI-Spoke/WAI-State.json.tmp" "$target_path/WAI-Spoke/WAI-State.json"
```

#### 4. Prompt for Hub Path

Ask user where the hub is located (needed for registration):

```bash
echo "Enter hub path for this spoke:"
echo "(Example: /home/user/projects/wheelwright-hub)"
read hub_path
```

#### 5. Register Spoke in Hub Registry

Load the hub's registry and add the new wheel:

```bash
hub_registry="$hub_path/hub-registry.json"

# Generate unique wheel ID
wheel_id="$project_name"
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Add wheel entry to registry
jq --arg wheel_id "$wheel_id" \
   --arg spoke_id "$spoke_id" \
   --arg path "$target_path" \
   --arg timestamp "$timestamp" \
   --arg version "$framework_version" \
   '.wheels += [{
     "wheel_id": $wheel_id,
     "spoke_id": $spoke_id,
     "path": $path,
     "status": "active",
     "taught_at": $timestamp,
     "taught_version": $version,
     "last_sync": $timestamp,
     "learnings_contributed": 0,
     "signals_received": [],
     "adoptions": [],
     "module_adoption": {
       "lugs": "2.0",
       "registry": "3.0",
       "teach": "1.0"
     },
     "pending_contributions": {},
     "adoption_lag": {
       "behind_modules": [],
       "missing_modules": []
     }
   }] |
   .statistics.total_wheels += 1 |
   .statistics.active_wheels += 1 |
   .statistics.last_teach = $timestamp' \
   "$hub_registry" > "$hub_registry.tmp" \
   && mv "$hub_registry.tmp" "$hub_registry"
```

### Post-Init Confirmation

After initialization, present confirmation:

```
## Spoke Initialized ✓

Created: /path/to/target
- Name: [directory_name]
- Spoke ID: [spoke_id]
- Hub: [hub_path]
- Version: [framework_version]
- Git Repo: [repo_url or "none"]

Registered in hub registry.

Next: Proceeding to teach skills and lugs...
```

Then continue to [Teach Protocol Steps](#teach-protocol-steps).

---

## Teach Protocol Steps

**Prerequisite**: Target is a verified spoke (either existing or newly initialized via [Spoke Initialization](#spoke-initialization))

1. **Identify target** — hub path from `WAI-State.json` → `wheel.hub_path`, or explicit target name
2. **Check target exists** — verify directory and WAI-Spoke/ structure
3. **Scan templates** — collect files from `templates/commands/` and `templates/spoke/`
4. **Build upgrade adoption plan** — with file hashes, version, safe_to_auto_adopt flags
5. **Sign plan** — with hub fingerprint from `hub-profile.json` → `hub_config.fingerprint`
6. **Distribute template files** — copy with `.teaching` extension to `target/WAI-Spoke/seed/ingest/`
7. **Deliver outbox lugs** — copy matching lugs to `target/WAI-Spoke/lugs/inbox/`
8. **Save adoption plan** — write `upgrade-adoption-plan.json` to target root
9. **Send delivery confirmations** — write confirmation lug to hub's inbox for each delivered lug
10. **Update hub registry** — record teach event in `hub-registry.json`
11. **Report summary** — show files distributed, lugs delivered, version taught

---

## Self-Delivery

When teaching yourself (framework teaching its own WAI-Spoke), delivery confirmations are skipped. Log: `[SELF] Skipping confirmation (self-delivery)`.

---

## Output Format

```
Teaching [target]...

Template Files:
✓ wai-closeout.md → seed/ingest/wai-closeout.md.teaching
✓ wai-learn.md → seed/ingest/wai-learn.md.teaching
✓ [N files total]

Lugs Delivered:
✓ task-for-basher.jsonl → basher/lugs/inbox/

Upgrade Plan: upgrade-adoption-plan.json (signed)
Registry: Updated hub-registry.json

Teaching complete — [target] will learn on next wakeup.
```

---

## Version Comparison

Framework version is stamped into each upgrade adoption plan. The target determines if it's already up to date by comparing:
- `upgrade-adoption-plan.json` → `metadata.framework_version`
- vs current `WAI-State.json` → `wheel.version`

If target version >= plan version, no adoption needed.

---

## Related Skills

- `/wai` — Wakeup (triggers automatic learning from inbox)
- `/wai-learn` — Inbox processing protocol
- `/wai-closeout` — Captures session state; run before teaching hub

---

*Teach = Intentional push. The sender decides what to share.*
