# Wheelwright Framework

**Build AI wheels that roll forward forever.**

Your hub remembers everything. Your spokes extend your capabilities.
Every turn makes your wheel smarter.

Works with ChatGPT, Claude, Gemini - any AI you use.

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> *"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

---

## What is Wheelwright?

Wheelwright gives your AI assistants **perfect memory** across all your development sessions. Never lose context, never repeat explanations, always stay in flow.

### The Wheel Metaphor

- **Hub** = Your central memory and consolidated knowledge
- **Spokes** = Specialized capabilities (analysis, consultation, code review)
- **Wheels** = Individual project contexts that roll forward
- **Rolling** = Each session moves forward, never losing ground

### Key Features

- **Hub Memory** - Your wheel's hub remembers every decision, every insight, every pattern you've discovered
- **Extensible Spokes** - Add capabilities: meta-consultation, document analysis, code review, and more
- **Works Everywhere** - ChatGPT, Claude, Gemini, Copilot - your wheel rolls across all platforms
- **Beyond Code** - Write books, develop strategies, build products. Wheelwright is your universal AI partner

---

## Quick Start

### Installation

```bash
# Clone the framework
git clone https://github.com/wheelwright-ai/framework.git wheelwright
cd wheelwright

# Make the CLI executable
chmod +x wwai

# Optional: Add to PATH
echo 'export PATH="$PATH:$(pwd)"' >> ~/.bashrc
source ~/.bashrc
```

### Initialize Your First Wheel

```bash
# Navigate to your project
cd ~/projects/my-awesome-project

# Initialize Wheelwright
wwai init

# Or with the full path
wwai init ~/projects/my-awesome-project
```

This creates a `.wwai/` directory with:
- `WWAI-State.json` - Machine-readable project state
- `WWAI-State.md` - Human-readable strategic context
- `WWAI-Guide.md` - Instructions for AI assistants
- `wheel-signals.jsonl` - High-impact learnings
- `kb-sync.json` - Hub synchronization status

### Create a Hub (for multiple projects)

```bash
# Create your personal hub
wwai hub create

# Or specify a location
wwai hub create ~/wheelwright-hub
```

---

## Usage

### Basic Commands

```bash
wwai init [path]           # Initialize a new wheel
wwai status                # Show current wheel state
wwai sync                  # Sync with hub
wwai closeout              # Generate closeout for session end
wwai context               # Output context for LLM paste
```

### Hub Commands

```bash
wwai hub create            # Create a new hub
wwai hub status            # Show hub health
wwai hub locate            # Find hub location
wwai projects scan         # Discover existing projects
wwai sync --all            # Sync all wheels
```

### Spoke Commands

```bash
wwai spoke list            # List available spokes
wwai spoke add <name>      # Add a spoke to current wheel
wwai spoke remove <name>   # Remove a spoke
```

---

## How It Works

### 1. Initialize Your Wheel

When you run `wwai init`, the framework creates context files that AI assistants can read. These files contain:

- **Project foundation** - Identity, boundaries, approach
- **Session state** - Who worked last, what changed
- **Decisions log** - Important choices and rationale
- **Evolution log** - How the project direction has changed

### 2. Work with AI

Start any AI session by sharing your wheel context:

```bash
# Copy context to clipboard
wwai context | pbcopy  # macOS
wwai context | xclip   # Linux
```

Or point your AI to the `.wwai/` directory directly.

### 3. Session Continuity

During your session, the AI updates the state files. Built-in commands:

| Command | Response |
|---------|----------|
| `'Time'` | Token usage estimate with 80% capacity warnings |
| `'Rules'` | List active guidelines and project protocols |
| `'Closeout'` | Generate updated WWAI-State files for session end |

### 4. Hub Learning

High-impact learnings (impact >= 8) flow to your hub, benefiting all your projects:

```
Your Wheel → wheel-signals.jsonl → Hub → Other Wheels
```

---

## Project Structure

```
your-project/
├── .wwai/                    # Wheelwright directory
│   ├── WWAI-State.json       # Machine state
│   ├── WWAI-State.md         # Strategic state
│   ├── WWAI-Guide.md         # AI instructions
│   ├── wheel-signals.jsonl   # High-impact learnings
│   └── kb-sync.json          # Hub sync status
└── ... your project files
```

### Hub Structure

```
wheelwright-hub/
├── .wwai/                    # Hub's own state
├── .wwai-registry/           # Wheel tracking
│   ├── wheels/               # Individual wheel metadata
│   └── wheel-projects.json   # Registry
├── hub-profile.json          # Your preferences
└── learnings/                # Cross-project patterns
    ├── ide/                  # IDE configurations
    ├── languages/            # Language-specific
    └── workflows/            # Workflow patterns
```

---

## Universal Application

Wheelwright isn't just for code. Build wheels for:

- **Writing** - Books, articles, documentation
- **Research** - Papers, analysis, investigations
- **Strategy** - Business plans, roadmaps, decisions
- **Design** - UI/UX, architecture, systems
- **Any project** requiring sustained AI context

---

## Configuration

### Environment Variables

```bash
WHEELWRIGHT_HUB_PATH=~/wheelwright-hub    # Hub location
WHEELWRIGHT_FRAMEWORK_PATH=~/wheelwright   # Framework location
WHEELWRIGHT_AUTO_SYNC=true                 # Auto-sync on changes
```

### Hub Profile

Customize `hub-profile.json` for personalized AI interactions:

```json
{
  "work_style": {
    "preferred_ais": ["Claude", "GitHub Copilot"],
    "coding_preferences": {
      "languages": ["Python", "TypeScript"],
      "patterns": ["functional", "clean-code"]
    }
  }
}
```

---

## Philosophy

### AI as Responsible Partner

Wheelwright implements **stewardship philosophy**:

> AI should enable but remain intentful. When work strays from the established
> foundation, the AI should flag it and require explicit acknowledgment.

### Behaviors

1. **Detect scope drift** - Flag before enabling work outside boundaries
2. **Require acknowledgment** - Direction changes need explicit approval
3. **Complete foundation first** - Guide setup before diving into work
4. **Prefer verification** - "Are you sure?" over silent compliance

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/wheelwright-ai/framework.git
cd wheelwright

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

---

## Roadmap

- [ ] VS Code extension
- [ ] Browser extension for web LLMs
- [ ] Cloud sync (wheelwright.cloud)
- [ ] Spoke marketplace
- [ ] Enterprise features

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Credits

Wheelwright Framework was originally developed as the Session Continuity Framework (SCF).

Created by **Mario Vaccari**

[wheelwright.ai](https://wheelwright.ai) | [GitHub](https://github.com/wheelwright-ai)

---

*Roll forward. Never lose ground.*
