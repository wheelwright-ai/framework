# Signal Best Practices

**Purpose:** Guidelines for creating, reviewing, and adopting cross-node signals
**Audience:** Spoke developers and maintainers
**Version:** 1.0.0

---

## When to Create Signals

### ✅ Good Signal Candidates (Impact >= 8)

**Architecture Patterns:**
- ✅ "Hexagonal architecture for microservices isolation"
- ✅ "Event sourcing for audit trail requirements"
- ✅ "CQRS pattern for read-heavy workloads"

**Performance Optimizations:**
- ✅ "Caching layer reduces DB load 60%"
- ✅ "Connection pooling eliminates timeout errors"
- ✅ "Lazy loading improves page load 2x"

**Critical Bugs:**
- ✅ "Race condition in concurrent payment processing"
- ✅ "Memory leak from unclosed event listeners"
- ✅ "SQL injection via unescaped user input"

**Development Patterns:**
- ✅ "Co-located tests reduce maintenance burden"
- ✅ "Feature flags enable gradual rollout"
- ✅ "Pre-commit hooks prevent secret leaks"

### ❌ Bad Signal Candidates (Don't Create)

**Low Impact:**
- ❌ "Fixed typo in variable name" (impact: 2)
- ❌ "Updated README formatting" (impact: 3)
- ❌ "Refactored function name for clarity" (impact: 4)

**Spoke-Specific:**
- ❌ "Updated our custom config file format" (not applicable elsewhere)
- ❌ "Changed our internal API endpoints" (spoke-specific implementation)
- ❌ "Adjusted our deployment script" (local tooling)

**Temporary:**
- ❌ "Temporary workaround for deployment issue" (not permanent)
- ❌ "Quick fix until library updated" (temporary hack)
- ❌ "Emergency hotfix for production" (not a pattern)

---

## Writing Good Signals

### Title (< 80 characters)

**Pattern:** `[Pattern/Bug/Optimization] + [Benefit/Problem] + [Metric if applicable]`

**Good titles:**
- ✅ "JWT refresh strategy reduces auth overhead 40%"
- ✅ "Co-located tests reduce maintenance burden"
- ✅ "Race condition in concurrent writes causes duplicates"

**Bad titles:**
- ❌ "Authentication stuff" (too vague)
- ❌ "The way we do JWT tokens with refresh and sliding windows..." (too long)
- ❌ "Bug" (not descriptive)

### Body (2-5 sentences)

**Pattern:** Context + Problem + Solution + Result

**Example:**
```
Discovered efficient JWT refresh pattern using sliding window refresh
(15min token, 7day refresh token). Previous approach had tokens
expiring every 5 minutes, causing 200+ refresh calls/hour and poor
UX. New pattern reduced refresh overhead by 40% and eliminated
user complaints about frequent re-logins.
```

### PEV (Perspective-Evidence-Verdict)

**Perspective:** What was the situation/problem?
- "JWT tokens expiring too frequently caused UX issues"
- "Separated tests (tests/ directory) became stale"
- "Two simultaneous requests could charge user twice"

**Evidence:** What data/observations support this?
- "User complaints about re-login, metrics showed 200+ refresh calls/hour"
- "Found 8 orphaned test files, 12 tests not updated when code changed"
- "Production logs show 3 duplicate charge incidents in one week"

**Verdict:** What was the conclusion/solution?
- "Sliding window refresh (15min/7day) eliminated re-login issues"
- "Co-located tests eliminate orphan problem, tests move with code"
- "Added transaction lock, eliminated duplicate charges"

### Tags (3-5 tags)

**Categories:**
- Pattern type: `architecture`, `performance`, `testing`, `security`
- Domain: `authentication`, `caching`, `database`, `concurrency`
- Impact type: `bug-fix`, `optimization`, `pattern`, `lesson`

**Good tags:**
- ✅ `["authentication", "jwt", "performance", "pattern"]`
- ✅ `["testing", "maintenance", "architecture", "pattern"]`
- ✅ `["concurrency", "bug-fix", "critical", "race-condition"]`

**Bad tags:**
- ❌ `["stuff", "things", "update"]` (too vague)
- ❌ `["authentication", "auth", "user-auth", "jwt-auth"]` (redundant)

---

## Reviewing Signals

### When to Adopt vs Acknowledge

**Adopt (create local Lug):**
- Pattern directly applicable to your spoke
- You plan to implement this pattern soon
- High relevance to current work

**Acknowledge (archive only):**
- Pattern interesting but not immediately applicable
- Different technology stack (e.g., Python pattern, you use Node)
- Good to know, but not actionable now

**Skip (leave in queue):**
- Need more time to evaluate
- Waiting for team discussion
- Will review in next session

### Review Frequency

**Recommended:** Weekly or bi-weekly

**Triggers:**
- hub-watcher notification on session_start
- Before planning new features (check for existing patterns)
- After completing major work (reflect on what could be shared)

---

## Signal Hygiene

### For Signal Publishers

**Before publishing:**
1. Check impact threshold (>= 8)
2. Verify applicability beyond your spoke
3. Search hub/intake/ for duplicates
4. Sanitize sensitive information
5. Write clear PEV (not just body)

