# Handles Demand Exchange — Specification

**Spec for:** `implementation-handles-demand-exchange-v1`
**Status:** defined
**Depends on:** `handles-product-spec.md`

---

## 1. Feature-Demand Enrollment and Voting/Request Model

### What the Demand Exchange Is

The Demand Exchange lets the Wheelwright community vote on feature priorities and signal vendor interest — without direct financial transactions in v1. It is a structured preference signal, not a marketplace.

### Enrollment Model

```json
{
  "demand_item_id": "<hash>",
  "type": "feature_request | model_capability | integration | workflow_pattern",
  "title": "Support streaming output in Ozi dispatch",
  "description": "...",
  "submitted_by": "<member_pseudonym>",
  "submitted_at": "ISO-8601",
  "tags": ["ozi", "streaming", "dispatch"],
  "target": "wheelwright | vendor:<provider_id> | open"
}
```

### Voting Model

Members vote with credits or free votes (one free vote per item per account per month):

```json
{
  "vote_type": "upvote | credit_boost | vendor_interest",
  "voter_pseudonym": "<member_pseudonym>",
  "demand_item_id": "<hash>",
  "credits_spent": 0,
  "voted_at": "ISO-8601"
}
```

**Vote weights:**
- Free upvote: 1 point
- Credit boost (50 credits): 5 points (indicates stronger preference)
- Vendor interest signal: displayed separately — not added to community vote total

Vendors signal interest separately to prevent gaming the community vote with commercial pressure.

### Demand Board Surfaces

| Surface | Access tier |
|---------|-------------|
| Public demand board (top 20, delayed 7 days) | Public |
| Full demand board with trending | Member |
| Vendor interest overlay | Pro |
| Custom segment demand analysis | Enterprise |

---

## 2. Credit Economy (within Handles)

Defined in `handles-product-spec.md` Section 2. Demand-specific additions:

| Action | Credits |
|--------|---------|
| Submitting a demand item that reaches 50 votes | 100 |
| Your demand item gets funded/shipped by vendor | 500 |
| Credit boost vote on a demand item | −50 |

Credits earned from demand participation are the same credits spendable on Pro features (fresh data, work-class reports). The economy is unified — there is no separate "demand currency."

---

## 3. Vendor Custom-Segment Request Contract

### What Vendors Can Request

Vendors (AI providers, model vendors) can purchase access to custom aggregated segment reports. They do NOT get raw data or individual wheel data — they get Wheelwright-mediated aggregated insights.

### Request Contract

```json
{
  "vendor_id": "<verified vendor account>",
  "request_type": "segment_report",
  "segment_definition": {
    "task_classes": ["architecture", "planning"],
    "model_filter": "claude-*",
    "min_sample_size": 100,
    "time_window_days": 30
  },
  "purpose": "model performance evaluation",
  "agreed_terms_version": "1.0",
  "requested_at": "ISO-8601"
}
```

### Wheelwright as Mediator

Wheelwright computes the report server-side and returns only the aggregated result. The vendor never touches underlying wheel data.

```
Vendor request  →  Handles API  →  Aggregation engine  →  Report (no raw data)
                                   ↑
                   Minimum cohort size enforced (n >= 100 for vendor segments)
                   Anti-gaming filters applied
                   Privacy review passes
```

**What vendors can see:** Aggregated model performance scores, work-class rankings, adoption trends for their model — all in the same delayed/aggregated format as Pro tier, with custom segment filtering.

**What vendors cannot see:** Individual wheel identities, project contents, competitor wheel data, or anything that could re-identify a user.

---

## 4. Privacy, Consent, Trust, and Anti-Displacement Rules

### Privacy Rules

1. No demand item can include personal project details — submissions are reviewed for PII before publishing
2. Vote records are pseudonymous — Wheelwright does not correlate votes to real identities
3. Vendor interest signals are not shared with other vendors
4. Custom segment reports are delivered only to the requesting vendor — not published

### Consent

- Members consent to their demand votes being aggregated and surfaced to vendors during registration
- Consent is item-level: a member can mark a vote as "anonymous to vendors" at vote time
- Revoking consent removes the member's votes from future vendor reports (historical aggregates already delivered are unaffected)

### Operator-Relationship Stays Central

**Anti-displacement principle:** The demand exchange supplements the user's relationship with Wheelwright — it does not shift loyalty to individual AI vendors.

Concretely:
- Vendor branding on demand items is limited (no vendor logos dominating the board)
- Demand items targeting `wheelwright` (framework improvements) are displayed more prominently than vendor-targeted items
- Vendor interest signals cannot boost item rank on the community board
- Wheelwright retains editorial control over which vendor requests are fulfilled

---

## 5. How Marketplace Demand Feeds Roadmap and Monetization

### Roadmap Signal

High-demand items (top 5% by vote) are surfaced to the Wheelwright roadmap team as community signals. These are advisory — the team decides independently what to build.

Items that address Wheelwright core (framework, hub, spoke protocols) are treated as community priority signals. Items targeting vendors are surfaced to those vendors as paid intelligence.

### Monetization

| Revenue source | Mechanism |
|---|---|
| Vendor segment reports | One-time or subscription fee per custom segment |
| Credit boost votes | Members spend credits to amplify votes (credits already earned through participation) |
| Demand board API | Pro/Enterprise members can query the demand board programmatically |

**Key constraint:** The demand exchange does not move private money between users and vendors in v1. No feature bounties, no user payouts. The exchange is information, not funds.

---

## Verification Checklist

- [ ] Vendor access is mediated — no raw data exposure ✓
- [ ] Community vote and vendor interest signal are separate ✓
- [ ] Credit economy is unified with Handles Pro features ✓
- [ ] Operator relationship stays central (anti-displacement rules) ✓
- [ ] No financial transactions between users and vendors in v1 ✓
- [ ] Local Wheelwright usefulness does not depend on marketplace participation ✓
- [ ] Protected track-restoration plugins excluded from this spec ✓
