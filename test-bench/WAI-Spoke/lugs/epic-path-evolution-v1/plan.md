# Execution Plan: Path Evolution

**Agent:** Haiku (execution model)
**Supervision:** User reviews before commit

## Prerequisites

Read these files first to understand current state:
- `framework/skills/track-encapsulation.yaml` — current point capture skill
- `templates/commands/wai.md` — wakeup protocol (references track)
- `templates/commands/wai-closeout.md` — closeout protocol (references track)
- `WAI-Spoke/WAI-State.json` — session state (has `track_path`)
- `WAI-Spoke/session-20260313-0400/track.jsonl` — existing session data

## Phase 1: Track → Path Rename

All changes are mechanical renames. No logic changes.

### 1.1 Rename skill file
- `framework/skills/track-encapsulation.yaml` → `framework/skills/wai-path.yaml`
- Inside the file: replace all references to "track" with "path" where they refer to the session capture object
- Keep the point schema intact — only naming changes

### 1.2 Update wakeup protocol
- File: `templates/commands/wai.md`
- Step 5a title: "Read Session Track" → "Read Session Path"
- All references: `track.jsonl` → `path.jsonl`
- `track_path` → `path_dir` in WAI-State.json references
- Step 9 title: "Initialize Session Track" → "Initialize Session Path"
- References to "track" in context of session capture → "path"

### 1.3 Update closeout protocol
- File: `templates/commands/wai-closeout.md`
- All references: `track.jsonl` → `path.jsonl`, "track" → "path" for session capture context
- `track_path` → `path_dir`

### 1.4 Update WAI-State.json
- `_session_state.track_path` → `_session_state.path_dir`

### 1.5 Rename existing session data
- `WAI-Spoke/session-20260313-0400/track.jsonl` → `WAI-Spoke/session-20260313-0400/path.jsonl`

### 1.6 Update historian skill
- File: `framework/skills/historian.yaml`
- References to `track.jsonl` → `path.jsonl`

### 1.7 Update spoke CLAUDE.md template
- If `templates/spoke/CLAUDE.md` or similar exists, update track → path references

### 1.8 Add trigger field to point schema
- In `framework/skills/wai-path.yaml` (renamed), add `trigger` to the point schema
- Values: `periodic`, `decision`, `milestone`, `manual`
- Default capture cadence: every 3 turns + on-decision

## Phase 2: Folder-Based Lugs

### 2.1 Define the folder-lug convention
- Create `framework/skills/lug-folders.yaml` (or add to existing lug advisor)
- Convention:
  ```
  WAI-Spoke/lugs/{lug-id}/
    BRIEF.md    — metadata, summary, what this lug IS and IS NOT
    {assets}    — .md, .yaml, .jsonl, whatever content the lug carries
  ```
- WAI-Lugs.jsonl continues as registry/index — each entry points to its folder
- HEAD convention: folder at `lugs/{lug-id}/` is always HEAD. Version history in `lugs/{lug-id}/versions/`

### 2.2 Update lug extraction convention
- When extracting lugs from a WAI Path file (lugs in transit):
  - Create folder `lugs/{lug-id}/`
  - Write BRIEF.md with metadata + summary
  - Copy any assets into the folder
  - Append registry entry to WAI-Lugs.jsonl with `folder: "lugs/{lug-id}/"`
- Source path file is never modified

### 2.3 Update lug advisor skill
- File: `templates/commands/wai-lug-advisor.md`
- Add folder-based lug convention alongside existing JSONL guidance
- HEAD is always the folder at top level; versions nest inside

### 2.4 Do NOT migrate existing JSONL-only lugs
- Existing lugs in WAI-Lugs.jsonl that have no folder are fine as-is
- New lugs get folders; old ones get folders when they're next touched
- No mass migration needed

## Phase 3: WAI Path Generator Skill

### 3.1 Create the skill file
- File: `framework/skills/wai-path-generator.yaml`
- Content: the WAI Path Generator prompt from `prompt-v3.md` in this lug
- This is a synthesis skill — used to generate WAI Path exports from session points

### 3.2 Register in available skills
- Add to the skills list in `templates/commands/wai.md` (Step 10)
- Not a user-invocable command yet — it's a prompt template for path generation

## Phase 4: Verify

### 4.1 Check all references
- `grep -r "track\.jsonl" templates/ framework/skills/` should return 0 results
- `grep -r "track_path" templates/ framework/skills/ WAI-Spoke/WAI-State.json` should return 0 results
- Existing session data renamed

### 4.2 Validate lug folder structure
- `epic-path-evolution-v1/` exists with BRIEF.md and assets
- This lug itself is the first example of the pattern

## Notes for Agent

- This is a rename + convention change, not a rewrite
- The point schema is stable — only adding `trigger` field
- Don't change any logic, just naming
- WAI-Lugs.jsonl is additive — existing entries stay, new entries add `folder` field
- Ask user before committing
