# Lug: Wakeup Ingest — Detect and Absorb WAI_Track-*.jsonl Files

**ID:** lug-chat-to-track-wakeup-ingest
**Type:** lug
**Status:** open
**Priority:** P1
**Created:** 2026-03-16
**Created by:** code-puppy-f16663
**Parent epic:** epic-chat-to-track-v1
**Dogfood pass:** true

## What This Is

Extend the wakeup protocol (Step 6b) to detect and absorb external
session tracks captured via the Chat-to-Track prompt. These files use
the naming pattern `WAI_Track-*.jsonl` and contain event-based telemetry
(not turn-based points).

## What This Is NOT

- Not a change to the existing `.track.jsonl` bootstrap ingest (that stays)
- Not a modification to the historian (that's a separate lug)
- Not a new step — this extends the existing Step 6b

## Challenge

Wakeup Step 6b currently detects only `.track.jsonl` files in
`WAI-Spoke/seed/ingest/`. External tracks from the Chat-to-Track prompt
use `WAI_Track-YYYYMMDD-HHMM-Provider-Model.jsonl` naming. They are
invisible to the wakeup protocol.

## Hypothesis

Add a second detection block in Step 6b specifically for
`WAI_Track-*.jsonl` files, with validation of the event-based format
before absorption.

## Perceive

1. Open `templates/commands/wai.md` and search for the text:
   `Check \`WAI-Spoke/seed/ingest/\` for \`.track.jsonl\` files`
   This is the Step 6b track ingest block.
2. Open `.claude/commands/wai.md` and `WAI-Spoke/commands/wai.md`.
   Diff all three against `templates/commands/wai.md` around the
   Step 6b block to see if local overrides exist.
3. Run: `ls -d WAI-Spoke/seed/ingest/processed/` — confirm directory
   exists.

## Execute

1. In `templates/commands/wai.md`, locate the paragraph starting with:
   `Check \`WAI-Spoke/seed/ingest/\` for \`.track.jsonl\` files`

2. After that paragraph, add a new paragraph for external tracks:

   ```markdown
   Check `WAI-Spoke/seed/ingest/` for `WAI_Track-*.jsonl` files — external
   session tracks captured via the Chat-to-Track prompt. If present:
   - Output: "📡 N external track file(s) awaiting ingest"
   - For each file:
     1. Read the first line. Validate it is valid JSON containing
        `"event":"session_start"` with `provider` and `model` fields.
     2. If valid: copy file to `WAI-Spoke/sessions/` preserving the
        original filename. Move the original to `seed/ingest/processed/`.
        Output:
        ```
        📡 Absorbed: {filename}
           Source: {provider} / {model}
           Events: {total line count}
           Decisions: {count of lines containing "decision_made"}
           Concepts: {count of lines containing "concept_update"}
        ```
     3. If invalid (missing session_start, missing provider/model, or
        malformed JSON on first line): output:
        ```
        ⚠️ Could not absorb: {filename}
           Issue: {specific problem}
           File left in seed/ingest/ — fix and retry.
        ```
        Do not move the file.
   ```

3. Run: `cp templates/commands/wai.md .claude/commands/wai.md`

4. **Handle `WAI-Spoke/commands/wai.md` carefully.** This file may be
   divergent from the template (different step numbering, spoke-specific
   content like Auto-Implementation Queue). Do NOT blindly `cp`.
   Instead:
   - Run `diff templates/commands/wai.md WAI-Spoke/commands/wai.md`
   - If the files are identical (no diff output): safe to `cp`.
   - If the files differ: locate the equivalent Step 6b section in
     `WAI-Spoke/commands/wai.md` (search for `.track.jsonl` or the
     nearest ingest-related section) and manually insert the same
     `WAI_Track-*.jsonl` detection block there. Preserve all other
     spoke-specific content.
   - If `WAI-Spoke/commands/wai.md` has NO track ingest section at all:
     add the `WAI_Track-*.jsonl` block at the end of the ingest-related
     steps, with a markdown comment noting it was ported from the
     template.

## Verify

1. `grep "WAI_Track" templates/commands/wai.md` — returns at least one
   line containing the new detection text.
2. `grep ".track.jsonl" templates/commands/wai.md` — still returns the
   original bootstrap ingest text (no regression).
3. `diff templates/commands/wai.md .claude/commands/wai.md` — returns
   no output (files are identical after copy).
5. `grep "WAI_Track" WAI-Spoke/commands/wai.md` — returns at least one
   line (spoke version also has the new detection block).
4. Create a test file to confirm pattern matching:
   `echo '{"event":"session_start","ts":"2026-03-16T00:00:00Z","session_id":"test","provider":"Test","model":"test-1"}' > WAI-Spoke/seed/ingest/WAI_Track-20260316-0000-Test-test1.jsonl`
   Manually verify the wakeup instructions would match it.
   Clean up: `rm WAI-Spoke/seed/ingest/WAI_Track-20260316-0000-Test-test1.jsonl`

## Context for Cold Reader

The Chat-to-Track system lets users paste a prompt into external AI
chats (ChatGPT, Gemini, etc.) to record structured event telemetry.
On "closeout chat", the AI exports a JSONL file. The user saves it to
`WAI-Spoke/seed/ingest/`. This lug makes wakeup aware of those files.

The prompt lives at `framework/skills/chat-to-track.md`.
The slash command is `templates/commands/wai-chat-to-track.md`.
The parent epic is `WAI-Spoke/lugs/epic-chat-to-track-v1/BRIEF.md`.
