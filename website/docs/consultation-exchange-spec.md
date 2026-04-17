# Handles Consultation Exchange — Specification

**Spec for:** `implementation-handles-consultation-exchange-v1`
**Status:** defined
**Depends on:** `handles-product-spec.md`

---

## 1. Consultation Eject Packet

### What the Consultation Exchange Is

The Consultation Exchange lets a user send a bounded slice of their session context to an external expert or AI service, receive a response, and restore it back into their session with full provenance. It is structured context handoff — not manual copy/paste, not raw track dumping.

### Eject Packet Schema

```json
{
  "eject_id": "<uuid>",
  "created_at": "ISO-8601",
  "source_session_id": "session-20260323-0806",
  "source_wheel_id": "<pseudonym or identified ID per privacy tier>",
  "slice_type": "full_session | recent_N_turns | bounded_topic",
  "slice_config": {
    "turn_count": 10,
    "topic_anchor": "rate limiting implementation",
    "include_decisions": true,
    "include_open_threads": true,
    "exclude_file_contents": true
  },
  "content": {
    "summary": "Working on distributed rate limiting across API gateway services...",
    "recent_points": [ ... ],
    "decisions": [ ... ],
    "open_threads": [ ... ],
    "context_hash": "<sha256 of content for integrity>"
  },
  "consent": {
    "scope": "this_consultation_only",
    "expires_at": "ISO-8601 or null",
    "permitted_uses": ["direct_response", "aggregated_learning"],
    "prohibits": ["retention_beyond_session", "sharing_with_third_parties"]
  },
  "destination": {
    "type": "handles_network | direct_model | expert_wheel",
    "destination_id": "anthropic/claude-opus-4-6"
  }
}
```

**Slice types:**
- `full_session` — entire current session track (use sparingly — high token cost)
- `recent_N_turns` — last N turns of the session (most common)
- `bounded_topic` — turns matching a topic anchor (semantic filter)

---

## 2. Point and Trail Value Preservation

### The Problem

When context is ejected to an external agent, the original session loses continuity. The exchange must preserve the "trail" — the sequence of decisions and insights that led to the current state — so the return response can be meaningfully reintegrated.

### How Trail Value Is Preserved

**Before eject:** The originating agent writes a `consultation_eject` lug:

```json
{
  "id": "consult-eject-<uuid>",
  "type": "consultation_eject",
  "eject_id": "<uuid>",
  "session_id": "session-20260323-0806",
  "turn_at_eject": 14,
  "topic": "rate limiting implementation",
  "open_threads_at_eject": ["Redis connection failure fallback", "per-endpoint config"],
  "awaiting_return": true,
  "ejected_at": "ISO-8601"
}
```

This lug is the local anchor. The session cannot be closed (without warning) while `awaiting_return: true`.

**Reference precision:** The eject packet includes `source_session_id` and `turn_at_eject` so the returned advice can be pinned to the exact session state it was based on. If the session has advanced by the time the response arrives, the return agent flags the delta.

---

## 3. Return Packet

### Return Packet Schema

```json
{
  "return_id": "<uuid>",
  "eject_id": "<uuid — links back to original eject>",
  "responded_at": "ISO-8601",
  "responder": {
    "type": "model | human_expert | expert_wheel",
    "id": "claude-opus-4-6",
    "provider": "anthropic",
    "version": "4.6"
  },
  "provenance": {
    "input_slice": "recent_10_turns",
    "input_hash": "<sha256 — matches eject content_hash>",
    "response_latency_ms": 4200,
    "tokens_consumed": 12400
  },
  "response": {
    "summary": "The Redis connection failure fallback should use a local in-memory token bucket...",
    "advice": [ ... ],
    "addresses_open_threads": ["Redis connection failure fallback"],
    "new_open_threads": ["token bucket TTL under high load"],
    "confidence": 0.88
  },
  "restoration_prompt": "You were consulting an external expert about rate limiting. They recommended: ...\nResume from turn 14 with this context integrated."
}
```

### Restoration Prompt

The `restoration_prompt` is a pre-formatted context injection string that the originating agent can use to resume the session. It is structured so the next agent can orient without re-reading the full exchange.

---

## 4. Wheelwright Web Service Boundary

### Service Endpoints

