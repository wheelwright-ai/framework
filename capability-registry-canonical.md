# Wheelwright Canonical Capability Registry

**Version:** 1.0.0-draft  
**Date:** 2026-03-19  
**Epic:** epic-session15-fleet-evolution  
**Purpose:** Define canonical file shapes and behaviors for the core Wheelwright object model

## 1. Registry Overview

This registry defines the canonical capabilities required for Wheelwright framework implementation. Each capability specifies:

- **File schemas** and required fields
- **Behavioral contracts** (what each model does)
- **Interaction patterns** between models
- **Migration compatibility** requirements

The registry ensures "maintain expectations, not file locations" — capabilities are canonical, paths are implementation details.

## 2. Design Principles (from Goal-State Doc)

1. **Simplicity over bureaucracy** — Create continuity and leverage, not ceremony
2. **Maintain expectations, not file locations** — Preserve behavioral contracts across framework evolution
3. **PEV is a relation, not a field** — Perceive/Execute/Verify represented as linked lugs
4. **Signals are not mail** — Signals are staged intelligence, not inbox commands
5. **Historian is advisory in planning** — May create candidate lugs but requires user review
6. **Core object count stays small** — Use explicit relations over new entity types
7. **Hub pull beats hub flood** — Spokes choose what they absorb

## 3. Core Capability Definitions

### 3.1 Canonical State Model (WAI-State.json)

**Capability ID:** `wai-state-canonical`  
**Contract Version:** `2.0`  
**Family:** `spoke-core`

**Purpose:** Primary spoke identity, environment, and operational state

**Required Schema Fields:**
```json
{
  "wheelwright": {
    "version": "string",
    "structure_version": "string", 
    "framework_path": "string|null",
    "hub_path": "string|null"
  },
  "_project_foundation": {
    "completed": "boolean",
    "identity": {
      "type": "string|null",
      "name": "string|null", 
      "one_liner": "string|null"
    },
    "boundaries": {
      "in_scope": "array",
      "out_of_scope": "array"
    }
  },
  "_session_state": {
    "last_session_id": "string|null",
    "last_modified_by": "string|null",
    "last_modified_at": "ISO-8601|null",
    "session_count": "number",
    "protocol_completed": "boolean"
  },
  "wheel": {
    "name": "string|null",
    "hub_path": "string|null",
    "spoke_id": "string" // 12-char hex identifier
  }
}
```

**Behavioral Contracts:**
- MUST be the primary source of truth for spoke identity
- MUST track session state for continuity
- MUST maintain hub/framework path discovery
- MUST support foundation completion workflow
- MUST provide environment detection metadata

**Migration Strategy:** Dual-read legacy `BRIEF.md`/`WAI-Manifest.yaml` during transition, single-write to WAI-State.json

**Verification Rules:**
- File MUST parse as valid JSON
- Required fields MUST be present
- `spoke_id` MUST be unique across hub registry
- Session state MUST increment on significant changes

---

### 3.2 Canonical Track Model (Session Tracking)

**Capability ID:** `wai-track-canonical`  
**Contract Version:** `2.0`  
**Family:** `session-tracking`

**Purpose:** High-fidelity session telemetry for cross-tool continuity

**File Path Pattern:** `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`

**Required Schema Fields (per turn):**
```json
{
  "turn": "number",
  "ts": "ISO-8601", 
  "focus": "string",
  "action": "string",
  "thinking": "string", // 5-8 sentences of complete architectural rationale
  "activity": "array", // Concrete actions taken
  "decisions": "array", // Architectural choices made
  "insights": "array", // New understandings
  "open": "array", // Unresolved threads
  "phase": "string",
  "evolution": "string" // How understanding evolved this turn
}
```

**Session Metadata (turn 1):**
```json
{
  "session_metadata": {
    "session_id": "session-YYYYMMDD-HHMM",
    "provider": "string", // claude-code, gemini-cli, etc
    "model": "string", // claude-3-5-sonnet, gemini-1.5-pro, etc
    "predecessor": "session-YYYYMMDD-HHMM|null", // Enables track chaining
    "environment": {
      "tool": "string",
      "machine": "string", 
      "os": "string"
    }
  }
}
```

**Behavioral Contracts:**
- MUST capture every turn with mandatory high-fidelity thinking
- MUST enable cold-start continuity for any agent
- MUST support cross-tool session chaining via predecessor links
- MUST preserve complete architectural rationale, not summaries
- MUST record concrete activity, not just outcomes

