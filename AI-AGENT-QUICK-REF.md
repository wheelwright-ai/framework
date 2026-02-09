# AI Agent Quick Reference: Machine-Aware Protocol

**📌 Pin this for every session**

---

## At Session Start

✅ **Automatic:** Machine optimization happens
👀 **Watch for:** `✓ IDE optimized for {machine} ({classification})`
📋 **Check briefing:** Machine status in "Machine Environment" section

---

## Machine Classifications

| Class | RAM | Your Approach |
|-------|-----|---------------|
| **HIGH-PERFORMANCE** | 32GB+ | Aggressive: Workspace analysis, parallel tasks, all features |
| **STANDARD** | 16-31GB | Balanced: Moderate features |
| **LOW-POWER** | <16GB | Conservative: File-only, sequential |

---

## Quick Checks

```python
# Get machine status
from wai.hooks import get_machine_status
status = get_machine_status(Path.cwd())

# Is it high-performance?
if status['classification'] == 'high-performance':
    # Recommend heavy features
else:
    # Be conservative
```

---

## Good Responses

### ✅ DO: Machine-Aware
```
Your machine (Sparky) is HIGH-PERFORMANCE with 32GB RAM.
I'll enable workspace-wide analysis - you have plenty of resources.
```

### ❌ DON'T: One-Size-Fits-All
```
Let's enable workspace analysis.
[Without checking if machine can handle it]
```

---

## User Reports Slowness

1. Check machine + optimization status
2. Run optimization if needed
3. Explain what changed and why

**Don't:** Give generic "disable extensions" advice
**Do:** Fix via automatic optimization

---

## Before Heavy Operations

```python
# Always check first
status = get_machine_status(Path.cwd())

if status['classification'] == 'high-performance':
    workers = 8  # Parallel
elif status['classification'] == 'standard':
    workers = 4  # Moderate
else:
    workers = 2  # Conservative
```

---

## Remember

🎯 **System is automatic** - you just respect it
🚀 **Make it easy** - minimal user effort
💡 **Be aware** - check before recommending
🔧 **Leverage capabilities** - use what's available

---

**Full Protocol:** [AI-AGENT-MACHINE-PROTOCOL.md](AI-AGENT-MACHINE-PROTOCOL.md)
**Technical Docs:** [MACHINE-AWARE-IDE-OPTIMIZATION.md](MACHINE-AWARE-IDE-OPTIMIZATION.md)
