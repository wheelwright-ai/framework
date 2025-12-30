# Wheelwright Quickstart Guide

Get up and running with Wheelwright in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Git (optional, for cloning)

## Installation

```bash
# Clone the framework
git clone https://github.com/wheelwright-ai/framework.git wheelwright
cd wheelwright

# Make CLI executable
chmod +x WAI-CLI

# Add to PATH (optional)
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
source ~/.bashrc
```

## Quick Start

### 1. Initialize Your First Wheel

```bash
cd ~/projects/my-project
WAI-CLI init
```

This creates a `WAI-Spoke/` directory with:
- `WAI-State.json` - Machine-readable state
- `WAI-State.md` - Human-readable context
- `WAI-Guide.md` - AI instructions
- `WAI-Signals.jsonl` - Learning log
- `WAI-KB-Sync.json` - Hub sync status

### 2. Start an AI Session

Copy your wheel context to share with any AI:

```bash
WAI-CLI context | pbcopy  # macOS
WAI-CLI context | xclip   # Linux
```

Or simply tell your AI to read the `WAI-Spoke/` directory.

### 3. Work with Your AI Partner

During the session, use these commands:

| Command | What it does |
|---------|--------------|
| `'Time'` | Check token usage |
| `'Rules'` | List active guidelines |
| `'Closeout'` | Generate session summary |

### 4. Check Status

```bash
WAI-CLI status
```

## Creating a Hub (Optional)

If you work on multiple projects, create a hub:

```bash
WAI-CLI hub create
```

This enables:
- Cross-project learning
- Centralized preferences
- Shared patterns

## Next Steps

- Read the [full documentation](README.md)
- Explore [available spokes](SPOKES.md)
- Check out [examples](../examples/)

---

*Wheelwright Framework - wheelwright.ai*
