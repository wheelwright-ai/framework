# Claude Code Instructions for Wheelwright Framework

**CRITICAL: This project uses Wheelwright for session continuity.**

## Priority 0: Session Start

Execute this on first message:

1. **Display Session Briefing** (Observation System Auto-Load):
   ```python
   from wai.session_hook import get_session_start_briefing
   briefing = get_session_start_briefing()
   print(briefing)  # Display to user immediately
   ```
   Auto-shows:
   - **Machine environment** (hardware, optimization status)
   - Recent work summary
   - Failed observations requiring remediation
   - Incomplete items to continue
   - Session statistics

   **This is AUTOMATIC** - briefing displays first thing, before any other action.

2. **Verify Machine Optimization** (Automatic at startup):
   The system automatically checks and applies IDE optimizations for the current machine.
   Machine profile stored in `../hub/machines/{hostname}.lug.json` includes:
   - Hardware specs (CPU, RAM, GPU)
   - Classification (high-performance/standard/low-power)
   - IDE settings recommendations
   - Optimization history

   **You'll see:** `✓ IDE optimized for {machine} ({classification})`

   This ensures you're running with optimal settings for the hardware available.

3. **Validate Session State** (Closeout Verification):
   ```bash
   python -m wai.closeout_validator --check
   ```
   Confirms:
   - ✅ Git status clean (or explains uncommitted files)
   - ✅ Observations logged (or empty if fresh session)
   - ✅ Framework detectable (or warns if misconfigured)
   - ✅ Machine profile exists (or creates one)

4. **Load WAI Context**:
   - Read WAI-Spoke/WAI-State.json (project state, decisions)
   - Read WAI-Spoke/WAI-State.md (strategic vision)
   - Invoke skills (behavioral rules live in skill files)

5. **Check Uncommitted Work**:
   - Run git status (validator already did this)
   - If uncommitted changes, ask: Resume or start fresh?

6. **Summary for User**:
   - **Machine:** {hostname} ({classification}, {RAM}GB RAM)
   - **Project:** name and purpose from WAI-State.md
   - **Last session:** info from WAI-State.json
   - **Environment:** tool + machine optimization status
   - **Action items:** Any failed observations needing remediation (from briefing)

## Priority 1: Behavioral Guidelines

**All behavioral rules are in skills.** Skills are authoritative source of truth.

### Machine-Aware Development (CRITICAL)

**Read:** [AI-AGENT-MACHINE-PROTOCOL.md](AI-AGENT-MACHINE-PROTOCOL.md) for complete protocol.

**Key Points:**
- Machine optimization is **automatic** at session start
- You see: `✓ IDE optimized for {machine} ({classification})`
- Session briefing shows machine class (HIGH-PERFORMANCE/STANDARD/LOW-POWER)
- **Adjust recommendations** based on machine class:
  - HIGH-PERFORMANCE (32GB+): Aggressive features, parallel execution, workspace analysis
  - STANDARD (16-31GB): Balanced features, moderate parallelism
  - LOW-POWER (<16GB): Conservative features, sequential execution
- **Check before recommending:** Heavy features on low-power = bad experience
- **Leverage capabilities:** Don't cripple high-performance machines with conservative settings

**Example:**
```python
from wai.hooks import get_machine_status
status = get_machine_status(Path.cwd())
if status['classification'] == 'high-performance':
    # Recommend aggressive type checking, workspace analysis
else:
    # Be conservative with resource-intensive features
```

**Bottom line:** Make it easy for users. System optimizes automatically - you just respect it.

Key skills:
- **Complexity gate** → wai-complexity-advisor.md (triggers on 2+ files OR 6+ steps)
- **Scope drift** → wai-stewardship-advisor.md (detects out-of-scope)
- **Foundation** → wai-foundation-advisor.md (validates before work)
- **Context** → wai-context-advisor.md (warns at 60%, 80%, 90%)
- **Signals** → wai-signal-advisor.md (logs impact >= 8)

When in doubt: Read relevant skill file. Don't memorize rules.

## Priority 2: Session Commands

All optional. Skills define when they auto-trigger.

User-invoked:
- /wai — Unified briefing
- /wai-status — Health check
- /wai-closeout — End session ceremony
- /wai-shipit — Closeout + commit with summary
- /wai-time — Token usage
- /wai-rules — Show boundaries

Note: /wai-teach and /wai-learn are hub-only (framework maintenance).
Regular spokes don't use these.

## Priority 3: Conversation Logging

Every user and assistant turn logged to WAI-Spoke/WAI-Session-Log.jsonl.
Hub learning requires closeout completion.

---

**See WAI-Spoke/README.md for file documentation.**
**Skills are in templates/commands/.**
