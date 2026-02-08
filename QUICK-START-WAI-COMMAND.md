# 🎡 Quick Start: Using the `wai` Command

You're on Windows/WSL. Here are the easiest ways to use the CLI:

---

## ⚡ Fastest Way (Right Now!)

### From PowerShell:
```powershell
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

# Option A: Direct Python (works immediately)
python3 -m wai.cli.main --help
python3 -m wai.cli.main init hub --name MyHub

# Option B: Using wrapper script
.\wai.ps1 --help
.\wai.ps1 init hub --name MyHub

# Option C: Using batch file
wai.bat --help
wai.bat init hub --name MyHub
```

### From WSL Terminal (Ubuntu):
```bash
cd /home/mario/projects/wheelwright-ai/framework

# Option A: Direct Python
python3 -m wai.cli.main --help

# Option B: Using wrapper script
python3 WAI-CLI --help

# Option C: Create alias
alias wai="python3 $PWD/WAI-CLI"
wai --help

# Option D: Add to PATH
export PATH="$PATH:$PWD"
wai --help  # Won't work unless WAI-CLI is executable (chmod +x)
```

---

## 📝 Add Permanent Alias (Recommended)

### PowerShell (Windows):

**Option 1: Add to Session (Lasts until you close PowerShell)**
```powershell
Set-Alias wai "python3 //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/wai.ps1"

# Now use it
wai --help
wai init hub --name MyHub
```

**Option 2: Add to Profile (Permanent)**
```powershell
# Open your PowerShell profile
code $PROFILE

# Add this line
Set-Alias wai "python3 $env:USERPROFILE\path\to\wai.ps1"

# Save and restart PowerShell
```

---

## 🎯 Best Setup for Your Windows/WSL

Since you have both Windows and WSL, I recommend:

### For Windows (PowerShell):
```powershell
# Add this to your PowerShell profile ($PROFILE):
Set-Alias wai 'python3 //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/WAI-CLI'

# Now use it globally
wai --help
wai init hub --name MyHub
```

### For WSL (Ubuntu Terminal):
```bash
# Add to ~/.bashrc:
alias wai="python3 /home/mario/projects/wheelwright-ai/framework/WAI-CLI"

# Reload
source ~/.bashrc

# Now use it
wai --help
```

---

## 📍 File Locations & What They Do

| File | Purpose | Platform |
|------|---------|----------|
| `WAI-CLI` | Main executable (Python) | All |
| `wai.bat` | Batch wrapper | Windows |
| `wai.ps1` | PowerShell wrapper | Windows/PowerShell |
| `python3 -m wai.cli.main` | Direct Python call | All |

---

## 🚀 Quick Commands

### Initialize
```powershell
wai init hub --name CoreHub
wai init spoke --name ProjectA --hub CoreHub
```

### Learn (Push Signals)
```powershell
wai learn spoke ProjectA
wai learn spoke ProjectA --priority high
wai learn spoke ProjectA --json
```

### Teach (Pull Templates)
```powershell
wai teach spoke ProjectA
wai teach spoke ProjectA --force
wai teach spoke ProjectA --json
```

### Stats & Review
```powershell
wai stats spoke ProjectA
wai stats spoke ProjectA --format json
wai review spoke ProjectA
wai review spoke ProjectA --deep
```

### Help
```powershell
wai --help
wai init --help
wai learn --help
```

---

## ✨ No Setup Option (Works Immediately)

Just use Python directly:

```powershell
python3 -m wai.cli.main --help
python3 -m wai.cli.main init hub --name MyHub
python3 -m wai.cli.main learn spoke ProjectA
```

**This requires NO aliases, NO PATH changes, NO setup.**

---

## 🔄 Switch Between Methods

All of these work (pick your favorite):

```powershell
# Method 1: Direct Python
python3 -m wai.cli.main init hub --name MyHub

# Method 2: Python with wrapper
python3 WAI-CLI init hub --name MyHub

# Method 3: Batch file
wai.bat init hub --name MyHub

# Method 4: PowerShell wrapper
.\wai.ps1 init hub --name MyHub

# Method 5: Alias (if set up)
wai init hub --name MyHub
```

---

## 📋 Recommended Setup Steps

### Step 1: Verify It Works
```powershell
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework
python3 -m wai.cli.main --help
```

### Step 2: Create Easy Alias
Open PowerShell and run:
```powershell
$profileDir = Split-Path $PROFILE
if (!(Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force }

# Add alias to profile
Add-Content $PROFILE "Set-Alias wai 'python3 //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/WAI-CLI'"

# Reload profile
. $PROFILE
```

### Step 3: Test
```powershell
wai --help
```

---

## 🎡 You're Ready!

Pick your preferred method above and start using the CLI:

```powershell
wai init hub --name MyHub
wai init spoke --name ProjectA --hub MyHub
wai learn spoke ProjectA
wai teach spoke ProjectA
```

---

## 🐛 Troubleshooting

### "wai: The term 'wai' is not recognized"
→ Use full path: `python3 -m wai.cli.main --help`
→ Or create alias (see Step 2 above)

### "ModuleNotFoundError: No module named 'wai'"
→ Make sure you're in the framework directory
→ Or use full path: `python3 //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/WAI-CLI`

### "Python was not found"
→ You need Python 3.8+
→ Install: `winget install Python.Python.3.11` (Windows)
→ Or: `sudo apt install python3-pip` (WSL)

---

## 📚 Next Steps

1. **Run the tests:**
   ```powershell
   pytest wai/cli/tests/ -v
   ```

2. **Read documentation:**
   - `PHASE1-QUICK-REFERENCE.md` (5 min)
   - `CLI-GETTING-STARTED.md` (20 min)
   - `PHASE1-DOCUMENTATION-INDEX.md` (navigation)

3. **Start building:**
   ```powershell
   wai init hub --name MyHub
   ```

---

**Choose one method above and start using `wai`!** 🎡

**Simplest:** `python3 -m wai.cli.main <command>`  
**Easiest:** Create the PowerShell alias (see Step 2)  
**Fastest:** `wai <command>` after setup
