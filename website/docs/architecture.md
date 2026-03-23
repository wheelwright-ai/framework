# Wheelwright Web — Architecture Overview

## Purpose

The `website/` layer is the product and commercial surface of Wheelwright. It is entirely optional for local operation — the hub-spoke system works without it. This layer adds networked intelligence: shared model-performance data, community rankings, and premium insight services.

## Service Boundary

```
Local Wheelwright (hub + spokes)     Wheelwright Web (this layer)
─────────────────────────────────    ──────────────────────────────
WAI-Spoke/                           website/api/          ← REST endpoints
WAI-Lugs.jsonl                       website/services/     ← business logic
hub routing table                    website/models/       ← data schemas
Octo / Ozi orchestration             website/docs/         ← specs (this dir)
```

Local operation NEVER requires the web layer. The web layer is additive.

## Products Living Here

| Product | Spec | Status |
|---------|------|--------|
| Cohort Sharing | `cohort-sharing-contract.md` | defined |
| Wheelwright Handles | `handles-product-spec.md` | defined |
| Demand Exchange | `demand-exchange-spec.md` | defined |
| Consultation Exchange | `consultation-exchange-spec.md` | defined |

## Key Constraints (apply to all products)

1. **Local-first:** No product in this layer breaks hub-spoke operation if unavailable.
2. **Privacy-by-default:** Telemetry contribution is opt-in. No raw private data is ever exposed publicly.
3. **Delayed public data:** Free-tier public reports are trailing-average with a minimum 4-day delay.
4. **Provenance required:** All rankings and scores carry confidence, sample size, and anti-gaming metadata.
5. **No vendor lock-in:** Storage and delivery integrations are hooks, not the product.
