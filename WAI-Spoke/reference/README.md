# WAI-Spoke Reference Folder

**Purpose:** Documentation, historical snapshots, and reference materials that should NOT be loaded on every session start.

---

## Load Policy Philosophy

Wheelwright optimizes token usage through **intelligent lazy-loading**. Files are categorized by load policy:

| Policy | When Loaded | Token Impact | Examples |
|--------|-------------|--------------|----------|
| **always** | Every session start | ~13K tokens | WAI-State.json, WAI-State.md, WAI-AI-ONBOARDING.md |
| **summary_only** | Metadata/stats only | ~5K tokens | WAI-Lugs.jsonl (IDs+titles), WAI-Signals.jsonl (recent 10) |
| **on_request** | When explicitly needed | 0 (until requested) | WAI-Guide.md, commands/*.md, reference docs |
| **never** | Debugging/special cases only | 0 (unless debugging) | sessions/, seed/processed/, reference/auto/ |

**Result:** Only 18K tokens loaded automatically (9% of 200K budget), saving 120K+ tokens per session.

---

## Folder Structure

### `/reference/auto/`
**Load Policy:** `never`  
**Purpose:** Historical snapshots and backups created automatically during closeout

**Contents:**
- `WAI-Lugs.jsonl.v1-backup` - Lug format migration backup
- `WAI-State-SESSION-END.json` - State snapshots
- `SESSION-CLOSEOUT-*.md` - Detailed closeout reports
- `_framework/` - Framework template snapshots
- `_hooks/` - Hook script snapshots

**When to Load:** Only during debugging, rollback, or historical analysis

---

### `/reference/manual/`
**Load Policy:** `on_request`  
**Purpose:** Manually curated reference documentation

**Contents:**
- Project-specific reference docs
- Architecture decision records
- Implementation guides

**When to Load:** When working on specific features that require this context

---

### `/reference/` (root level)
**Load Policy:** Mixed (see WAI-File-Index.json)

**Key Files:**
- `WAI-AI-ONBOARDING.md` (`always`) - AI interaction model, command reference
- `WAI-VERSION-GUIDE.md` (`on_request`) - Version compatibility matrix
- `WAI-MERGE-PROTOCOLS.md` (`on_request`) - JSON merge guidance for teachings
- `WAI-Hub-Index.md` (`on_request`) - Hub connection metadata

---

## For AI Agents

### On Session Start
1. **Load:** WAI-File-Index.json to understand what's available
2. **Review:** Files marked `always` are already loaded in your context
3. **Check:** Summary data from `summary_only` files (stats, not full content)
4. **Request:** Use `on_request` files only when needed for specific tasks

### During Work
- If you need full lug details → request WAI-Lugs.jsonl
- If you need protocol guidance → request WAI-Guide.md or commands/*.md
- If you need version info → request WAI-VERSION-GUIDE.md
- If you need historical context → request reference/auto/* files

### Token Awareness
- Before loading additional files, check token budget remaining
- Prioritize `on_request` files over `never` files
- If context is tight, work with summaries instead of full content

---

## For Humans

This folder exists to **reduce AI context loading overhead**. Instead of loading every file on every session:

1. **Core files** (state, foundation) are always loaded (~13K tokens)
2. **Working files** (lugs, signals) provide summaries (~5K tokens)
3. **Reference files** (this folder) are loaded on-demand (0 tokens until needed)

**Impact:** Faster session starts, more tokens available for actual work, better scalability as project grows.

---

## Maintenance

### Adding New Files
1. Update `WAI-File-Index.json` with load_policy
2. Place in appropriate subfolder:
   - `auto/` for automated snapshots
   - `manual/` for curated docs
   - Root level for AI interaction docs
3. Document in this README if it's a new file type

### Cleaning Up
- `auto/` can be cleaned periodically (keep last 5 sessions)
- `manual/` should be curated (remove outdated docs)
- Root-level files are stable (rarely change)

---

**Token Savings:** 120K+ tokens per session (6.7x efficiency gain)  
**Last Updated:** 2026-03-17  
**Version:** 1.0
