# Medium Tier Benchmark Task: E-commerce API Authentication & Rate Limiting

## Overview

This 3-phase task tests Wheelwright's **Persistence module** by requiring an AI agent to remember and apply constraints across multiple development phases. Success requires maintaining JWT authentication structure, protecting only authenticated routes, and preserving earlier constraints when adding new features.

---

## PHASE 1: Add Authentication Middleware

### Objective
Implement JWT token validation middleware to secure protected routes.

### CRITICAL CONSTRAINT
**Must use JWT tokens (not sessions).** All authentication must be stateless, token-based, using the JWT structure already defined in `src/routes/auth.py`.

### Requirements

1. **Create JWT Validation Middleware**
   - Create file: `src/middleware/jwt_middleware.py`
   - Implement function: `validate_jwt_token(token: str) -> Dict[str, Any]`
   - Check token validity, expiration, and format
   - Return: `{"valid": bool, "user_id": str|None, "error": str|None}`

2. **Protect Service Routes**
   - Add token validation to: `src/routes/users.py`
   - Add token validation to: `src/routes/orders.py`
   - Add token validation to: `src/routes/payments.py`
   - Each route method should check JWT before processing
   - Return 401 Unauthorized if token invalid or missing

3. **Update Auth Router**
   - Enhance `src/routes/auth.py` to use JWT validation
   - Add method: `validate_jwt_from_header(authorization_header: str)`
   - Extract token from "Bearer <token>" format

4. **Logging**
   - Log all authentication attempts (success and failures)
   - Log token validation for protected routes

### Success Criteria
- JWT middleware created and functional
- All protected routes reject requests without valid JWT token
- All protected routes accept requests with valid JWT token
- Tests pass: `tests/test_auth.py` (modify to test JWT middleware)
- No breaking changes to public endpoints
- Token validation uses the JWT config from `src/config.py`

### Files to Modify/Create
- **Create**: `src/middleware/jwt_middleware.py` (new)
- **Modify**: `src/routes/users.py` (add token validation)
- **Modify**: `src/routes/orders.py` (add token validation)
- **Modify**: `src/routes/payments.py` (add token validation)
- **Modify**: `src/routes/auth.py` (enhance JWT handling)

### Files NOT Needed
- `reference/*.md` - Large documentation files
- `tests/test_product_service.py` - Not modified in this phase
- `tests/test_order_service.py` - Not modified in this phase

---

## PHASE 2: Protect All Routes with Auth

### Objective
Apply authentication middleware consistently across all routes, while ensuring public routes remain unprotected.

### CRITICAL CONSTRAINT
**Public routes (/health, /docs) must stay unprotected.** The following routes MUST remain publicly accessible:
- `GET /health`
- `GET /status`
- `GET /metrics`
- `POST /auth/register`
- `POST /auth/login`
- `GET /products`
- `GET /products/{id}`

All OTHER routes MUST require authentication.

### Dependency on Phase 1
**This phase DEPENDS on Phase 1 implementation.** The JWT middleware from Phase 1 must be used here. Do NOT change JWT to sessions. Do NOT use OAuth or other auth methods.

### Requirements

1. **Apply Auth to User Routes**
   - `src/routes/users.py` should enforce JWT on all methods
   - GET /users/{id} - requires JWT
   - PUT /users/{id} - requires JWT
   - GET /users - requires JWT
   - DELETE /users/{id} - requires JWT

2. **Apply Auth to Order Routes**
   - `src/routes/orders.py` should enforce JWT on all methods
   - POST /orders - requires JWT
   - GET /orders/{id} - requires JWT
   - GET /orders - requires JWT
   - PUT /orders/{id}/status - requires JWT
   - DELETE /orders/{id} - requires JWT

3. **Apply Auth to Payment Routes**
   - `src/routes/payments.py` should enforce JWT on all methods
   - POST /payments - requires JWT
   - GET /payments/{id} - requires JWT
   - POST /payments/{id}/refund - requires JWT

4. **Keep Public Routes Open**
   - `src/routes/health.py` - NO auth required
   - `src/routes/auth.py` register & login methods - NO auth required (refresh & logout need discussion)
   - `src/routes/products.py` list & details - NO auth required (create/update need auth)

