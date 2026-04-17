# Session Ledger

**WAI-Ledger.jsonl** is an append-only log of commitments that survives context loss.

## Origin Story

During WAI v2 migration (2026-02-12), token exhaustion caused context loss mid-migration. The executing agent:

- Reconstructed intent from partial memory
- Renamed PEV fields (perceive/execute/verify → perspective/evidence/verdict)
- Skipped 2 phases (8-9 of 9)
- Declared migration complete

**There was no mechanism to detect the drift** because commitments lived only in conversation context, not in files.

The session ledger fixes this.

## How It Works

### Lifecycle

```
request (conductor) → agreement (agent) → delivery (agent) → verification (conductor)
```

### Entry Types

| Type | Who | Meaning |
|------|-----|---------|
| `request` | conductor | "I want this done" |
| `agreement` | agent | "I will do this, here's how" |
| `clarification` | either | "Do you mean X or Y?" / "I mean X" |
| `amendment` | either | "Actually, let's change the approach" |
| `delivery` | agent | "This is done" — links to commit hash |
| `verification` | conductor | "Confirmed" or "Doesn't match agreement" |
| `rejection` | conductor | "Doesn't fulfill the agreement, because..." |

### Schema

```jsonl
{"id":"led-2026-02-12-001","timestamp":"2026-02-12T14:00:00Z","session_id":"session-001","type":"request","content":"Migrate Lug schema to v2 with PEV fields","source":"conductor","status":"open"}
{"id":"led-2026-02-12-002","timestamp":"2026-02-12T14:05:00Z","session_id":"session-001","type":"agreement","content":"Will add perceive/execute/verify as optional fields","source":"agent","references":"led-2026-02-12-001","status":"open"}
{"id":"led-2026-02-12-003","timestamp":"2026-02-12T15:00:00Z","session_id":"session-001","type":"delivery","content":"350 Lugs upgraded, PEV fields added","source":"agent","references":"led-2026-02-12-001","commit":"73112e9","status":"fulfilled"}
```

## Integration Points

### On Session Start (Wakeup)

1. Read WAI-Ledger.jsonl
2. Filter for status: "open"
3. Surface in composite briefing: "Open commitments from prior sessions"

### On Session Close (Closeout)

1. session-observer reconciles open ledger entries
2. For each: was it delivered? Create delivery entry with commit hash
3. Surface unfulfilled commitments: "These requests are still open"

### On Context Loss / Resume

1. New agent reads ledger
2. Compares open agreements against actual state of codebase
3. Identifies drift: "Agreement says X, but codebase has Y"
4. Creates diagnosis Lug for each discrepancy

## Use Cases

### Prevents Premature Completion

**Scenario:** Conductor asks for 9 phases, agent delivers 7 and says "complete"

**Ledger:** Has 9 request entries. Only 7 have delivery entries.

**Closeout:** Flags 2 open commitments remain. Catches premature completion.

### Detects Spec Drift

**Scenario:** Agreement says "perceive/execute/verify", code has "perspective/evidence/verdict"

**On Resume:** Ledger shows the agreement. New agent reads code, detects mismatch, creates diagnosis Lug.

### Survives Context Loss

**Scenario:** Token exhaustion mid-session

**Recovery:** Commitments are file-permanent. New agent reads ledger, sees what was agreed to, verifies against codebase.

## Integrity Rules

Per WAI-Integrity.md:

- **Append-only:** Never delete ledger entries
- **Status progression:** open → fulfilled / amended / rejected
- **Amendments create new entries:** Don't modify old entries
- **Reconciliation is mandatory:** Part of closeout ceremony

## For Agents

- Write ledger entries as you make commitments
- Use the ledger to track multi-session work
- On resume, read the ledger FIRST to understand prior commitments
- Flag unfulfilled commitments at session close

The ledger is the parity check. Use it.
