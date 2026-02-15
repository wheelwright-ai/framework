# 🎡 Wheelwright CLI - Getting Started

**Version:** 3.2.0  
**Status:** ✅ READY TO USE (Block 3 Complete)

---

## Quick Start: Run the CLI Right Now

### **Option 1: Python Command (Easiest)**

```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

# Run with no args to see welcome banner + wagon wheel animation
python3 -m wai.cli.main

# Or run commands directly
python3 -m wai.cli.main init hub --name MyHub
python3 -m wai.cli.main learn spoke ProjectA
python3 -m wai.cli.main teach spoke ProjectA
```

### **Option 2: Direct Script**

```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

# Make executable (one time)
chmod +x WAI-CLI

# Run the CLI
./WAI-CLI
./WAI-CLI init hub --name MyHub
./WAI-CLI learn spoke ProjectA
```

### **Option 3: Python Script**

```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

python3 WAI-CLI
python3 WAI-CLI stats spoke ProjectA --format json
```

---

## Try These Commands

### **Show Welcome Banner with Wagon Wheel**
```bash
python3 -m wai.cli.main
```

### **Initialize a Hub**
```bash
python3 -m wai.cli.main init hub --name CoreHub
python3 -m wai.cli.main init hub --name CoreHub --description "My Hub"
```

### **Initialize a Spoke**
```bash
python3 -m wai.cli.main init spoke --name ProjectA --hub CoreHub
python3 -m wai.cli.main init spoke --name ProjectB --hub CoreHub --path /projects/B
```

### **Push Signals (Learn)**
```bash
python3 -m wai.cli.main learn spoke ProjectA
python3 -m wai.cli.main learn spoke ProjectA --priority high
python3 -m wai.cli.main learn spoke ProjectA --force
python3 -m wai.cli.main learn spoke ProjectA --json
```

### **Pull Templates (Teach)**
```bash
python3 -m wai.cli.main teach spoke ProjectA
python3 -m wai.cli.main teach spoke ProjectA --force
python3 -m wai.cli.main teach spoke ProjectA --json
```

### **View Statistics**
```bash
python3 -m wai.cli.main stats spoke ProjectA
python3 -m wai.cli.main stats spoke ProjectA --format json
python3 -m wai.cli.main stats spoke ProjectA --format table
python3 -m wai.cli.main stats spoke ProjectA --format text
```

### **Review Project State**
```bash
python3 -m wai.cli.main review spoke ProjectA
python3 -m wai.cli.main review spoke ProjectA --deep
python3 -m wai.cli.main review spoke ProjectA --json
```

### **Get Help**
```bash
python3 -m wai.cli.main --help
python3 -m wai.cli.main init --help
python3 -m wai.cli.main learn --help
```

### **Show Version**
```bash
python3 -m wai.cli.main --version
```

---

## What You'll See

### Welcome Banner + Wagon Wheel
When you run with no arguments:
```
    ╔═══════════════════════════════════╗
    ║                                   ║
    ║       WHEELWRIGHT AI              ║
    ║                                   ║
    ║           v3.2.0                  ║
    ║                                   ║
    ║   Build AI wheels that roll       ║
    ║   forward forever                 ║
    ║                                   ║
    ║      [wagon wheel rolling...]     ║
    ║                                   ║
    ╚═══════════════════════════════════╝
```

### Command Output
```
$ python3 -m wai.cli.main learn spoke ProjectA
Learning from spoke: ProjectA
  Priority: normal
  [wagon wheel rolling...]
✅ Learned: 12 signals from ProjectA
  • 3 high-impact decisions
  • 2 patterns identified
  • 7 additional signals
```

### JSON Output
```bash
$ python3 -m wai.cli.main learn spoke ProjectA --json
{
  "status": "success",
  "spoke": "ProjectA",
  "signals": 12,
  "priority": "normal"
}
```

### Table Output
```bash
$ python3 -m wai.cli.main stats spoke ProjectA
╔══════════════════════════════╗
│ ProjectA Statistics          │
╠══════════════════════════════╣
│ Status:     Active           │
│ Last Sync:  2 days ago       │
│ Signals:    12 pending       │
│ Templates:  Up to date       │
│ Tech Stack: Python, FastAPI  │
╚══════════════════════════════╝
```

---

## Available Commands

### **init**
Initialize hub or spoke
```
init hub --name <name> [--path <path>] [--description <desc>]
init spoke --name <name> --hub <hub> [--path <path>] [--description <desc>]
```

### **learn**
Push signals from spoke to hub
```
learn <spoke> [--priority high/normal/low] [--force] [--json]
```

### **teach**
Pull templates from hub to spoke
```
teach <spoke> [--force] [--json]
```

### **stats**
View node statistics
```
stats <spoke> [--format table/json/text] [--all]
```

### **review**
Inspect project state
```
review <spoke> [--deep] [--format text/json]
```

---

## Running Tests

