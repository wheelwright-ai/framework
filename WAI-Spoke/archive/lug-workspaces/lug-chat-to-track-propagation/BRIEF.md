# Lug: Propagate Chat-to-Track Command and Skill to All Spokes

**ID:** lug-chat-to-track-propagation
**Type:** lug
**Status:** open
**Priority:** P2
**Created:** 2026-03-16
**Created by:** code-puppy-f16663
**Parent epic:** epic-chat-to-track-v1
**Dogfood pass:** true (round 2 — format and symlink issues fixed)
**Blocked by:** lug-chat-to-track-wakeup-ingest, lug-chat-to-track-historian-compat

## What This Is

Create a teaching file so the Chat-to-Track slash command propagates
to all spokes via the hub teach/learn pipeline.

## What This Is NOT

- Not a change to the teach/learn protocol itself
- Not propagating the historian changes (those travel via hub framework
  symlink automatically)
- Not propagating the skill file `chat-to-track.md` — it lives in
  `framework/skills/` which is already accessible to all spokes via
  the hub framework symlink (same mechanism as `historian.yaml`)
- Not urgent — blocked by the other two lugs in this epic

## Challenge

The `/wai-chat-to-track` command only exists on the framework spoke.
Other spokes have no way to access it. Users working on other projects
can't get the Chat-to-Track prompt copied to their clipboard.

Note: the skill file (`framework/skills/chat-to-track.md`) does NOT
need a teaching — it propagates via the hub framework symlink, same as
all other skills. Only the command needs teaching-based propagation.

## Hypothesis

Create one `.teaching` file for the command, matching the existing
Markdown teaching format. Spokes adopt it on next wakeup pull.

## Perceive

1. Run: `ls teachings/*.teaching | head -5` — list existing teaching
   files to see the format in use.
2. Read one existing `.teaching` file (pick the first from listing)
   to learn the structure. **Note: teaching files use Markdown format
   with YAML-like header metadata — they are NOT JSON or YAML.**
   Look for sections like: `What This Teaching Does`, `Version Check`,
   `Transformation`, `Embedded Lug`, `Post-Completion`.
3. Read `templates/commands/wai.md` and search for `Check teachings:`
   to understand how teachings are discovered and adopted on the spoke
   side (Step 3a).
4. Confirm the command source file exists:
   `ls templates/commands/wai-chat-to-track.md`

## Execute

1. Using the Markdown format from the existing `.teaching` file as a
   template, create `teachings/wai-chat-to-track-command.teaching`
   with these sections:

   **Header metadata:**
   - Type: `Skill` (or match whatever the existing teachings use)
   - Target: `All spokes`
   - Version: `1.0`
   - Created: current date
   - `safe_to_auto_adopt: true`

   **What This Teaching Does:**
   "Installs `WAI-Spoke/commands/wai-chat-to-track.md` — a slash
   command that copies the Chat-to-Track capture prompt to clipboard
   and shows workflow directions for external session capture."

   **Version Check:**
   "If `WAI-Spoke/commands/wai-chat-to-track.md` already exists, move
   this teaching to processed and stop."

   **Transformation:**
   "Copy `templates/commands/wai-chat-to-track.md` verbatim to
   `WAI-Spoke/commands/wai-chat-to-track.md`."

   **Post-Completion:**
   "Move this file to `WAI-Spoke/seed/ingest/processed/`."

2. Do NOT create a teaching for `chat-to-track.md` (the skill file).
   It lives in `framework/skills/` which propagates via the hub
   framework symlink — same mechanism as `historian.yaml`. Creating a
   teaching would produce a drifting copy on each spoke.

3. Do NOT create a teaching for `historian.yaml` changes — same
   symlink reasoning.

## Verify

1. `ls teachings/*chat-to-track*` — returns exactly 1 file
   (`wai-chat-to-track-command.teaching`).
2. `grep "safe_to_auto_adopt" teachings/wai-chat-to-track-command.teaching`
   — returns `true`.
3. Confirm the file follows Markdown teaching format (NOT JSON/YAML):
   - `head -10 teachings/wai-chat-to-track-command.teaching` should
     show a Markdown heading and metadata lines, not JSON braces.
   - Contains all required sections: `What This Teaching Does`,
     `Transformation`, `Post-Completion`.
4. On a test spoke (e.g. `solutions-by-mv`), confirm
   `WAI-Spoke/seed/ingest/processed/` does NOT contain
   `wai-chat-to-track-command.teaching` — wakeup will see it as new.

## Context for Cold Reader

The Chat-to-Track system has two artifacts:

1. **The command** (`templates/commands/wai-chat-to-track.md`) — needs
   a teaching to propagate to spoke `commands/` directories.

2. **The skill** (`framework/skills/chat-to-track.md`) — does NOT need
   a teaching. It's in the hub framework directory, accessible to all
   spokes via the existing symlink mechanism.

The parent epic is `WAI-Spoke/lugs/epic-chat-to-track-v1/BRIEF.md`.
