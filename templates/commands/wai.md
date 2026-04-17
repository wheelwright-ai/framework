# WAI Wakeup Protocol

Execute wakeup to initialize the spoke.

---

## Check: Is Session Data Fresh?

Look for `<wai-session-init>` in context and check if it contains `Wakeup brief: FRESH`.

---

## FAST PATH — 0 tool calls (FRESH brief)

Pre-conditions met: hook pre-computed all data, track entry already written by session-start.sh.

**DO NOT make any tool calls.** Display the briefing immediately.

**Steps:**

**1. Interrupted session check.** If `Prev session: INTERRUPTED` in session-init CONTEXT HEALTH:
- Surface in briefing: `⚠ INTERRUPTED — [G]reen Light / [R]ed Light / [S]kip / [N]ew Project`

**2. Display banner** using session-init sections:

```
┌─ WAI WAKEUP Session-{N} [{session_name}] {today_date}
│  Project: {name} v{version}               ← STATIC DATA
│  Active: {epics_open} open, {epics_ip} ip | {other_open} other | {signals} signals
│  Queue: {ready} ready | {refinement} refinement     ← Expediter line
│  Vibe: none  |  Context: unknown — run /context
│  {If TEACHINGS New > 0: Teachings: N pending (Path A/B)}
│  {If HUB SIGNALS > 0: Hub signals: N framework}
│  {If recommendations valid: Navigator: N profiles current | If stale or null: ⚠ Navigator: recommendations stale}
│  {If TOOL ADVISOR audit due: ⚠ Tool audit due}
│  {If context feeds stale: Context feeds: N stale}
│  {If HISTORIAN ADVICE present: Historian: {first bullet}}
│  Next: {first item from NEXT ACTIONS}
└─ Ready to work.
```

**3. Ask:** `Vibe? (build / fix / think / grind / ship / refine) [skip]`

**4. Work Queue Interactive Mode:** After vibe prompt, if `_work_queue.items` has `>=1` ready item, display top-3 by ROI.

```python
import json, os
wai_state_path = 'WAI-Spoke/WAI-State.json'
if os.path.exists(wai_state_path):
    with open(wai_state_path, 'r') as f:
        wai_state = json.load(f)
    work_queue = wai_state.get('_work_queue', {})
    ready_items = sorted([
        item for item in work_queue.get('items', [])
        if item.get('readiness') == 'ready' and item.get('quality_score', 10) > 3
    ], key=lambda x: x.get('roi', 0), reverse=True)
    needs_refinement_items = [
        item for item in work_queue.get('items', [])
        if item.get('readiness') == 'needs_refinement'
    ]

    if ready_items:
        print("Work Queue:")
        for i, item in enumerate(ready_items[:3]):
            print(f"  [{i+1}] {item.get('id')} (ROI {item.get('roi', 'N/A')}) — {item.get('title')}")
        print("\n[W]ork top item / [R]eview refinements / [A]uto-chain / [S]kip")
    elif needs_refinement_items:
        print(f"Queue: 0 ready | {len(needs_refinement_items)} need refinement")
        print("\n[R]eview refinements / [S]kip")
    # If queue is completely empty, do nothing (silent).
```

Done. Zero tool calls.

---

## BRIEF PATH — 1 tool call (no session-init, brief exists)

Pre-conditions: No `<wai-session-init>` in context AND `WAI-Spoke/wakeup-brief.json` exists.

**Steps:**

1. Read `WAI-Spoke/wakeup-brief.json` (1 tool call)
2. Display banner:

```
┌─ WAI WAKEUP [brief-path] {today_date}
│  Project: v{spoke_version}
│  Open lugs: {open_lug_count} | Queue: {ready_count} ready | {needs_refinement_count} refinement
│  Context: unknown — run /context  |  Vibe: none
│  {If teachings_pending > 0: Teachings: N pending}
│  {If hub_signals_pending > 0: Hub signals: N pending}
│  Next: {next_actions[0] — first 120 chars}
└─ Ready to work. (brief-path)
```

3. Ask: `Vibe? (build / fix / think / grind / ship / refine) [skip]`

**4. Work Queue Interactive Mode:** (Same as FAST PATH Step 4, adapted for brief path)

