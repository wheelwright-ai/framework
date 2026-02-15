# Common Use Cases

## Solo Developer with Multiple Projects

**Scenario:** You maintain 5 different projects and want patterns from one to benefit others.

**Setup:**
- Hub at `~/wheelwright-hub`
- 5 spokes (one per project)
- Each spoke submits high-impact learnings to hub/intake/
- Hub processes patterns, broadcasts back to all spokes

**Example:**
1. Project A discovers SQL injection pattern, creates diagnosis Lug (impact: 9)
2. Spoke auto-submits to hub/intake/
3. On next hub wakeup, hub-processor detects pattern
4. Creates hub observation Lug: "SQL injection pattern seen in Project A"
5. Project B wakes up, hub-watcher pulls this signal
6. Project B agent sees warning about SQL injection, checks its own code

**Value:** Learn once, apply everywhere.

---

## Team with Shared Coding Standards

**Scenario:** Team of 5 developers, want consistent code quality across all repos.

**Setup:**
- Centralized hub with team-wide policies in hub/BRIEF.md
- Each developer's projects are spokes inheriting hub policies
- QA skill runs on all commits, creates diagnosis Lugs

**Hub BRIEF.md:**
```markdown
## Always
- Maintain 80% test coverage
- Run safe-refactor before structural changes
- Create decision Lugs for architectural choices

## Never
- Deploy without tests passing
- Commit secrets or credentials
- Skip security review on auth changes
```

**Value:** Policies cascade to all projects. No copy-paste, no drift.

---

## Long-Running Migration

**Scenario:** Migrating auth from JWT to sessions across 20 routes over 3 weeks.

**Setup:**
- Use WAI-Ledger.jsonl to track commitments across sessions
- Break work into 20 task Lugs (one per route)
- Each session: agent reads ledger, sees what's still open

**Ledger entries:**
```jsonl
{"type":"request","content":"Migrate all 20 routes from JWT to sessions","status":"open"}
{"type":"agreement","content":"Will migrate 5 routes per week, starting with public routes","status":"open"}
{"type":"delivery","content":"Routes 1-5 migrated","commit":"abc123","status":"fulfilled"}
{"type":"delivery","content":"Routes 6-10 migrated","commit":"def456","status":"fulfilled"}
...
```

**Closeout each session:** Reconciles ledger, shows "10 routes done, 10 remaining"

**Value:** No context loss. Work survives across weeks, token limits, crashes.

---

## Multi-Agent Collaboration

**Scenario:** Main agent orchestrates, specialist skills handle specific domains.

**Agents:**
- **Main agent** (expensive, Sonnet 4.5): Writes code, makes decisions
- **safe-refactor** (cheap, Haiku): Checkpoints git before structural changes
- **qc-check** (medium, Sonnet 3.5): Runs tests, diagnoses failures
- **security-review** (expensive, Opus 4.5): Scans for vulnerabilities on auth changes

**Workflow:**
1. Main agent plans change: "Refactor auth module"
2. safe-refactor fires automatically (pre-refactor trigger)
3. Main agent makes changes
4. qc-check fires on commit, finds test failure
5. Main agent fixes based on diagnosis Lug
6. security-review fires (auth code changed)
7. security-review creates 2 diagnosis Lugs (SQL injection, session fixation)
8. Main agent addresses both issues

**Value:** Specialization. Cheap agents do repetitive checks, expensive agents solve hard problems.

---

## Institutional Memory (Decision Tracking)

**Scenario:** 6 months from now, you need to know "why did we choose X over Y?"

**Setup:**
- Create decision Lugs whenever making architectural choices
- Include alternatives_considered with reasoning

