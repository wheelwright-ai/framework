# WAI Lug Schema Definition

**Version:** 1.0  
**Status:** Active  
**Schema File:** `reference/schemas/lugs-schema.json`

## Overview

A **Lug** is the fundamental unit of work in Wheelwright AI. It represents a task, epic, bug, or feature request. Lugs are designed to be "AI-native"—structured for autonomous agents to read, reason about, and execute.

## Data Formats

### 1. Logical Format (The API)
This is the format agents interact with (via `wai ready --json` or `Lug.to_dict()`). It uses descriptive, human-readable keys.

**Example:**
```json
{
  "id": "a1b2c3d4",
  "title": "Implement Login",
  "type": "feature",
  "status": "open",
  "priority": "high",
  "value": 8,
  "deps": ["e5f6g7h8"],
  "created_at": "2026-01-20T10:00:00.000000"
}
```

### 2. Storage Format (The Disk)
To optimize storage and parsing speed, Lugs are stored in `WAI-Spoke/lugs.jsonl` using minified keys. Agents typically do not need to parse this directly; they should use the CLI or Python API.

| Logical Key | Storage Key | Verified |
|:---|:---|:---|
| `id` | `i` | ✅ |
| `title` | `t` | ✅ |
| `type` | `ty` | ✅ |
| `status` | `s` | ✅ |
| `created_at` | `ca` | ✅ |
| `updated_at` | `ua` | ✅ |
| `priority` | `p` | ✅ |
| `impact` | `im` | ✅ |
| `value` | `v` | ✅ |
| `deps` | `d` | ✅ |
| `extras` | `ex` | ✅ |

## Field Definitions

### Core Fields
- **id** (`string`): Unique SHA-256 segment or hierarchical ID.
- **title** (`string`): Concise summary of the work.
- **type** (`enum`):
  - `epic`: Large initiative.
  - `feature`: Distinct user-facing functionality.
  - `task`: Sub-unit of work.
  - `bug`: Defect to fix.
  - `chore`: Maintenance work.
- **status** (`enum`): `open`, `in_progress`, `closed`.
- **priority** (`enum`): `critical`, `high`, `medium`, `low`.

### Planning Fields
- **value** (`int`, 1-10): Estimated ROI. Helps agents prioritize.
- **impact** (`enum`): `small`, `medium`, `large`. Risk/Scope assessment.
- **deps** (`list[string]`): IDs of *blocking* Lugs. A Lug is not "ready" until all `deps` are `closed`.

## Validation Rules
1. **Dependency Cycle**: A Lug cannot depend on itself or its descendants (no loops).
2. **Readiness**: A Lug is only returned by `wai ready` if `status == open` AND all `deps` are `closed`.
3. **Immutability**: `id` and `created_at` should never change.