```python
import json, os
wai_state_path = 'WAI-Spoke/WAI-State.json'
if os.path.exists(wai_state_path):
    with open(wai_state_path, 'r') as f:
        wai_state = json.load(f)
    work_queue = wai_state.get('_work_queue', {})
    ready_items = sorted([
        item for item in work_queue.get('items', [])
        if item.get('readiness') == 'ready' and item.get('quality_score', 10) > 3
    ], key=lambda x: x.get('roi', 0), reverse=True)
    needs_refinement_items = [
        item for item in work_queue.get('items', [])
        if item.get('readiness') == 'needs_refinement'
    ]

    if ready_items:
        print("Work Queue:")
        for i, item in enumerate(ready_items[:3]):
            print(f"  [{i+1}] {item.get('id')} (ROI {item.get('roi', 'N/A')}) — {item.get('title')}")
        print("\n[W]ork top item / [R]eview refinements / [A]uto-chain / [S]kip")
    elif needs_refinement_items:
        print(f"Queue: 0 ready | {len(needs_refinement_items)} need refinement")
        print("\n[R]eview refinements / [S]kip")
```

Done. 1 tool call.

**If brief does not exist:** fall through to FULL PROTOCOL.
**If brief is clearly stale** (git_sha_at_generation far behind HEAD): note staleness,
proceed anyway or fall through to FULL PROTOCOL.

---

## FULL PROTOCOL (STALE brief or no session-init)

### Step 1: Load Spoke Taste

Load `WAI-Spoke/taste.spoke.yaml`. If any `entries` have `status: proposed`, surface them in the briefing and prompt for action.

```python
import yaml, os
try:
    with open('WAI-Spoke/taste.spoke.yaml', 'r') as f:
        taste_data = yaml.safe_load(f)
    proposed_nudges = [e for e in taste_data.get('entries', []) if e.get('status') == 'proposed']
    if proposed_nudges:
        print(f"Taste nudges: {len(proposed_nudges)} proposed -- [a]ccept / [r]eject / [s]kip")
    # Historian nudge output format comment
    # {id, category, statement, evidence: [session_ids where correction occurred]}
except FileNotFoundError:
    pass # No taste.spoke.yaml yet, or it's empty/malformed.
```

### Step 1b: Navigator Startup (silent if hub absent)

Sync Navigator recommendations from hub and check catalog TTL.

```python
import json, datetime, os, shutil

nav_dir = 'WAI-Spoke/advisors/navigator'
cache_path = f'{nav_dir}/catalog-cache.json'
rec_local = f'{nav_dir}/recommendations-current.json'
now = datetime.datetime.now(datetime.timezone.utc)

# Catalog TTL check (warn only)
if os.path.exists(cache_path):
    cache = json.load(open(cache_path))
    if cache.get('cached_at'):
        age_h = (now - datetime.datetime.fromisoformat(cache['cached_at'])).total_seconds() / 3600
        if age_h > cache.get('ttl_hours', 24):
            print(f'⚠ Navigator catalog cache stale ({age_h:.0f}h old) — will refresh on next nightly run.')

# Recommendations sync from hub (silent skip if hub absent)
try:
    state = json.load(open('WAI-Spoke/WAI-State.json'))
    hub_path = state.get('_hub', {}).get('path') or state.get('hub_path')
    if hub_path:
        hub_rec = os.path.join(hub_path, 'WAI-Hub/advisors/navigator/recommendations-current.json')
        if os.path.exists(hub_rec):
            shutil.copy2(hub_rec, rec_local)
            rec = json.load(open(rec_local))
            if os.path.exists(cache_path):
                cache = json.load(open(cache_path))
                cache['recommendations_pulled_at'] = now.isoformat()
                cache['recommendations_valid_through'] = rec.get('valid_through')
                json.dump(cache, open(cache_path, 'w'), indent=2)
            n_profiles = len(rec.get('profiles', {}))
            valid_through = rec.get('valid_through')
            if valid_through and datetime.datetime.fromisoformat(valid_through) > now:
                print(f'Navigator: {n_profiles} recommendation profiles current')
            else:
                print(f'⚠ Navigator: recommendations stale — hub nightly run may be overdue')
except Exception:
    pass  # hub not connected or file absent — silent skip
```

### Step 2: Execute Full Protocol

Use `Read` to load `templates/commands/wai-full.md`, then execute all steps in that document.

---

*Fast path: 0 tool calls, ~15s. Brief path: 1 tool call. Full protocol in wai-full.md (loaded on demand).*


Convergence rules for all tools:
- Finish the WAI Point briefing before pausing for teaching approval or any other side action.
- During wakeup, inspect teachings using filenames and lightweight header/frontmatter fields only. Do NOT read full teaching bodies unless the user explicitly asks to review them now.
- If pending teachings exist, include them in the briefing under a compact "Pending Teachings" section, then ask what to do next.


Output contract for all tools:
- Output the completed WAI Point briefing directly; do not narrate shell probes or bootstrap steps before it.
- Keep the post-brief closeout to one short readiness line such as `Wake complete. Ready to work.`
- Do not replace the briefing with a numbered next-steps plan unless the user explicitly asks for planning.
- If teachings or stale-task decisions need approval, list them compactly under `Pending Items` inside the briefing rather than stopping early.