**Don't publish:**
- Secrets or credentials
- Customer data or PII
- Proprietary algorithms
- Security vulnerabilities (until patched across ecosystem)

### For Signal Reviewers

**When reviewing:**
1. Read full signal (title + body + PEV)
2. Consider applicability to your spoke
3. Check if similar pattern already adopted
4. Archive signals you've reviewed (don't leave in queue)

**Don't ignore:**
- Critical bugs (impact: 10) - review immediately
- Signals from similar spokes (likely applicable)
- Signals older than 7 days (prevent staleness)

---

## Common Patterns

### Pattern 1: Architecture Decision

**When to signal:**
- Choosing between 2+ architectural approaches
- Decision has cross-cutting impact
- Pattern reusable in other spokes

**Example:**
```json
{
  "title": "CQRS pattern for read-heavy workloads",
  "body": "Separated read and write models for API. Reads served from
          optimized read cache, writes go to normalized DB. Improved
          read latency 10x.",
  "pev": {
    "perceive": "Read queries slowing down write operations",
    "execute": "95% of requests are reads, 5% writes. Contention high.",
    "verify": "CQRS separated concerns, read latency dropped 10x"
  },
  "impact": 9,
  "tags": ["architecture", "cqrs", "performance", "pattern"]
}
```

### Pattern 2: Bug Lesson

**When to signal:**
- Critical or high-impact bug (>= 8)
- Root cause non-obvious
- Lesson prevents similar bugs elsewhere

**Example:**
```json
{
  "title": "Race condition in concurrent payment processing",
  "body": "Two simultaneous requests could charge user twice due to
          race condition in payment state check + update. Added
          transaction lock around payment flow.",
  "pev": {
    "perceive": "Reports of duplicate charges from users",
    "execute": "3 duplicate charge incidents, race condition confirmed",
    "verify": "Transaction lock eliminated duplicates (zero incidents since)"
  },
  "impact": 10,
  "tags": ["bug-fix", "concurrency", "critical", "payments"]
}
```

### Pattern 3: Performance Optimization

**When to signal:**
- Significant performance improvement (> 2x)
- Technique applicable to similar workloads
- Optimization measurable and repeatable

**Example:**
```json
{
  "title": "Caching layer reduces DB load 60%",
  "body": "Added Redis caching layer for frequently-accessed data.
          Cache hit rate 85%, DB query load dropped 60%, API latency
          improved 3x.",
  "pev": {
    "perceive": "DB queries bottleneck for API performance",
    "execute": "DB at 80% capacity, 200ms average query time",
    "verify": "Redis cache reduced load to 40%, query time down to 50ms"
  },
  "impact": 8,
  "tags": ["performance", "caching", "optimization", "redis"]
}
```

---

## Troubleshooting

### Signal Not Created

**Check:**
- Impact >= 8? (wai-signal-capture threshold)
- cross_node_signals: true in WAI-Manifest.yaml?
- hub_path configured in WAI-State.json?
- Duplicate signal already in hub/intake/?

**Fix:**
- Increase impact in Lug if appropriate
- Enable cross_node_signals in manifest
- Configure hub_path in state
- Verify uniqueness before publishing

### Signal Not Discovered

**Check:**
- hub-watcher running on session_start?
- Signal file in hub/intake/ directory?
- hub/health.yaml showing pending_count > 0?

**Fix:**
- Verify hub/intake/ path accessible
- Check signal file format (*.lug.json)
- Update hub/health.yaml manually if needed

### Signal Lost/Missing

**Check:**
- Signal archived to hub/archive/?
- Signal in hub/intake/ but not visible?

**Fix:**
- Search hub/archive/{YYYY-MM}/ directories
- Check file permissions on hub/intake/
- Verify signal file not corrupted (valid JSON)

---

## Metrics for Success

### Signal Quality

**Target:** 80%+ adoption or acknowledgment rate

**Good:**
- ✅ Signals reviewed within 7 days
- ✅ 50%+ signals adopted (high relevance)
- ✅ 30%+ signals acknowledged (good to know)
- ✅ < 20% signals skipped (high quality)

**Bad:**
- ❌ Signals sitting unreviewed > 30 days (stale)
- ❌ Most signals skipped (low quality or relevance)
- ❌ hub/intake/ queue > 20 pending (backlog)

### Hub Health

**Target:** < 10 pending signals at any time

**Good:**
- ✅ Intake queue: 0-5 pending (manageable)
- ✅ Oldest pending: < 7 days (fresh)
- ✅ Archive organized: Monthly directories exist

**Bad:**
- ❌ Intake queue: > 20 pending (backlog)
- ❌ Oldest pending: > 30 days (stale)
- ❌ Archive unorganized: All files in flat structure

---

## Related Documents

- **docs/CROSS-NODE-SIGNALS.md** - Complete signal protocol
- **hub/intake/README.md** - Signal queue documentation
- **framework/skills/wai-signal-capture.yaml** - Signal creation Skill
- **framework/skills/hub-watcher.yaml** - Signal detection Skill
- **wai/signal_reviewer.py** - /wai-learn implementation

---

**Version:** 1.0.0
**Created:** Phase 7 - Integration testing
**Framework:** Wheelwright v2.0.0