**Example decision Lug:**
```json
{
  "type": "decision",
  "title": "Use JWT tokens instead of sessions",
  "alternatives_considered": [
    {
      "option": "Server-side sessions",
      "chosen": false,
      "reasoning": "Requires sticky sessions with load balancer, adds state complexity"
    },
    {
      "option": "JWT tokens",
      "chosen": true,
      "reasoning": "Stateless, works with horizontal scaling, simpler deployment"
    }
  ],
  "summary": "Chose JWT for stateless auth. Trade-off: token revocation is harder but worth it for scaling simplicity."
}
```

**6 months later:**
- Agent reads past decision Lugs
- Sees JWT was chosen specifically for horizontal scaling
- When refactoring auth, preserves this requirement

**Value:** Institutional memory. Decisions persist beyond any single developer or session.

---

## Preventing Data Loss

**Scenario:** Agent previously destroyed Hub folder by restructuring files.

**Setup:**
- WAI-Integrity.md defines data protection rules
- safe-refactor fires before structural changes
- Destructive ops require human gate

**Protection layers:**
1. **Read-only paths:** Framework files can't be modified
2. **Append-only paths:** WAI-Lugs.jsonl and WAI-Ledger.jsonl only grow
3. **Scoped writes:** Spokes write to their own directory only
4. **Pre-refactor checkpoint:** Git commit before structural changes
5. **Human gate:** Deleting data requires explicit approval

**What prevented:**
- Hub folder deletion (read-only)
- Lug file truncation (append-only)
- Cross-project file modification (scoped writes)

**Value:** Safety net. Agents can't accidentally destroy critical data.

---

## E2E Benchmarking (Performance Validation)

**Scenario:** Want to prove WAI reduces token usage vs baseline agents.

**Setup:**
- Benchmark projects at benchmarks/projects/small and benchmarks/projects/medium
- Each has reference documentation (large, unnecessary files)
- Compare baseline (loads everything) vs Wheelwright (selective loading)

**Results:**
- **Small tier:** 3900.7x token efficiency (24 files → 3 files, 20MB → 3.3KB)
- **Medium tier:** 7833.1x token efficiency (59 files → 5 files, 100MB → 11KB)
- **Critical test:** Wheelwright NEVER loads reference files (0/10 loaded)

**How it works:**
- WAI-Manifest.yaml defines file_load_policy:
  ```yaml
  file_load_policy:
    load_always: ["src/formatters/data.py"]
    load_on_demand: ["src/utils/logger.py"]
    never_load: ["reference/**/*"]
  ```
- Agent respects policy, loads only necessary files
- Massive token savings, faster responses

**Value:** Quantifiable proof of efficiency gains.

---

## Cross-Project Pattern Detection

**Scenario:** Want to know if same bug appears in multiple projects.

**Setup:**
- Hub aggregates signals from all spokes
- hub-processor detects recurring patterns

**Flow:**
1. Project A: security-review finds SQL injection, creates Lug (impact: 9)
2. Project A submits to hub/intake/
3. Project B: security-review finds same pattern, submits to hub
4. Hub wakeup: hub-processor sees 2 spokes with same diagnosis
5. Creates hub observation Lug: "SQL injection pattern detected in 2 projects"
6. Suggests: "Promote parameterized query helper to framework template"

**Value:** Learn from mistakes across ALL projects, not just one.

---

## Communication Style Consistency

**Scenario:** Want all agents to respond in consistent format (terse, numbered lists).

**Setup:**
- hub/BRIEF.md Communication Style section defines format rules
- All spokes inherit via cascade
- preference Lugs capture style feedback

**hub/BRIEF.md:**
```markdown
### Communication Style

**Response Format:**
- Lead with the answer, then supporting details
- Use numbered lists for multi-part answers
- Verification responses: max 10 lines total
- No verbose explanations unless errors found

**Tone Matching:**
- Mirror user's verbosity (terse question → terse answer)
- Match technical depth to question specificity
```

**User feedback:** "Too verbose, just give me bullets"
**Agent creates:** preference Lug documenting this
**Later:** Preference consolidated into hub/BRIEF.md via /wai-teach

**Value:** Agents learn your communication preferences, apply consistently.
