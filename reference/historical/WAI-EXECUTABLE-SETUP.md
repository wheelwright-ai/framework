# 🎡 Setting Up the `wai` Command

You have two options to run the CLI as `wai` instead of `python3 -m wai.cli.main`:

---

## Option 1: Use the Executable Directly (Easiest)

The `WAI-CLI` file is already executable:

```bash
# Make it executable (one time)
chmod +x WAI-CLI

# Create symlink or alias
ln -s WAI-CLI wai

# Now you can use it
./wai --help
./wai init hub --name MyHub
```

Or from anywhere in the project:

```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework
./wai init hub --name MyHub
```

---

## Option 2: Add to PATH (Recommended)

### Step 1: Make WAI-CLI Executable
```bash
chmod +x WAI-CLI
```

### Step 2: Add to Your PATH

**For current session only:**
```bash
export PATH="//wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework:$PATH"
wai --help
```

**For permanent setup, add to ~/.bashrc:**
```bash
echo 'export PATH="//wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework:$PATH"' >> ~/.bashrc
source ~/.bashrc
wai --help
```

---

## Option 3: Create a Global Symlink (Advanced)

If you want `wai` available system-wide:

```bash
# Create symlink in /usr/local/bin
sudo ln -s //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework/WAI-CLI /usr/local/bin/wai

# Now use from anywhere
wai --help
wai init hub --name MyHub
```

---

## Verification

Once set up, verify it works:

```bash
# Should show help
wai --help

# Should show version
wai --version

# Should create hub
wai init hub --name TestHub

# Should show welcome banner with wagon wheel
wai
```

---

## Quick Setup Script

Run this once to set everything up:

```bash
#!/bin/bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework

# Make executable
chmod +x WAI-CLI

# Add to PATH for this session
export PATH="$PWD:$PATH"

# Test it
wai --help
```

Or save as `setup-wai.sh` and run:
```bash
bash setup-wai.sh
```

---

## Recommended: Option 1 (Simplest)

Just use `./wai` from the framework directory:

```bash
cd //wsl.localhost/Ubuntu/home/mario/projects/wheelwright-ai/framework
./wai init hub --name MyHub
./wai learn spoke ProjectA
./wai teach spoke ProjectA
```

This works immediately without any PATH manipulation.

---

## What's Inside

The `WAI-CLI` executable is a Python script that:
1. Finds the framework root
2. Adds it to Python's import path
3. Calls `wai.cli.main.main()`

It's lightweight (~20 lines) and has no external dependencies.

---

## Commands Available

Once `wai` is set up, use:

```bash
wai init hub --name <name>
wai init spoke --name <name> --hub <hub>
wai learn <spoke> [--priority high/normal/low] [--force] [--json]
wai teach <spoke> [--force] [--json]
wai stats <spoke> [--format table/json/text] [--all]
wai review <spoke> [--deep] [--format text/json]
wai --help
wai --version
```

---

## Troubleshooting

### "wai: command not found"
→ Run from the framework directory: `./wai --help`
→ Or add to PATH: `export PATH="$PWD:$PATH"`

### "Permission denied"
→ Make executable: `chmod +x WAI-CLI`

### "ModuleNotFoundError: No module named 'wai'"
→ Run from framework root directory
→ Or ensure framework root is in PYTHONPATH

---

**Choose Option 1 or 2 above, and you're ready to go!** 🎡