**Migration Strategy:** 
- Canonical path: `sessions/session-YYYYMMDD-HHMM/track.jsonl`
- Legacy read: flat `sessions/track_*.jsonl` format
- New writes always use canonical structure

**Verification Rules:**
- Each turn MUST have all required fields
- `ts` MUST be valid ISO-8601
- `turn` MUST be sequential starting at 1
- `thinking` MUST be substantive (5+ sentences)
- Session directory MUST exist before track creation

---

### 3.3 Signal Bulletin Model (Hub Distribution)

**Capability ID:** `wai-signals-canonical`  
**Contract Version:** `2.0`  
**Family:** `hub-distribution`

**Purpose:** Stage high-impact intelligence for selective pull by spokes

**File Path Pattern:** 
- Incoming: `WAI-Hub/signals/incoming/{lug_id}.json`
- Processed: `WAI-Hub/signals/processed/{lug_id}.json`

**Signal Classification Rule:**
- Signals are lugs with `impact >= 8`
- Qualifying lugs are copied to hub bulletin during closeout
- Other spokes inspect `incoming/` during wakeup

**Required Schema Fields:**
```json
{
  "lug_id": "string", // Original lug identifier
  "source_spoke": "string", // Originating spoke_id
  "timestamp": "ISO-8601",
  "impact": "number", // >= 8
  "title": "string",
  "description": "string",
  "type": "string", // lug type: epic, work, decision, finding, etc
  "tags": "array",
  "evidence": "array|null", // Supporting evidence
  "applies_to": "array", // Which spokes/projects this affects
  "signal_metadata": {
    "promoted_at": "ISO-8601",
    "promoted_by": "string",
    "category": "string" // pattern, practice, warning, etc
  }
}
```

**Processed Signal Extensions:**
```json
{
  "processing_metadata": {
    "absorbed_at": "ISO-8601",
    "absorbed_by": "string", // hub agent or framework process
    "generated_teaching_id": "string|null",
    "resolution": "string" // teaching_created, no_teaching_needed, etc
  }
}
```

**Behavioral Contracts:**
- Signals MUST be derived from lugs, not separate entities
- Hub MUST stage signals for pull, not push broadcast
- Processed signals MUST retain source attribution
- Framework MAY generate teachings from processed signals
- Spokes MUST be able to selectively ignore signals

**Migration Strategy:** Deprecate separate `WAI-Signals.jsonl`, migrate content to lug model

**Verification Rules:**
- Signal MUST have corresponding source lug
- `impact` MUST be >= 8
- `source_spoke` MUST exist in hub registry
- Processing MUST be idempotent

---

### 3.4 Closeout Receipt Model (Session Preservation)

**Capability ID:** `wai-closeout-canonical`  
**Contract Version:** `2.0`  
**Family:** `session-management`

**Purpose:** Session preservation ceremony outputs and verification

**File Path Pattern:** `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/closeout-receipt.json`

**Required Schema Fields:**
```json
{
  "session_id": "string",
  "closeout_timestamp": "ISO-8601",
  "closeout_agent": "string",
  "session_summary": {
    "total_turns": "number",
    "duration_seconds": "number",
    "focus_areas": "array",
    "completion_status": "string" // completed, interrupted, deferred
  },
  "state_updates": {
    "lugs_created": "number",
    "lugs_updated": "number", 
    "lugs_closed": "number",
    "signals_promoted": "number",
    "session_state_updated": "boolean",
    "files_modified": "array"
  },
  "continuity_artifacts": {
    "session_lug_created": "string|null", // lug_id for session summary
    "next_actions": "array",
    "open_threads": "array",
    "key_decisions": "array"
  },
  "quality_verification": {
    "track_complete": "boolean",
    "state_consistent": "boolean", 
    "git_clean": "boolean",
    "errors": "array"
  },
  "outbound_mail": {
    "signals_published": "array", // Signal IDs sent to hub
    "teachings_generated": "array",
    "cross_spoke_mail": "array"
  }
}
```

**Behavioral Contracts:**
- MUST finalize session track before creating receipt
- MUST update spoke state consistently
- MUST reconcile in-progress work into durable records
- MUST surface qualifying signals for hub promotion
- MUST verify session integrity before completion

**Migration Strategy:** New capability, no legacy equivalent

**Verification Rules:**
- Session MUST have corresponding track file
- State updates MUST be verifiable against actual files
- Quality verification MUST pass before receipt creation
- Outbound mail MUST be deliverable

---

