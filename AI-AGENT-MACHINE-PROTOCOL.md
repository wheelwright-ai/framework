# AI Agent Protocol: Machine-Aware Optimization

**For:** All AI Assistants (Claude, Copilot, Cursor, Gemini, etc.)
**Priority:** High - Execute at session start
**Effort Required:** Minimal - System is automatic

---

## Core Principle

**"To do the most with AI, you must optimize the IDE's settings, tasks file, and integrations for the machine you're running on."**

Just as you wouldn't ask a developer to code without their tools configured, don't start work without ensuring the environment is optimized for the available hardware.

---

## Your Responsibility as an AI Agent

### 1. **Verify Optimization at Session Start** ✅ AUTOMATIC

The system does this for you, but be aware:

```bash
# When user starts wai:
$ wai
✓ IDE optimized for Sparky (high-performance)
```

**What happens:**
- Machine detected (hostname)
- Profile loaded from hub
- IDE settings auto-applied
- You see confirmation message

**Your action:** None required - just be aware it happened.

### 2. **Acknowledge Machine Context**

In your session briefing, you'll see:

```markdown
## Machine Environment

🖥️  **Machine:** Sparky (HIGH-PERFORMANCE)
   RAM: 32.0 GB | CPU: Intel(R) Core(TM) i7-10850H...
   Last optimized: 9 minutes ago
```

**Your action:**
- Acknowledge the machine capabilities when relevant
- Make recommendations appropriate for the hardware class
- Don't suggest resource-intensive operations on low-power machines
- Leverage powerful hardware when available

### 3. **Respect Machine Classifications**

| Classification | What It Means | Your Behavior |
|----------------|---------------|---------------|
| **HIGH-PERFORMANCE** | 32GB+ RAM, 8+ CPU threads | Aggressive: Recommend workspace-wide analysis, parallel tasks, full type checking |
| **STANDARD** | 16-31GB RAM, 4-7 threads | Balanced: Moderate recommendations, some features |
| **LOW-POWER** | <16GB RAM, <4 threads | Conservative: Minimal overhead, file-only analysis, be gentle |

### 4. **Guide Users Through Optimization**

If you detect the machine profile doesn't exist or is outdated:

**Good Response:**
```
I notice we haven't profiled this machine yet. Let me set that up:

1. Detecting hardware... ✓
2. Creating profile... ✓
3. Optimizing IDE... ✓

Your machine (MacBook-Pro) is classified as STANDARD.
IDE configured for 16GB RAM with balanced settings.
```

**Bad Response:**
```
You need to run these commands:
1. python -m wai.skills.machine_detect --save-to-hub
2. python -m wai.skills.ide_optimize
3. Restart VS Code
```

**Why bad?** Manual steps. The system is automatic. Just invoke it.

### 5. **When Recommending Tools/Setup**

Consider the machine class:

**HIGH-PERFORMANCE Machine:**
```
✅ "Let's enable strict type checking - your 32GB RAM can handle it"
✅ "I'll analyze the entire workspace for you"
✅ "Let's run tests in parallel - you have 12 threads"
```

**LOW-POWER Machine:**
```
✅ "I'll analyze just the files you're editing to conserve memory"
✅ "Let's run tests sequentially to avoid overwhelming the CPU"
❌ "Let's enable workspace-wide analysis" (too heavy)
```

---

## Integration Checklist for AI Agents

### At Session Start
- [ ] Check if session briefing includes machine status
- [ ] Note the machine classification (high/standard/low)
- [ ] Verify optimization message was shown
- [ ] Adjust your recommendations accordingly

### During Work
- [ ] Recommend features appropriate for machine class
- [ ] Suggest parallel execution only on capable hardware
- [ ] Be conservative with memory-intensive operations on low-power
- [ ] Leverage full capabilities on high-performance machines

### Before Heavy Operations
- [ ] Check machine classification first
- [ ] Warn if operation might strain a low-power machine
- [ ] Optimize for available resources

---

## Common Scenarios

### Scenario 1: User reports "IDE is slow"

**Don't:**
```
Try disabling extensions and reducing IntelliSense settings.
```

**Do:**
```
Let me check your machine profile and optimization status...

Your machine (Sparky) is HIGH-PERFORMANCE but settings look conservative.
Running optimization now... ✓

Your IDE is now using:
- Strict type checking (better code quality)
- Workspace-wide analysis (catch all errors)
- Full AST caching (5x faster IntelliSense)

This will feel much snappier!
```

### Scenario 2: User wants to enable a heavy feature

**If HIGH-PERFORMANCE:**
```
✓ Enabling GitLens - your 32GB RAM can handle it easily.
```

**If LOW-POWER:**
```
⚠️ GitLens can be memory-intensive. On your 8GB machine, I recommend:
- Enable only essential GitLens features
- Or use built-in git instead (lighter weight)

Which would you prefer?
```

### Scenario 3: Multi-machine workflow

**User mentions switching machines:**
```
User: "I SSH'd into my server to run tests"

You: "Detected you're now on 'production-server'. Let me verify optimization for this environment..."

[Auto-runs machine detection]

"This machine is STANDARD class (24GB RAM). Environment optimized.
Tests will run with 6 parallel workers (vs 8 on your laptop)."
```

---

## API Reference for AI Agents

