# 🎡 Wheelwright CLI Phase 1: WSL Menu Quick Start

**Primary Environment:** WSL (Ubuntu Terminal)  
**Status:** ✅ READY  
**Date:** 2026-02-08

---

## TL;DR - Just Run It!

```bash
cd /home/mario/projects/wheelwright-ai/framework

# Run with no arguments to get the interactive menu
python3 -m wai.cli.main

# Or use the wrapper
python3 WAI-CLI

# Or create an alias for easy access
alias wai="python3 /home/mario/projects/wheelwright-ai/framework/WAI-CLI"
wai
```

That's it! You'll see the interactive menu with wagon wheel animation.

---

## What You'll See

When you run with no arguments:

```
    ╔═════════════════════════════════╗
    ║                                 ║
    ║       WHEELWRIGHT AI            ║
    ║                                 ║
    ║    Build AI wheels that roll    ║
    ║    forward forever              ║
    ║                                 ║
    ║   [wagon wheel rolling...]      ║
    ║                                 ║
    ╚═════════════════════════════════╝


WHEELWRIGHT AI - Main Menu

  1/i - ✨ Initialize
  2/l - 📚 Learn
  3/t - 🎓 Teach
  4/s - 📊 Stats
  5/r - 📋 Review
  6/h - ❓ Help
  q/q - 👋 Quit

Select option [1]:
```

---

## Menu Navigation

### How to Select

| Action | Input |
|--------|-------|
| Initialize | `1` or `i` |
| Learn | `2` or `l` |
| Teach | `3` or `t` |
| Stats | `4` or `s` |
| Review | `5` or `r` |
| Help | `6` or `h` |
| Quit | `q` |
| Use Default | Just press `Enter` |

### Example Session

```bash
$ python3 -m wai.cli.main

[wagon wheel animation]

WHEELWRIGHT AI - Main Menu
...

Select option [1]: 1

Initialize - Choose Type

  1/h - 🏛️  Hub
  2/s - 💼 Spoke
  b/b - ⬅️  Back

Choose type [1]: 1

Initialize Hub

Enter hub name: MyHub
Enter description (optional): My central hub
Creating hub: MyHub
[wagon wheel rolling...]

✅ Hub created: MyHub

Select option [1]: q
👋 Goodbye!
```

---

## Permanent Setup for WSL

### Add Alias to ~/.bashrc

```bash
# Edit your bashrc
nano ~/.bashrc

# Add this line at the end
alias wai="python3 /home/mario/projects/wheelwright-ai/framework/WAI-CLI"

# Save (Ctrl+X, Y, Enter)

# Reload
source ~/.bashrc

# Now use it
wai
```

### Or Add to PATH

```bash
# Add framework to PATH
echo 'export PATH="/home/mario/projects/wheelwright-ai/framework:$PATH"' >> ~/.bashrc

# Reload
source ~/.bashrc

# Make WAI-CLI executable
chmod +x /home/mario/projects/wheelwright-ai/framework/WAI-CLI

# Now you can use from anywhere
wai
```

---

## Both Menu and Command-Line Work

### Interactive Menu (Default)
```bash
wai
# Shows menu, prompts for input
# Best for: Learning, interactive use
```

### Direct Commands (Power User)
```bash
wai init hub --name MyHub
wai learn spoke ProjectA --priority high
wai teach spoke ProjectA --json
wai stats spoke ProjectA
wai review spoke ProjectA
```

---

## Complete First-Time Workflow

```bash
# 1. Go to framework
cd /home/mario/projects/wheelwright-ai/framework

# 2. Run with no args to get menu
python3 -m wai.cli.main

# 3. Select: 1 (Initialize)
# 4. Select: 1 (Hub)
# 5. Enter name: MyHub
# 6. Enter description: (skip or enter)
# 7. Watch wagon wheel animation!
# 8. Hub created ✅

# 9. Back in menu, select: 1 (Initialize)
# 10. Select: 2 (Spoke)
# 11. Enter name: ProjectA
# 12. Enter description: (skip or enter)
# 13. Enter hub: MyHub
# 14. Spoke created ✅

# 15. Select: 2 (Learn)
# 16. Enter spoke: ProjectA
# 17. Select priority (press 2 for normal)
# 18. Watch wagon wheel animation!
# 19. Signals learned ✅

# 20. Select: 3 (Teach)
# 21. Enter spoke: ProjectA
# 22. Watch wagon wheel animation!
# 23. Templates pulled ✅

# 24. Select: 4 (Stats)
# 25. Enter spoke: ProjectA
# 26. Select format (1 for table)
# 27. See statistics ✅

# 28. Select: 5 (Review)
# 29. Enter spoke: ProjectA
# 30. See project review ✅

# 31. Select: q (Quit)
# 32. Done! 🎉
```

