# Hub Knowledge Base Curator

**Aggregate high-value signals and patterns from all connected spokes into reusable hub teachings.**

---

## Execution Context

- **Nodes:** hub only
- **Exposure:** hub.chat:local
- **Trigger:** `/hub-knowledge-base-curator` — run periodically (not at every wakeup)

---

## What This Skill Does

Each spoke generates signals — high-impact decisions and learnings. Most of these are
spoke-specific, but some represent patterns that would benefit every spoke on the fleet.
This skill identifies cross-spoke patterns, curates them into teaching files, and stages
them for distribution.

**Without this skill:** Each new spoke independently rediscovers the same patterns.
**With this skill:** The hub acts as institutional memory — one spoke's learning becomes
every spoke's baseline.

---

## Step 1: Collect Signals Across Fleet

For each registered spoke (from hub registry):

```bash
# Read signals from each spoke's WAI-Lugs.jsonl
# A signal is any lug with type="signal" and impact >= 8
```

Collect all signals not yet present in `hub/WAI-Lugs.jsonl`.

**Dedup check:** Use `id` field. If a signal with the same `id` already exists in the hub's
lugs, skip it.

---

## Step 2: Identify Cross-Spoke Patterns

Group collected signals by topic cluster. Look for:

- **Same problem, multiple spokes:** Two or more spokes flagged the same issue independently
- **Protocol evolution:** A signal describes a change that should apply to all spokes
- **Anti-pattern capture:** A signal describes something that went wrong (prevention value for others)

Signals that appear on 2+ spokes, or that describe universal protocol behavior, are candidates
for hub teachings.

---

## Step 3: Curate Teaching Candidates

For each candidate signal or pattern:

1. Read the signal(s) fully
2. Assess: is this a spoke-specific detail, or a universal pattern?
3. If universal: draft a teaching outline

```
Teaching candidate: {signal title}
Source spokes: {spoke1}, {spoke2}
Pattern: {one-paragraph description}
Teaching type: signal | skill | migration
safe_to_auto_adopt: true/false
Reason for false: {if applicable}
```

4. Present candidates to user for approval before creating teaching files

---

## Step 4: Create Teaching Files (User-Approved Only)

For each approved candidate:

Create a teaching file in `hub/teachings_repo/framework/current/`:

```
{type}-{topic}-v{N}.md.teaching
```

Follow the teaching file standard:
- Include `## Prerequisites` block with runnable PASS/FAIL checks
- Include `## Batch Sequence` block with apply order
- `safe_to_auto_adopt: true` only if the change is purely additive and low-risk
- Embed the actual content (not a pointer to it)

---

## Step 5: Update Hub Lugs

Append a `curation-run` lug to `hub/WAI-Lugs.jsonl`:

```json
{
  "id": "curation-{YYYYMMDD-HHMM}",
  "type": "curation-run",
  "timestamp": "ISO-8601",
  "signals_reviewed": N,
  "patterns_found": M,
  "teachings_created": K,
  "teaching_ids": ["..."],
  "fw_ver": "{current_fw_ver}",
  "created_by": "hub-knowledge-base-curator"
}
```

---

## What NOT to Do

- Do NOT auto-create teachings without user approval (Step 4 is gated)
- Do NOT include spoke-specific business logic in hub teachings
- Do NOT overwrite an existing teaching with a lower-version update
- Do NOT create duplicate teachings — check `current/` before creating

---

## Related Skills

- `hub-registry-verification.md` — prerequisite: need reachable spokes to collect from
- `hub-health-monitor.md` — provides context on fleet activity for curation timing
- `wai-closeout.md` Step 9b — how spoke signals flow up to the hub
