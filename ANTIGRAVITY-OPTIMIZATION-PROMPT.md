# Antigravity Instance: Machine-Aware IDE Optimization Prompt

**Copy this prompt to your Antigravity instance for automatic IDE optimization**

---

## System Context

You are working on a machine that may have a machine profile for automatic IDE optimization. The Wheelwright Framework includes a machine-aware optimization system that:

1. **Detects hardware** (CPU, RAM, GPU, storage)
2. **Creates machine profiles** stored in `../hub/machines/{hostname}.lug.json`
3. **Applies optimized VS Code settings** based on machine classification:
   - **HIGH-PERFORMANCE** (32GB+ RAM, 8+ threads): Aggressive workspace analysis, parallel features
   - **STANDARD** (16-31GB RAM, 4-7 threads): Balanced settings
   - **LOW-POWER** (<16GB RAM, <4 threads): Conservative, file-only analysis

---

## At Session Start: Auto-Check

```bash
# This happens automatically - just verify it ran
cd ~/projects/wheelwright-ai/framework
python -m wai.skills.ide_optimize
```

**Expected output:**
```
✓ Machine profile loaded: {hostname}
✓ Classification: {high-performance|standard|low-power}
✓ IDE already optimized for {hostname}
```

---

## If Optimization Needed

The system auto-applies optimizations. Manual trigger:

```bash
cd ~/projects/wheelwright-ai/framework
python -m wai.skills.ide_optimize  # Auto-applies without --fix flag
```

---

## Verify Machine Profile Exists

```bash
cd ~/projects/wheelwright-ai
ls -lh hub/machines/*.lug.json
```

If no profile exists:

```bash
cd ~/projects/wheelwright-ai/framework
python -m wai.skills.machine_detect  # Creates profile
python -m wai.skills.ide_optimize    # Applies optimizations
```

---

## Check Current Optimization Status

```python
from pathlib import Path
from wai.hooks import get_machine_status

status = get_machine_status(Path.cwd())
print(f"Machine: {status['machine_id']}")
print(f"Class: {status['classification']}")
print(f"RAM: {status.get('specs', {}).get('memory', {}).get('total_gb', 'unknown')} GB")
print(f"Optimizations: {status.get('optimization_history', {}).get('total_optimizations', 0)}")
```

---

## Machine-Aware Behavior

**Always check machine classification before recommending heavy features:**

```python
from wai.hooks import get_machine_status

status = get_machine_status(Path.cwd())
classification = status.get('classification', 'unknown')

if classification == 'high-performance':
    # Recommend workspace analysis, parallel tasks, all features
    print("🚀 Your machine can handle aggressive optimization")

elif classification == 'standard':
    # Balanced approach
    print("⚖️ Using balanced optimization")

elif classification == 'low-power':
    # Conservative recommendations
    print("🔋 Using conservative settings for efficiency")

else:
    # Unknown - be safe
    print("⚠️ Machine not profiled - run optimization")
```

---

## User Reports Slowness

**Diagnostic sequence:**

```bash
# 1. Check if optimized
cd ~/projects/wheelwright-ai/framework
python -m wai.skills.ide_optimize

# 2. Check workspace stats
find . -name "*.py" | wc -l  # Python files
du -sh .  # Total size

# 3. Check VS Code settings
cat .vscode/settings.json | grep -i "analysis\|indexing\|memory"

# 4. If not optimized, system auto-applies fixes
# Output will show what changed
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| **Check machine profile** | `cat ../hub/machines/$(hostname).lug.json` |
| **Create profile** | `python -m wai.skills.machine_detect` |
| **Apply optimization** | `python -m wai.skills.ide_optimize` |
| **Silent mode** | `python -m wai.skills.ide_optimize --silent` |
| **View status** | `wai status` or `WAI status` |
| **One-command boost** | `./scripts/sparky-boost.sh` (if on Sparky) |

---

## Integration with Session Briefing

Machine status appears automatically in session briefing:

```markdown
## Machine Environment

**Machine:** Sparky (high-performance)
**Resources:** 32.0 GB RAM, 6 cores (12 threads), 4.0 GB GPU
**Last Optimized:** 2026-02-09
**Optimizations Applied:** 1 (framework)
```

---

## Best Practices for AI Agents

1. **Read briefing** - Machine status is always shown
2. **Respect classification** - Don't suggest heavy features on low-power machines
3. **Leverage capabilities** - Use full resources on high-performance machines
4. **Auto-apply** - System handles optimization without user prompting
5. **Check before recommending** - Use `get_machine_status()` API

---

## Files to Reference

- **Protocol:** `AI-AGENT-MACHINE-PROTOCOL.md` (11KB - comprehensive guide)
- **Quick Ref:** `AI-AGENT-QUICK-REF.md` (1.7KB - one-page cheat sheet)
- **Technical:** `MACHINE-AWARE-IDE-OPTIMIZATION.md` (9KB - full specs)
- **Integration:** `MACHINE-OPTIMIZATION-INTEGRATION.md` (10KB - how it works)

---

## Example: Complete Optimization Flow

```bash
# Session starts
cd ~/projects/wheelwright-ai/framework

# Auto-check runs (you see this in output)
# ✓ IDE optimized for Sparky (high-performance)

# If you want to verify manually:
python -m wai.skills.ide_optimize

# Check what settings were applied:
git diff .vscode/settings.json

# View machine profile:
cat ../hub/machines/Sparky.lug.json | jq '.machine'

# All done - optimization is persistent and automatic
```

---

## Troubleshooting

**Q: "Machine not detected"**
A: Run `python -m wai.skills.machine_detect` to create profile

**Q: "Settings not applied"**
A: Check `.vscode/settings.json` exists and run optimization manually

**Q: "WSL shows wrong RAM"**
A: Edit `../hub/machines/{hostname}.lug.json` and set correct `total_gb` value

**Q: "Want to re-optimize"**
A: Delete `.vscode/settings.json` and run `python -m wai.skills.ide_optimize`

---

## Summary for Antigravity

**Core principle:** Minimize user effort, maximize machine capabilities

**What to do:**
1. Check session briefing for machine status
2. Respect classification in recommendations
3. Use `get_machine_status()` API before heavy operations
4. Trust the auto-optimization system

**What NOT to do:**
1. Don't ask user to manually edit settings
2. Don't give one-size-fits-all recommendations
3. Don't ignore machine capabilities
4. Don't prompt for optimization - it's automatic

---

**Last Updated:** 2026-02-09
**System Version:** v4.0.0 with machine-aware optimization