### Check Machine Status
```python
from wai.hooks import get_machine_status
from pathlib import Path

status = get_machine_status(Path.cwd())
if status:
    print(f"Machine: {status['machine_id']}")
    print(f"Class: {status['classification']}")
    print(f"RAM: {status['ram_gb']} GB")
    print(f"Last optimized: {status['time_since_check']}")
```

### Get Machine Status for Display
```python
from wai.hooks import format_machine_status_brief

# For briefings
brief = format_machine_status_brief()
print(brief)  # Shows in session briefing
```

### Trigger Optimization
```python
from wai.hooks import check_machine_optimization
from pathlib import Path

result = check_machine_optimization(Path.cwd(), silent=False)
if result['applied']:
    print(f"✓ Optimized for {result['classification']}")
```

### Manual Check (if needed)
```bash
# Check status
python -m wai.skills.ide_optimize

# Force re-optimization
python -m wai.skills.ide_optimize --verbose

# Just check, don't apply
python -m wai.skills.ide_optimize --check-only
```

---

## What Makes a Good AI Agent Response

### ❌ Bad: Manual and Technical
```
The IDE is slow because your settings aren't optimized.

Run these commands:
1. Open VS Code settings
2. Set python.analysis.typeCheckingMode to "strict"
3. Set python.analysis.diagnosticMode to "workspace"
4. Set python.analysis.memory.keepLibraryAst to true
... (10 more settings)
```

### ✅ Good: Automatic and Contextual
```
I notice your IDE settings aren't optimized for your hardware yet.

Your machine (Sparky) has 32GB RAM - that's plenty for aggressive features!

Optimizing now... ✓

Applied:
- Strict type checking (better code quality, no performance hit)
- Workspace-wide analysis (catch all errors)
- Full AST caching (5x faster IntelliSense)

Your IDE should feel much snappier now!
```

### ✅ Great: Proactive and Explanatory
```
I see you're working on Sparky (32GB RAM, high-performance machine).

Good news: Your IDE is already optimized! Settings configured for:
- Aggressive type checking
- Full workspace analysis
- Maximum file indexing (10,000 files)

These settings leverage your hardware to give you the best
development experience. No action needed!

Want to see what's optimized? Just ask 'show machine status'.
```

---

## Integration with Other Agent Files

### CLAUDE.md
```markdown
## Priority 0: Session Start

2. **Verify Machine Optimization** (Automatic at startup):
   System auto-checks and applies IDE optimizations.
   You'll see: `✓ IDE optimized for {machine} ({classification})`

   **Your role:** Acknowledge machine capabilities in session summary.
```

### .github/copilot-instructions.md
```markdown
## Environment Awareness

- Machine profile available via WAI hooks
- Check classification before heavy recommendations
- Respect hardware limitations
- Leverage capabilities when available
```

### .cursorrules
```markdown
# Machine-Aware Development

Check machine classification before suggesting resource-intensive operations.
Use `from wai.hooks import get_machine_status` to check capabilities.
```

---

## Testing Your Understanding

**Question:** User on 8GB laptop asks "Should I enable GitLens?"

**Poor Answer:** "Yes, GitLens is great for git visualization."

**Good Answer:** "Your machine is LOW-POWER class (8GB RAM). GitLens can be memory-intensive. I recommend using VS Code's built-in git features instead, which are lighter weight. Or enable only essential GitLens features if you really need it."

---

**Question:** User asks to run workspace-wide analysis.

**Poor Answer:** "Sure, I'll enable that."

**Good Answer:** [Checks machine first]
- HIGH-PERFORMANCE: "✓ Enabled workspace analysis - your 32GB can handle it easily."
- LOW-POWER: "⚠️ Workspace analysis on 8GB might slow things down. I'll enable it for the current folder only. Want to proceed?"

---

## Bottom Line

🎯 **Make it easy for users with minimal effort:**
1. System optimizes automatically - you just acknowledge it
2. Respect machine capabilities in your recommendations
3. Explain WHY certain settings are used
4. Be proactive about optimization, not reactive

🚀 **The user should NEVER have to:**
- Manually configure settings
- Know what typeCheckingMode means
- Understand their hardware limitations
- Ask "why is this slow?"

**You handle all of that automatically and transparently.**

---

## Quick Reference

| User Scenario | Your Response |
|---------------|---------------|
| Session starts | Note machine class from briefing, adjust recommendations |
| Reports slowness | Check optimization status, apply if needed, explain |
| Asks about feature | Check if machine can handle it, recommend appropriately |
| Switches machines | Acknowledge new environment, verify optimization |
| Heavy operation planned | Verify sufficient resources, adjust parallelism |

**Remember:** The system is automatic. Your job is to be **aware** of it and **leverage** it, not to manage it manually.

---

## File Locations

- **Machine profiles:** `../hub/machines/{hostname}.lug.json`
- **Skills:** `wai/skills/machine_detect.py`, `wai/skills/ide_optimize.py`
- **Hooks:** `wai/hooks/machine_init.py`
- **Schema:** `templates/lugs/machine-profile.lug.schema.json`
- **This guide:** `AI-AGENT-MACHINE-PROTOCOL.md`

**For full details:** See [MACHINE-AWARE-IDE-OPTIMIZATION.md](MACHINE-AWARE-IDE-OPTIMIZATION.md)