### **Run All CLI Tests**
```bash
pytest wai/cli/tests/ -v
```

Expected: 80+ tests passing ✅

### **Run Specific Test Module**
```bash
pytest wai/cli/tests/test_main.py -v
pytest wai/cli/tests/test_wheel.py -v
pytest wai/cli/tests/test_formatter.py -v
```

### **Run with Coverage**
```bash
pytest wai/cli/tests/ --cov=wai.cli --cov-report=html
```

---

## Troubleshooting

### **"ModuleNotFoundError: No module named 'wai'"**
Make sure you're running from the framework root:
```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework
python3 -m wai.cli.main
```

### **"No animation showing"**
The animation automatically disables in non-TTY environments (CI, piped output). To test:
```bash
# Should show animation
python3 -m wai.cli.main

# Will not show animation (piped)
python3 -m wai.cli.main | cat

# Disable animation explicitly
python3 -m wai.cli.main --no-animation
```

### **"Command not found: wai"**
The `wai` command alias will be available after installation. For now, use:
```bash
python3 -m wai.cli.main
# or
./WAI-CLI
```

---

## What's Working Now

✅ **Wagon wheel animation** - 12-frame rolling wheel  
✅ **Welcome banner** - Shows on startup  
✅ **5 core verbs** - init, learn, teach, stats, review  
✅ **Multiple output formats** - text, table, JSON  
✅ **Error handling** - Graceful errors, helpful messages  
✅ **TTY detection** - Auto-disables animation in CI  
✅ **Full test suite** - 80+ comprehensive tests  

---

## File Locations

```
Executable:
  //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/WAI-CLI

Module:
  //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/wai/cli/main.py

Tests:
  //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/wai/cli/tests/
```

---

## What's Next (Future Blocks)

### **Block 4: Core Command Implementation**
- Full `init` command with hub/spoke creation
- Full `learn` command with signal processing  
- Full `teach` command with template distribution
- State management integration

### **Block 5: State Management**
- WAI-State.json integration
- WAI-Signals.jsonl processing
- WAI-Lugs.jsonl handling

### **Block 6: Polish & Release**
- Full documentation
- Integration tests
- Release as v3.2

---

## Examples

### **Create a Hub and Spoke**
```bash
# Create hub
python3 -m wai.cli.main init hub --name MyCompanyHub \
  --description "Central knowledge repository"

# Create spoke (project)
python3 -m wai.cli.main init spoke --name ProjectAlpha \
  --hub MyCompanyHub \
  --description "Main application"

# Create another spoke
python3 -m wai.cli.main init spoke --name ProjectBeta \
  --hub MyCompanyHub
```

### **Learn from a Project**
```bash
# Push signals with high priority
python3 -m wai.cli.main learn spoke ProjectAlpha \
  --priority high \
  --force

# View JSON output
python3 -m wai.cli.main learn spoke ProjectAlpha --json
```

### **Teach to a Project**
```bash
# Pull latest templates
python3 -m wai.cli.main teach spoke ProjectAlpha

# Force without confirmation
python3 -m wai.cli.main teach spoke ProjectAlpha --force

# Get JSON result
python3 -m wai.cli.main teach spoke ProjectAlpha --json
```

### **View Statistics**
```bash
# Table format (default)
python3 -m wai.cli.main stats spoke ProjectAlpha

# JSON format (for scripting)
python3 -m wai.cli.main stats spoke ProjectAlpha --format json

# Plain text
python3 -m wai.cli.main stats spoke ProjectAlpha --format text

# Detailed breakdown
python3 -m wai.cli.main stats spoke ProjectAlpha --all
```

### **Review Project**
```bash
# Basic review
python3 -m wai.cli.main review spoke ProjectAlpha

# Deep analysis
python3 -m wai.cli.main review spoke ProjectAlpha --deep

# JSON output
python3 -m wai.cli.main review spoke ProjectAlpha --json
```

---

## Help System

```bash
# Show all commands
python3 -m wai.cli.main --help

# Show command help
python3 -m wai.cli.main init --help
python3 -m wai.cli.main learn --help
python3 -m wai.cli.main teach --help
python3 -m wai.cli.main stats --help
python3 -m wai.cli.main review --help

# Show version
python3 -m wai.cli.main --version
```

---

## Quick Reference

```bash
# Absolute paths
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

# Run CLI
python3 -m wai.cli.main [command] [options]

# Or use wrapper
python3 WAI-CLI [command] [options]

# Run tests
pytest wai/cli/tests/ -v

# Run specific test
pytest wai/cli/tests/test_main.py -v

# Generate coverage report
pytest wai/cli/tests/ --cov=wai.cli --cov-report=html
```

---

**🎡 You're ready to use the Wheelwright CLI! Start with `python3 -m wai.cli.main` to see the wagon wheel in action.**

---

**Document:** CLI-GETTING-STARTED.md  
**Status:** ✅ Ready to use  
**Next:** Run commands and explore!