---

## Testing It Works

```bash
cd /home/mario/projects/wheelwright-ai/framework

# Run tests to verify everything works
pytest wai/cli/tests/ -v

# Expected: 140+ tests pass ✅

# Run the menu
python3 -m wai.cli.main

# Try each menu option:
# 1. Init (hub + spoke)
# 2. Learn
# 3. Teach
# 4. Stats
# 5. Review
# q. Quit
```

---

## Keyboard Input in WSL

The menu uses **safe keyboard input** that works in WSL:

✅ Number keys (1-5)  
✅ Letter keys (i, l, t, s, r, q)  
✅ Enter/Return  
✅ No special terminal modes required  
✅ Works with default terminal settings  

---

## Power User Mode (Skip Menu)

If you already know what you want:

```bash
# Init directly
python3 -m wai.cli.main init hub --name QuickHub

# Learn directly
python3 -m wai.cli.main learn spoke ProjectA --priority high --force

# Teach directly
python3 -m wai.cli.main teach spoke ProjectA --force

# Stats directly
python3 -m wai.cli.main stats spoke ProjectA --format json

# Review directly
python3 -m wai.cli.main review spoke ProjectA --deep
```

These **bypass the menu** and execute immediately. Good for:
- Scripting
- Automation
- CI/CD
- Batch operations

---

## Troubleshooting

### "command not found: wai"
→ Use full path: `python3 -m wai.cli.main`  
→ Or set up alias (see "Permanent Setup" above)

### "ModuleNotFoundError"
→ Make sure you're in the framework directory  
→ Or use: `python3 /home/mario/projects/wheelwright-ai/framework/WAI-CLI`

### "Permission denied" (if trying to execute WAI-CLI directly)
→ Make it executable: `chmod +x /home/mario/projects/wheelwright-ai/framework/WAI-CLI`  
→ Then run: `./WAI-CLI` or `/path/to/WAI-CLI`

### Menu not responding to input
→ Try pressing Enter after your choice  
→ WSL should work fine with standard input

---

## Files You Need to Know

| File | Purpose | Location |
|------|---------|----------|
| `WAI-CLI` | Main executable | `/home/mario/projects/wheelwright-ai/framework/WAI-CLI` |
| `main.py` | Entry point (with menu) | `wai/cli/main.py` |
| `state_manager.py` | Manages state | `wai/cli/lib/state_manager.py` |
| `wheel.py` | Wagon wheel animation | `wai/cli/visuals/wheel.py` |
| `formatter.py` | Output formatting | `wai/cli/visuals/formatter.py` |

---

## Next Steps

1. **Try the menu now:**
   ```bash
   cd /home/mario/projects/wheelwright-ai/framework
   python3 -m wai.cli.main
   ```

2. **Create an alias (optional but recommended):**
   ```bash
   echo 'alias wai="python3 /home/mario/projects/wheelwright-ai/framework/WAI-CLI"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Run tests to verify:**
   ```bash
   pytest wai/cli/tests/ -v
   ```

4. **Start building:**
   ```bash
   wai  # or python3 -m wai.cli.main
   ```

---

## Summary

✅ **Interactive menu** - Run with no args  
✅ **Command-line shortcuts** - Run with args  
✅ **Wagon wheel animation** - In both modes  
✅ **Full WSL support** - No terminal hacks needed  
✅ **Easy setup** - Just add alias to ~/.bashrc  

**You're ready to go!** 🎡

```bash
python3 -m wai.cli.main
```

Press `1` to initialize, or `q` to quit.
