# Multi-Agent Colony Patterns

WAI enables agent colonies: groups of specialized agents working together under a conductor's direction.

## The Colony Model

```
Conductor (Human)
    ↓
Main Agent (Expensive - Sonnet/Opus)
    ↓ orchestrates
┌────────────────────────────────────┐
│ Skill Agents (Cheap - Haiku/Flash) │
├────────────────────────────────────┤
│ safe-refactor │ qc-check │ review │
│ hub-watcher   │ session-observer  │
└────────────────────────────────────┘
```

## Why Colonies?

**Problem:** Expensive models are good at everything but costly.
**Solution:** Use expensive models for hard problems, cheap models for routine checks.

**Cost comparison:**
- Opus 4.5: $15/M input, $75/M output
- Sonnet 4.5: $3/M input, $15/M output
- Haiku 3.5: $0.25/M input, $1.25/M output

Running safe-refactor with Haiku costs 60x less than Opus. For routine git checkpoints, Haiku is sufficient.

## Skill Roles

### Guardian (Pre-emptive Protection)
**Model:** Lightweight (Haiku)
**Trigger:** Before risky operations
**Examples:**
- `safe-refactor` - Git checkpoint before structural changes
- `backup-check` - Verify backups before deletions

### Reviewer (Quality Assurance)
**Model:** Standard (Sonnet) or Lightweight (Haiku)
**Trigger:** After changes
**Examples:**
- `qc-check` - Run tests, report failures
- `security-review` - Scan for vulnerabilities
- `lint-check` - Code style validation

### Advisor (Guidance)
**Model:** Standard (Sonnet)
**Trigger:** When thresholds crossed
**Examples:**
- `complexity-advisor` - Warn when task is complex
- `context-advisor` - Warn when context is filling up
- `signal-advisor` - Auto-submit high-impact Lugs

### Watcher (Observation)
**Model:** Lightweight (Haiku)
**Trigger:** Session events
**Examples:**
- `session-observer` - Track events, create closeout summary
- `hub-watcher` - Check hub for updates on wakeup
- `hub-processor` - Process intake on hub wakeup

## Orchestration Flow

```
User: "Refactor auth module to use sessions"

1. Main Agent receives task
2. safe-refactor fires (guardian, lightweight)
   → Creates checkpoint commit
3. Main Agent plans and implements changes
4. qc-check fires (reviewer, standard)
   → Runs tests, finds failure
   → Creates diagnosis Lug
5. Main Agent fixes based on diagnosis
6. security-review fires (reviewer, advanced)
   → Scans auth code
   → Creates 2 diagnosis Lugs
7. Main Agent addresses security issues
8. signal-advisor fires (advisor, lightweight)
   → Detects high-impact Lugs
   → Submits to hub/intake/
9. User triggers closeout
10. session-observer fires (watcher, lightweight)
    → Reconciles ledger
    → Creates session summary Lug
```

## Model Selection Guidelines

| Task Type | Model Tier | Examples |
|-----------|------------|----------|
| File existence, git status | Lightweight | safe-refactor, hub-watcher |
| Code analysis, test interpretation | Standard | qc-check, security-review |
| Architecture decisions, complex reasoning | Advanced | brief-advisor, complexity-advisor |

## Communication via Lugs

Skills communicate through Lugs, not direct messages:

```
security-review creates:
  Lug: {type: "diagnosis", title: "SQL injection in auth handler", impact: 9}

Main Agent reads Lug, addresses issue

Main Agent creates:
  Lug: {type: "prescription", title: "Parameterized queries", diagnosis_id: "..."}

On resolution:
  Lug updated: {status: "resolved", resolution: "accepted", commit: "abc123"}
```

## Cross-Session Learning

Skills learn from past decisions:

```
security-review checks:
  "Has this pattern been seen before?"
  → Reads past diagnosis Lugs
  → "Similar issue in auth handler was fixed with parameterized queries"
  → Includes context in new diagnosis
```

**Decision Lugs feed the apprenticeship loop:**
- Sub-agents reference past decision Lugs
- Learn conductor's risk tolerance, quality standards, priorities
- Adjust recommendations based on patterns

## Model Diversification

Mix providers for resilience and capability:

```yaml
skills:
  safe-refactor:
    model: haiku  # Fast, cheap
  qc-check:
    model: sonnet  # Good code analysis
  security-review:
    model: opus  # Deep reasoning
  hub-watcher:
    model: gemini-flash  # Alternative provider
```

Benefits:
- No single provider dependency
- Match model to task requirements
- Cost optimization

## Anti-Patterns

### ❌ Expensive Model for Routine Checks
```yaml
safe-refactor:
  model: opus  # Overkill for git status + commit
```

### ❌ Cheap Model for Complex Reasoning
```yaml
architecture-advisor:
  model: haiku  # Can't handle nuanced decisions
```

### ❌ Direct Communication Instead of Lugs
```python
# Bad: Skills talking directly
main_agent.message(security_review, "Found a bug")

# Good: Skills communicate via Lugs
create_lug(type="diagnosis", title="Found SQL injection")
```

### ❌ No Conductor Gate for Destructive Actions
```yaml
file-deleter:
  trigger: auto
  # Missing: requires_approval: true
```

## Best Practices

1. **Use the cheapest model that works** - Don't pay Opus prices for Haiku tasks
2. **Create Lugs for everything** - Communication happens through files
3. **Let skills run automatically** - Trust the trigger conditions
4. **Review high-impact findings** - Conductor makes final decisions
5. **Learn from decisions** - Reference past decision Lugs in recommendations
