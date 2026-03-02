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
- When hub sync is > 7 days old (flagged in wakeup briefing)

---

## Concept

Teaching is the act of **pushing what you know to another node**. The sender (you) places files and lugs into the target's inbox. The target learns them automatically on their next wakeup.

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

## Teach Protocol Steps

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