### 3.5 Migration Receipt Model (Migration Tracking)

**Capability ID:** `wai-migration-canonical`  
**Contract Version:** `2.0`  
**Family:** `capability-migration`

**Purpose:** Track and verify capability adoption and migration state

**File Path Pattern:** `WAI-Spoke/migrations/migration-{capability_id}-{timestamp}.json`

**Required Schema Fields:**
```json
{
  "migration_id": "string",
  "capability_id": "string",
  "spoke_id": "string",
  "migration_timestamp": "ISO-8601",
  "migration_agent": "string",
  "version_transition": {
    "from_version": "string|null",
    "to_version": "string",
    "contract_change": "boolean"
  },
  "migration_operations": {
    "files_created": "array",
    "files_updated": "array", 
    "files_removed": "array",
    "files_migrated": "array" // old_path -> new_path mappings
  },
  "compatibility_state": {
    "legacy_preserved": "boolean",
    "dual_read_required": "boolean",
    "rollback_supported": "boolean",
    "verification_complete": "boolean"
  },
  "verification_results": {
    "schema_valid": "boolean",
    "behavior_verified": "boolean",
    "integration_tested": "boolean",
    "errors": "array",
    "warnings": "array"
  },
  "rollback_metadata": {
    "rollback_supported": "boolean",
    "preserved_files": "array",
    "rollback_commands": "array"
  }
}
```

**Behavioral Contracts:**
- MUST be idempotent — running migration twice is safe
- MUST preserve rollback capability with verification
- MUST verify capability adoption completely
- MUST track exact file operations for audit trail
- MUST support hub visibility into migration state

**Migration Strategy:** New capability for managing all other migrations

**Verification Rules:**
- Migration MUST be idempotent when re-executed
- Rollback MUST restore exact prior state
- Verification MUST pass before marking complete
- Hub MUST be able to query migration state across spokes

---

## 4. Capability Interaction Patterns

### 4.1 Wakeup Protocol Interactions

```
WAI-State.json -> provides spoke identity and session state
Track files -> detect predecessor sessions for continuity
Hub Signals -> inspect bulletin for relevant intelligence
Migration receipts -> verify capability adoption is current
```

### 4.2 Closeout Protocol Interactions

```
Track files -> finalize session telemetry
WAI-State.json -> update session state and counters
Closeout receipt -> create preservation artifact
Hub signals -> promote qualifying lugs to bulletin
Migration receipts -> trigger any pending migrations
```

### 4.3 PEV Chain Pattern

PEV is represented as linked lugs, not embedded fields:

```json
// Perceive lug
{
  "id": "perceive-abc123",
  "type": "finding",
  "title": "Problem analysis",
  "pev_role": "perceive",
  "pev_chain": "chain-def456",
  "linked_lugs": ["execute-ghi789"]
}

// Execute lug  
{
  "id": "execute-ghi789", 
  "type": "work",
  "title": "Implementation approach",
  "pev_role": "execute", 
  "pev_chain": "chain-def456",
  "linked_lugs": ["perceive-abc123", "verify-jkl012"]
}

// Verify lug
{
  "id": "verify-jkl012",
  "type": "test", 
  "title": "Verification criteria",
  "pev_role": "verify",
  "pev_chain": "chain-def456", 
  "linked_lugs": ["execute-ghi789"]
}
```

### 4.4 Hub-Spoke Signal Flow

```
Spoke Lug (impact >= 8) -> Hub Signals/incoming/ -> Framework Review -> 
Hub Signals/processed/ -> Generated Teaching -> Spoke Adoption
```

## 5. Migration Compatibility Matrix

| Legacy Model | Canonical Model | Migration Strategy | Dual-Read Period |
|-------------|-----------------|-------------------|------------------|
| `BRIEF.md` | `WAI-State.json` | Extract identity/boundaries | Until v3.0 |
| `WAI-Manifest.yaml` | `WAI-State.json` | Merge wheel metadata | Until v3.0 |
| `WAI-Signals.jsonl` | Lug-based signals | Migrate to lugs w/impact>=8 | Complete |
| `track_*.jsonl` | `session-*/track.jsonl` | Directory structure | Until v3.0 |
| `teach`/`learn` commands | `closeout`/`wakeup` | Command mapping | Until v3.0 |

## 6. Canonical Lug Model Extensions

The goal-state design specifies a small set of durable lug types:

### 6.1 Core Types
- `epic` — Large coordinated work
- `work` — Executable tasks (kind: task/bug/feature)  
- `decision` — Architectural choices
- `finding` — Discoveries and insights
- `test` — Verification specifications
- `session-summary` — Session preservation records

### 6.2 Required Lug Schema
```json
{
  "id": "string", // 12-char hex
  "type": "string", // core type above
  "title": "string",
  "description": "string", 
  "status": "string", // lifecycle state
  "impact": "number", // 1-10, signals if >= 8
  "created_by": "string",
  "created_at": "ISO-8601",
  "tags": "array",
  "priority": "string",
  "scope": "string|null", // framework, spoke, project
  "category": "string|null" // for work type classification
}
```

### 6.3 Workflow States
- **Intake:** `new > draft > qualified > approved > planned`
- **Execution:** `indev > implemented > intest > verified`
- **Epic:** `active > verifying > verified` 
- **Decision/Finding:** `new > draft > qualified > approved > published`

## 7. Implementation Requirements

### 7.1 Framework Registry Location
**Canonical Path:** `framework/capability-registry.json`

**Registry Schema:**
```json
{
  "registry_version": "1.0.0",
  "last_updated": "ISO-8601",
  "capabilities": {
    "capability_id": {
      "id": "string",
      "family": "string",
      "contract_version": "string",
      "description": "string", 
      "owned_paths": "array",
      "depends_on": "array",
      "replaces": "array|null",
      "migration_strategy": "string",
      "verification_rules": "array"
    }
  }
}
```

### 7.2 Spoke Adoption Tracking
**Canonical Path:** `WAI-Spoke/capability-adoption.json`

**Adoption Schema:**
```json
{
  "spoke_id": "string",
  "last_updated": "ISO-8601", 
  "adopted_capabilities": {
    "capability_id": {
      "version": "string",
      "adopted_at": "ISO-8601",
      "verified_at": "ISO-8601",
      "migration_receipt": "string" // receipt file path
    }
  },
  "pending_migrations": "array"
}
```

## 8. Verification and Testing

### 8.1 Capability Verification Rules

Each capability MUST provide:
1. **Schema validation** — JSON Schema for all file formats
2. **Behavioral tests** — Verify contracts work as specified  
3. **Integration tests** — Verify interactions with other capabilities
4. **Migration tests** — Verify safe upgrade/rollback
5. **Performance tests** — Verify acceptable resource usage

### 8.2 Quality Gates

Before capability promotion:
- All tests MUST pass
- Schema MUST validate against reference implementations
- Documentation MUST be complete and accurate
- Migration path MUST be verified safe and idempotent
- Rollback MUST restore exact previous state

## 9. Evolution and Versioning

### 9.1 Contract Versioning
- **Major version** — Breaking behavioral changes
- **Minor version** — Backward-compatible additions
- **Patch version** — Bug fixes, documentation updates

### 9.2 Capability Evolution Process
1. **Proposal** — New capability or change request
2. **Review** — Community and maintainer evaluation
3. **Implementation** — Reference implementation with tests
4. **Migration** — Safe upgrade path with verification
5. **Release** — Version bump and documentation update

## 10. Current Status Assessment

### 10.1 Implemented Capabilities
- ✅ `wai-state-canonical` — WAI-State.json schema stable
- ✅ `wai-track-canonical` — Track format stable, directory migration in progress
- ⚠️ `wai-signals-canonical` — Lug-based signals working, hub bulletin needs implementation
- ❌ `wai-closeout-canonical` — Schema drafted, implementation needed
- ❌ `wai-migration-canonical` — Schema drafted, tooling needed

### 10.2 Implementation Dependencies
1. Hub bulletin board implementation (`WAI-Hub/signals/`)
2. Migration tooling for capability tracking
3. Closeout ceremony formalization
4. Registry file creation and maintenance tooling

## 11. Next Steps

1. **Validate Registry Schema** — Review with framework maintainers
2. **Implement Hub Bulletin** — Create signal staging directory structure  
3. **Build Migration Tooling** — Idempotent capability adoption tools
4. **Formalize Closeout** — Session preservation ceremony implementation
5. **Create Reference Implementation** — Complete example of all capabilities
6. **Migration Planning** — Spoke rollout and compatibility timeline

---

**Document Status:** Draft for review and refinement  
**Next Review:** After implementation team feedback  
**Approval Required:** Framework maintainers and epic-session15-fleet-evolution lead

This registry provides the foundation for implementing consistent, interoperable Wheelwright capabilities while preserving the design principles and migration compatibility requirements specified in the goal-state document.