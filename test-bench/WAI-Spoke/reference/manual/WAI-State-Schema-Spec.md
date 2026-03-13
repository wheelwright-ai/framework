# WAI State Schema Specification

**Version:** 1.0.0
**Date:** 2026-03-13
**Status:** Foundation Spec

---

## Philosophy

`WAI-State.json` is the source of truth for a node's persistent state. Unlike Lugs (which are actionable events), WAI-State captures metadata, project identity, and session continuity details.

## Schema Structure

### `wheel` (Project Metadata)
Captures project-level identifier and status.

```json
{
  "name": "Project Name",
  "version": "2.0.16",
  "node_type": "spoke | hub",
  "hub_id": "Target Hub ID",
  "hub_path": "Path to hub",
  "status": "active | retired"
}
```

### `_session_state` (Session Continuity)
Critical for cross-session context resumption.

```json
{
  "last_session_id": "session-YYYYMMDD-HHMM",
  "last_modified_by": "Agent Name",
  "last_modified_at": "ISO-8601",
  "last_closeout": "ISO-8601",
  "session_count": 0,
  "track_path": "WAI-Spoke/session-YYYYMMDD-HHMM/",  // Path to current/last session track
  "protocol_completed": true,
  "next_session_recommendation": "Summary for next agent"
}
```

### `_project_foundation` (Strategic Vision)
Core project identity and boundaries.

```json
{
  "identity": {
    "name": "Full Project Name",
    "one_liner": "Description",
    "success_looks_like": "Vision"
  },
  "boundaries": {
    "in_scope": [],
    "out_of_scope": [],
    "constraints": []
  }
}
```

---

## Fields in Focus: `track_path`

The `track_path` field links the state to the **Historian's** record (session tracks). This allows for deep context recovery even when `WAI-State.json` is partially lost or needs reconciliation.

- **Storage:** Relative path within `WAI-Spoke/`
- **Updated at:** Session start (`/wai`) and Closeout
- **Used by:** Wakeup protocol (for recovery/resume) and Historian reviews