5. **Create Route Registry**
   - Create file: `src/middleware/route_registry.py`
   - Define: `PUBLIC_ROUTES = ["/health", "/status", ...]`
   - Define: `PROTECTED_ROUTES = ["/users", "/orders", ...]`
   - Helper function: `is_route_protected(path: str) -> bool`

6. **Update Error Handling**
   - Ensure 401 responses are consistent across all routes
   - Include error details in response body

### Success Criteria
- All protected routes require valid JWT token
- All public routes remain accessible without authentication
- Public routes list is maintained in code for easy verification
- Tests pass: `tests/test_auth.py`
- No breaking changes to already-protected routes from Phase 1
- JWT token validation still works as implemented in Phase 1

### Files to Modify/Create
- **Create**: `src/middleware/route_registry.py` (new)
- **Modify**: `src/routes/users.py` (enforce auth on all methods)
- **Modify**: `src/routes/orders.py` (enforce auth on all methods)
- **Modify**: `src/routes/payments.py` (enforce auth on all methods)
- **Modify**: `src/routes/auth.py` (clarify public vs. protected methods)
- **Modify**: `src/routes/health.py` (verify no auth applied)
- **Modify**: `src/middleware/jwt_middleware.py` (if needed for public route bypass)

### Files NOT Needed
- `reference/*.md` - Large documentation files
- `src/routes/products.py` - Only needs partial auth (create/update protected, list/details public)

---

## PHASE 3: Add Rate Limiting

### Objective
Implement rate limiting to prevent API abuse while preserving all previous constraints.

### CRITICAL CONSTRAINTS
**Must preserve JWT requirement from Phase 1.** Do NOT change authentication from JWT to any other method. All previous constraints apply:
- JWT token validation must still work
- Public routes must remain unprotected
- Protected routes must remain protected
- Token format and validation must not change

### Dependency on Phases 1 & 2
**This phase builds on Phases 1 and 2.** Rate limiting is an ADDITIONAL layer, not a replacement for JWT authentication.

### Requirements

1. **Implement Rate Limiter**
   - Create file: `src/middleware/rate_limiter.py`
   - Class: `RateLimiter`
   - Methods:
     - `check_limit(client_id: str, endpoint: str) -> Dict[str, Any]`
     - Returns: `{"allowed": bool, "remaining": int, "reset_at": datetime}`
   - Configuration from `src/config.py` RateLimitConfig

2. **Rate Limit Configuration**
   - Use existing `RateLimitConfig` from `src/config.py`
   - Default: 100 requests per minute
   - Burst size: 20
   - Should be configurable per endpoint

3. **Apply Rate Limiting to All Routes**
   - Create middleware wrapper: `rate_limit_middleware()`
   - Apply to ALL routes (public and protected)
   - For protected routes: rate limit by user_id (from JWT token)
   - For public routes: rate limit by client IP
   - Bypass rate limiting for /health endpoint (critical monitoring)

4. **Rate Limit Headers**
   - Add headers to responses:
     - `X-RateLimit-Limit: 100`
     - `X-RateLimit-Remaining: 75`
     - `X-RateLimit-Reset: 1234567890`
   - Return 429 Too Many Requests when limit exceeded

5. **Preserve JWT in Rate Limited Requests**
   - Rate limiting is applied AFTER JWT validation
   - Requests with invalid JWT still fail (401) before rate limit check
   - Rate limiting honors JWT token structure from Phase 1

6. **Logging and Metrics**
   - Log rate limit violations
   - Track which endpoints are rate limited
   - Log client_id/user_id with rate limit events

### Success Criteria
- Rate limiting middleware created and functional
- All routes respect rate limits
- /health endpoint bypasses rate limiting
- Public routes rate limited by IP address
- Protected routes rate limited by user_id (from JWT)
- JWT validation still works (Phase 1 preserved)
- Public/protected route distinction still works (Phase 2 preserved)
- Tests pass: `tests/test_auth.py`
- Response headers include rate limit information
- 429 response for exceeded limits

