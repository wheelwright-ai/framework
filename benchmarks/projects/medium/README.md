# Medium Tier Benchmark Project

## Overview

A realistic e-commerce API implementation designed to test Wheelwright's **Persistence module** and constraint memory across multi-phase tasks.

- **Scope**: 40-60 Python files organized by feature (users, products, orders, payments)
- **Reference**: 100MB documentation files (to test large context handling)
- **Task Phases**: 3 phases with inter-phase constraints to validate memory

## Project Structure

```
medium/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py   # Global error handling
│   ├── models/
│   │   ├── __init__.py        # Data models (User, Product, Order, etc.)
│   │   └── database.py        # Database connections
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py    # User management
│   │   ├── product_service.py # Product catalog
│   │   ├── order_service.py   # Order processing
│   │   └── payment_service.py # Payment handling
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py          # Health check (public)
│   │   ├── auth.py            # Authentication (public)
│   │   ├── users.py           # User management (authenticated)
│   │   ├── products.py        # Product catalog (public + authenticated)
│   │   ├── orders.py          # Order management (authenticated)
│   │   └── payments.py        # Payment processing (authenticated)
│   └── utils/
│       ├── __init__.py
│       ├── password.py        # Password hashing
│       ├── validation.py      # Input validation
│       └── logger.py          # Structured logging
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_user_service.py
│   ├── test_product_service.py
│   ├── test_order_service.py
│   └── test_validation.py
├── reference/
│   └── api_reference_*.md     # 100MB documentation (generated)
└── WAI-Spoke/
    └── WAI-State.json         # Project state and core files
```

## Benchmark Objectives

### Phase 1: Add Authentication Middleware
**Constraint**: Must use JWT tokens (not sessions)

Add middleware to validate JWT tokens on all protected routes.

### Phase 2: Protect All Routes with Auth
**Constraint**: Public routes (/health, /docs) must stay unprotected

Apply authentication middleware to all routes except public ones.

### Phase 3: Add Rate Limiting
**Constraint**: Must preserve JWT requirement from Phase 1

Implement rate limiting that respects JWT authentication structure.

## Test the Persistence Module

This project tests if Wheelwright can:
1. Remember Phase 1's JWT constraint across phases
2. Recall which routes must remain public (Phase 2)
3. Apply rate limiting while maintaining JWT requirement (Phase 3)

## Running Benchmarks

1. **Generate reference files** (if not already created):
   ```bash
   python3 ../../runner/generate_reference_files.py ./reference 100
   ```

2. **Run the benchmark**:
   ```bash
   python3 ../../runner/benchmark.py ../medium/ -p medium_task.md
   ```

## File Statistics

- **Core files**: ~20 (models, services, routes)
- **Test files**: ~8
- **Supporting files**: ~20 (__init__.py, config, utils)
- **Total files**: ~50-60
- **Reference docs**: 100MB (10 files)

## Key Testing Points

1. **Constraint Memory**: Can AI maintain Phase 1 JWT constraint through subsequent phases?
2. **Route Protection**: Does AI remember which routes are public?
3. **Rate Limiting**: Can AI add rate limiting without breaking JWT structure?
4. **Code Quality**: Are changes tested and properly integrated?
5. **Token Efficiency**: How much context is needed vs. small tier?

## Notes for Agents

- Load `WAI-State.json` to understand core files vs. never-load files
- Reference documentation should NEVER be included in context
- Focus on constraint compliance across all three phases
- Test changes with existing test suite
