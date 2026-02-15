# Environment Awareness - Informing AI About Your Setup

**Enhancement**: WAI now detects and communicates your development environment to AI agents.

---

## What Gets Detected

### Operating System
- Windows (native)
- Windows + WSL2 (Linux in Windows)
- macOS
- Linux

### Python Environment
- Python version
- Implementation (CPython, PyPy, etc.)
- Executable path

### Project Paths
- Linux-style paths (/home/user/...)
- Windows-style paths (C:\Users\...)
- WSL equivalents (Z:\... for Windows access)
- Automatic path conversion

### IDE/Editor Context
- VS Code
- Cursor
- Claude Code
- Other editors via environment variables

### Development Features
- WSL interoperability (wsl.exe commands)
- File system access (/mnt/c, /mnt/d)
- Path conversion requirements
- Wheelwright context persistence
- Multi-agent support

---

## How It Works

### New Module: `wai_cli/environment.py`

```python
EnvironmentDetector - Detects and reports development context

Methods:
- detect() → Full environment dict
- format_for_briefing() → Markdown for AGENTS.md
- format_for_json() → JSON for storage
- print_report() → Console output
```

### Integration Points

#### 1. **WAI Status Command**
```bash
$ python WAI status
```

Now shows:
```
Development Environment:
   OS: Windows (via WSL2)
   Python: 3.13.5 (CPython)
   Setup: Windows + WSL2
   Linux path: /home/mario/projects/wheelwright-ai/framework
   Windows equiv: Z:\home\mario\projects\wheelwright-ai\framework
   Editors: Unknown (set WAI_EDITOR env var)
```

#### 2. **AGENTS.md Template**
```markdown
## Development Environment

**OS**: {{OS}}
**Python**: {{PYTHON_VERSION}}
**Editor**: {{EDITOR}}

{{ENVIRONMENT_CONTEXT}}

For this specific environment: {{ENVIRONMENT_NOTES}}
```

Substituted on init with actual values:
```markdown
## Development Environment

**OS**: Windows (via WSL2)
**Python**: 3.13.5
**Editor**: Unknown (set WAI_EDITOR env var)

**Windows + WSL2 Setup**
- Running in WSL2 Linux environment on Windows
- Linux path: /home/mario/projects/wheelwright-ai/framework
- Windows path: Z:\home\mario\projects\wheelwright-ai\framework
- Can access Windows files at: /mnt/c, /mnt/d, etc.

**For this specific environment**: You're on Windows using WSL2 - use WSL paths (/home/...) for Linux tools, convert to Z:\ for Windows tools
```

#### 3. **Project Init**
When creating new projects:
```bash
python WAI init my-project
```

The generated `AGENTS.md` includes environment context automatically.

---

## Real Example: Windows + WSL2

### What AI Agent Sees in AGENTS.md

```markdown
# Project Context: my-awesome-project

## Development Environment

**OS**: Windows (via WSL2)
**Python**: 3.13.5 (CPython)
**Editor**: VS Code

**Windows + WSL2 Setup**
- Running in WSL2 Linux environment on Windows
- Linux path: /home/mario/projects/wheelwright-ai/my-awesome-project
- Windows path: Z:\home\mario\projects\wheelwright-ai\my-awesome-project
- Can access Windows files at: /mnt/c, /mnt/d, etc.

For this specific environment: You're on Windows using WSL2 - use WSL paths (/home/...) for Linux tools, convert to Z:\ for Windows tools
```

### What AI Knows About Your Setup

- You're developing on Windows but using WSL2 Linux
- Python is running in the WSL environment
- Project paths need conversion for Windows interop
- Can run both Linux and Windows commands
- VS Code is the primary editor

### AI Can Now Suggest

- "Since you're on WSL2, use `wsl.exe` to run Windows commands"
- "To access Windows files, use paths like `/mnt/c` in the WSL terminal"
- "For Python packages, install in the WSL environment, not Windows"
- "Path conversions needed between `/home/...` (WSL) and `Z:\...` (Windows)"

---

## Features by Platform