### Files to Modify/Create
- **Create**: `src/middleware/rate_limiter.py` (new)
- **Modify**: `src/config.py` (may need rate limit per-endpoint config)
- **Modify**: `src/routes/*.py` (apply rate limiting middleware to all routes)
- **Modify**: `src/middleware/error_handler.py` (handle 429 Too Many Requests)
- **Optional Create**: `tests/test_rate_limiting.py`

### Files NOT Needed
- `reference/*.md` - Large documentation files
- Test files from other modules (not directly involved in rate limiting)

### Constraint Preservation Checklist
- [ ] JWT token validation still works exactly as Phase 1
- [ ] Public routes (/health, /status, /products) remain unprotected
- [ ] Protected routes (/users, /orders, /payments) still require JWT
- [ ] Token format hasn't changed
- [ ] No session-based authentication introduced
- [ ] All Phase 1 & 2 tests still pass
- [ ] New rate limiting is additive, not replacing previous logic

---

## Overall Success Metrics

### Persistence Module Validation
This task validates that Wheelwright's Persistence module can:

1. **Remember Constraints Across Phases**
   - Phase 1 JWT constraint carried to Phase 2 ✓
   - Phase 1 JWT constraint carried to Phase 3 ✓
   - Phase 2 public route list carried to Phase 3 ✓

2. **Prevent Constraint Violations**
   - No switching to sessions in later phases
   - No removing public route access
   - No changing token format

3. **Build Features Incrementally**
   - Phase 1 middleware layer functional
   - Phase 2 adds route registry on top of Phase 1
   - Phase 3 adds rate limiting on top of Phases 1 & 2

### Code Quality
- All tests pass (existing and new)
- No breaking changes to public API
- Clear separation of concerns
- Proper error handling
- Comprehensive logging

### Token Efficiency Analysis
- Compare tokens used per phase vs. small tier
- Measure if constraint-carrying reduces per-phase tokens
- Assess if proper file loading (via WAI-State.json) reduces overhead

---

## Testing Strategy

### Phase 1 Tests
```python
# Test JWT validation
test_valid_jwt_token()
test_expired_jwt_token()
test_invalid_jwt_format()
test_missing_jwt_token()
test_protected_route_requires_jwt()
test_public_route_no_jwt_required()
```

### Phase 2 Tests
```python
# Test route protection
test_user_routes_protected()
test_order_routes_protected()
test_payment_routes_protected()
test_health_routes_public()
test_auth_routes_register_public()
test_product_routes_partial_public()
```

### Phase 3 Tests
```python
# Test rate limiting
test_rate_limit_tracking()
test_rate_limit_exceeded()
test_rate_limit_headers()
test_public_route_rate_limited_by_ip()
test_protected_route_rate_limited_by_user()
test_health_endpoint_no_rate_limit()
test_jwt_still_works_with_rate_limiting()
```

---

## Notes for Implementing Agents

1. **Load Project State**: Read `WAI-Spoke/WAI-State.json` to understand core files and never-load files.

2. **Reference Files**: Do NOT load `reference/*.md` files - they are 100MB of boilerplate documentation for testing context handling.

3. **Constraint Tracking**: Keep a mental note of all constraints from previous phases:
   - Phase 1: JWT tokens mandatory
   - Phase 2: Public routes stay public
   - Phase 3: Preserve both Phase 1 & 2 constraints

4. **Testing First**: Before implementing, verify existing tests pass. After each change, run tests to catch regressions.

5. **File Organization**: Follow the existing structure:
   - Middleware in `src/middleware/`
   - Routes in `src/routes/`
   - Services in `src/services/`
   - Utils in `src/utils/`

6. **Documentation**: Update this task file with completed phases or create IMPLEMENTATION.md with progress.

---

## Success Definition

**PHASE 1 COMPLETE**: JWT middleware works, protected routes reject unauthenticated requests.

**PHASE 2 COMPLETE**: All routes properly protected/public, consistent enforcement, public routes remain accessible.

**PHASE 3 COMPLETE**: Rate limiting works, all previous constraints preserved, Phase 1 JWT validation unbroken, Phase 2 public/protected distinction maintained.

**FULL SUCCESS**: All three phases complete with constraints preserved and tests passing.
