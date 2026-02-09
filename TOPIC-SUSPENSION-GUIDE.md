# Topic Suspension System - Quick Guide

## Purpose

Pause work on one topic and resume later without losing context. Like browser tabs for AI sessions.

---

## Usage

### Suspend Current Topic

```bash
# Skill command (future):
wai suspend-topic "CLI Navigation Issue"

# Manual (current):
# 1. Create topic lug in ../hub/topics/
# 2. Fill in work_state, blocking_issues, next_actions
# 3. Commit and closeout session
```

### Resume Topic

```bash
# Skill command (future):
wai resume-topic TOPIC-20260209-CLI001

# Manual (current):
# 1. Read topic lug from ../hub/topics/
# 2. Read files_to_read
# 3. Run commands_to_run to verify state
# 4. Continue from next_actions
```

---

## Topic Lug Structure

```json
{
  "lug_type": "topic-suspension",
  "topic_id": "TOPIC-YYYYMMDD-HASH6",
  "topic_title": "Human readable title",
  "suspended_at": "ISO 8601 timestamp",
  "work_state": {
    "status": "blocked|in-progress|ready-for-review",
    "summary": "What was done",
    "blocking_issues": [...],
    "deliverables": [...],
    "next_actions": [...]
  },
  "resume_instructions": {
    "files_to_read": [...],
    "context_summary": "Quick brief",
    "commands_to_run": [...]
  }
}
```

---

## Current Suspended Topics

| Topic ID | Title | Status | Priority |
|----------|-------|--------|----------|
| TOPIC-20260209-CLI001 | CLI Navigation Issue | blocked | critical |

---

## Workflow

1. **Recognize blocking issue** - Work cannot proceed
2. **Create topic lug** - Capture full state
3. **Commit changes** - Save deliverables
4. **Closeout session** - Proper git push
5. **Switch context** - Start new topic
6. **Resume later** - Read lug, restore context, continue

---

## Benefits

✅ **No context loss** - Full state captured  
✅ **Clean switches** - Proper closeout between topics  
✅ **Parallel work** - Multiple topics in flight  
✅ **Better planning** - next_actions guide resumption  
✅ **Blocking visibility** - Issues documented clearly

---

## Future Skills

```bash
# Suspend current work
wai suspend-topic "Description" [--status blocked|in-progress]

# List suspended topics
wai list-topics [--status blocked] [--priority critical]

# Resume topic
wai resume-topic <topic-id>

# Close topic
wai close-topic <topic-id> --reason "completed|abandoned|merged"
```

---

## Location

**Topic lugs:** `../hub/topics/`  
**Schema:** `templates/lugs/topic-suspension.lug.schema.json`  
**Guide:** `TOPIC-SUSPENSION-GUIDE.md`

---

## Example: Today's Suspension

**Topic:** CLI Navigation Issue  
**ID:** TOPIC-20260209-CLI001  
**Status:** blocked (critical)  
**Context:** Machine optimization complete, CLI broken, user needs to teach spokes  
**Next:** Fix CLI navigation or provide alternative teach command

**Resume with:**
```bash
# Read the lug
cat ../hub/topics/TOPIC-20260209-CLI001.lug.json

# Read context files
cat wai/cli/main.py wai/cli/menu.py wai/cli/input.py

# Test CLI
wai

# Continue from next_actions
```

---

**Created:** 2026-02-09  
**Schema Version:** 1.0
