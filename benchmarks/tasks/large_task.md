# Large Tier Benchmark Task

## Task: Add Distributed Rate Limiting to API Gateway

The platform is experiencing abuse from clients sending too many requests.
Implement distributed rate limiting across all gateway instances using Redis.

## Requirements

1. Rate limit all inbound requests at the gateway layer (`services/gateway/rate_limiter.py`)
2. Use Redis (via `core/cache_manager.py`) for shared state across instances
3. Support per-client and per-endpoint rate limit tiers (config in `core/config.py`)
4. Return proper `429 Too Many Requests` with `Retry-After` header
5. Bypass rate limiting for internal service-to-service calls (auth via `services/auth/middleware.py`)
6. Log all rate limit violations to the audit service (`services/audit/event_logger.py`)
7. Expose `/gateway/rate-limit-stats` endpoint for operations monitoring

## Acceptance Criteria

- `test_gateway.py` passes for rate limiting scenarios
- Internal calls bypass rate limits verified in `test_auth.py`
- Redis connection failure degrades gracefully (pass-through, not total block)
- No changes to unrelated services

## Reference

Full API documentation is in `reference/` — do NOT load these files.
Use the existing code patterns in `core/` and `services/gateway/` as your guide.