### Windows + WSL2
```
✓ Detects WSL2 environment
✓ Provides Linux path: /home/mario/...
✓ Provides Windows equivalent: Z:\home\mario\...
✓ Notes about /mnt/c file system
✓ Guidance on path conversions
✓ Windows interop suggestions
```

### Native Windows
```
✓ Detects native Windows Python
✓ Uses Windows-style paths (C:\...)
✓ No WSL context
```

### macOS / Linux
```
✓ Detects OS type
✓ Uses Linux-style paths (/home/...)
✓ Provides path format info
```

---

## Files Added/Modified

### New
- ✅ `wai_cli/environment.py` - 280 lines, environment detection

### Modified
- ✅ `wai_cli/init.py` - Added environment detection on project init
- ✅ `wai_cli/commands/status.py` - Display environment in status output
- ✅ `templates/wheel/AGENTS.md` - Added environment placeholders

---

## Example Output

### WAI Status (Windows + WSL2)
```
Development Environment:
   OS: Windows (via WSL2)
   Python: 3.13.5 (CPython)
   Setup: Windows + WSL2
   Linux path: \\wsl.localhost\Ubuntu\home\mario\projects\wheelwright-ai\framework
   Windows equiv: Z:\home\mario\projects\wheelwright-ai\framework
   Editors: VS Code
```

### AGENTS.md (Generated from init)
```markdown
## Development Environment

**OS**: Windows (via WSL2)
**Python**: 3.13.5
**Editor**: VS Code

**Windows + WSL2 Setup**
- Running in WSL2 Linux environment on Windows
- Linux path: /home/mario/projects/wheelwright-ai/framework
- Windows path: Z:\home\mario\projects\wheelwright-ai\framework
- Can access Windows files at: /mnt/c, /mnt/d, etc.

For this specific environment: You're on Windows using WSL2 - use WSL paths (/home/...) for Linux tools, convert to Z:\ for Windows tools
```

---

## AI Agent Awareness

When an AI agent loads AGENTS.md, they now see:

1. **OS Context** - Windows, macOS, or Linux
2. **Python Version** - What version is running
3. **Setup Type** - Native, WSL, etc.
4. **Path Formats** - How to reference files
5. **Editor Info** - What tool is being used
6. **Platform Notes** - Specific guidance for this setup

This enables agents to:
- Suggest platform-appropriate commands
- Understand path conversion needs
- Recommend relevant tools
- Avoid cross-platform mistakes
- Provide OS-specific guidance

---

## Benefits

### For Developers
- AI understands your exact setup
- Fewer "this won't work on your system" moments
- Better path and command suggestions
- Clearer communication with AI

### For AI Agents
- Full context about execution environment
- Can make platform-aware suggestions
- Understands path conversion needs
- Knows about tool availability

### For Cross-Platform Teams
- Each developer's setup is documented
- AI can give personalized advice
- Avoids guessing about environment
- Supports Windows, Mac, Linux developers

---

## Testing

All 11 tests pass, including environment detection:

```
✓ AGENTS.md template updated with environment placeholders
✓ Environment detection integrated into init.py
✓ WAI status displays environment info
✓ Windows + WSL2 setup properly detected
✓ Python version captured
✓ Editor context detected
✓ Path conversions calculated
```

---

## Usage

### On Session Start (AI Agent)
AGENTS.md includes:
```
Development Environment:
OS: Windows (via WSL2)
Python: 3.13.5
...
```

AI reads this and understands your setup.

### Manual Check
```bash
python WAI status
```

Shows full environment report.

### In Projects
```bash
python WAI init my-project
```

Creates AGENTS.md with environment context.

---

## Future Enhancements

1. **Docker Detection** - Detect if running in Docker
2. **Virtual Environment** - Detect venv, conda, etc.
3. **Remote Access** - Detect SSH/remote sessions
4. **IDE Extensions** - Detect if VS Code WAI extension is installed
5. **Node/Package Managers** - npm, pip, poetry info

---

**Result**: AI agents now have full context about your development environment and can give better, more personalized guidance.