```
POST /api/v1/consultation/eject
  → Submits an eject packet; returns eject_id and estimated response time

GET  /api/v1/consultation/{eject_id}/status
  → Polls for response status: pending | in_progress | complete | failed

GET  /api/v1/consultation/{eject_id}/return
  → Retrieves the return packet once complete

DELETE /api/v1/consultation/{eject_id}
  → Cancels a pending consultation and purges the eject packet
```

### Routing

Handles routes eject packets to the appropriate responder:

| Destination type | Routing | Latency |
|---|---|---|
| `handles_network` | Handles selects best available model per task class and budget | Minutes |
| `direct_model` | Routes to specified provider API | Seconds–minutes |
| `expert_wheel` | Queued for another registered Handles member (async) | Hours |

### Automation Tiers

| Tier | Automation level |
|------|----------------|
| Free | Manual — user explicitly initiates each consultation |
| Member | Semi-automated — can configure triggers (e.g. "eject on `open_threads > 5`") |
| Pro | Fully automated — rules-based eject + return + restore without user intervention |

---

## 5. Monetization Surfaces

### Pricing Model

| Service | Free | Member | Pro |
|---------|------|--------|-----|
| Manual consultation ejections | 3/month | 10/month | Unlimited |
| Response destination | `handles_network` only | All types | All types + priority routing |
| Expert wheel access | No | Yes (queue) | Yes (priority) |
| Automated exchange | No | No | Yes |
| Consultation history | 7 days | 30 days | 1 year |

### Credit Equivalence (Spot Value)

When a member uses credits for consultations:
- 1 handles_network consultation ≈ 200 credits
- 1 direct model routing ≈ 100 credits (model API cost passed through at cost)
- Expert wheel response (if offered) ≈ negotiated per expert

Credit pricing is approximate and reviewed quarterly as model API costs change.

### Expert Wheel Program (Future)

Members with strong track records (high-confidence responses, positive return ratings) can register as Expert Wheels and offer consultation responses in exchange for credits or revenue share. This is a future feature — defined here to ensure the architecture supports it.

---

## 6. Trust, Consent, and Privacy Rules

### Consent Model

Consent is **per-eject** — users explicitly choose what to share each time:

```
User initiates eject
  ↓
Handles shows: "You are sharing [N turns] about [topic] with [destination].
                Permitted uses: [direct_response].
                This context will be purged after [24 hours / session end]."
  ↓
User confirms → eject proceeds
User declines → no data leaves the local session
```

There is no blanket consent for consultation exchange. Each eject requires explicit action.

### Export Privacy Rules

1. File contents are excluded by default (`exclude_file_contents: true` in eject config)
2. Lug content is summarized, not exported verbatim, unless explicitly included
3. Personal project paths are stripped before export
4. The destination sees only what the user explicitly includes in `slice_config`

### Retention Rules

| Actor | Retention policy |
|-------|----------------|
| Wheelwright Web | Eject packet deleted on return delivery or after 72 hours (whichever first) |
| Destination model | No retention beyond session (enforced by Handles terms with provider) |
| Expert wheel | May retain for 7 days for quality review; deleted after |
| Originating user | Return packet stored per user's Handles tier (7 days free, 30 days member, 1 year pro) |

### Integrity Verification

Return packets include the `input_hash` from the original eject. The originating agent verifies this matches the `content_hash` in the eject lug — confirming the response is based on exactly the context that was sent.

---

## 7. Implementation Boundaries

### What Is In Scope

- Eject packet creation and transmission to Handles
- Return packet receipt and restoration prompt generation
- Local `consultation_eject` lug lifecycle (eject → awaiting → returned → closed)
- Handles API service endpoints (4 endpoints above)
- Free tier (manual, 3/month)

### What Is Out of Scope (Future)

- Expert Wheel marketplace and revenue sharing
- Automated Pro-tier eject/return/restore pipelines
- Multi-hop consultations (eject → expert A → expert B → return)
- Protected track-restoration plugins (separate spec)

---

## Verification Checklist

- [ ] Eject is not manual copy/paste — it is a structured, consent-gated packet ✓
- [ ] Return packet carries full provenance (responder, input hash, latency) ✓
- [ ] Restoration prompt enables cold-start continuation without re-reading exchange ✓
- [ ] Consent is per-eject, not blanket ✓
- [ ] Eject packet is purged after delivery (72-hour hard limit) ✓
- [ ] Local Wheelwright operation does not depend on this service ✓
- [ ] Expert Wheel program is architected for but not implemented in this batch ✓
