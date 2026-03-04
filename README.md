# Wheelwright Framework

**AI session continuity through skills and lugs.**

Your AI picks up exactly where you left off — every session, every project, any model.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Is Wheelwright?

Wheelwright gives AI assistants **persistent memory** across sessions using two primitives:

- **Skills** — Markdown files that define agent behavior (how to start, close out, track work)
- **Lugs** — JSONL entries that carry work items, decisions, and signals across sessions

No Python. No database. No server. Just files the agent reads.

---

## Architecture

```
Framework (this repo)         Hub (your hub project)        Spoke (your project)
┌─────────────────────┐       ┌──────────────────────┐      ┌──────────────────────┐
│  templates/         │       │  WAI-Spoke/           │      │  WAI-Spoke/           │
│    commands/        │──────▶│  templates/commands/  │─────▶│  templates/commands/  │
│    spoke/           │  teach│  hub-profile.json     │teach │  WAI-State.json       │
│    HUB/             │       │                       │      │  WAI-Lugs.jsonl       │
│  WAI-Spoke/         │       └──────────────────────┘      └──────────────────────┘
│  (framework spoke)  │
└─────────────────────┘
```

**Hub** distributes skills and lugs to **spokes**. Spokes signal high-impact learnings back.

- **Framework** = this repo (source of truth for templates)
- **Hub** = your centralized registry (distributes upgrades, collects signals)
- **Spoke** = any project using WAI (`WAI-Spoke/` directory)
- **Teach** = PUSH (sender-initiated: hub → spoke, or spoke → hub)
- **Learn** = PULL (automatic on wakeup: each node processes its inbox)

---

## How Sessions Work

Every AI session follows the same protocol:

```
Session Start (/wai)
    ↓
Agent reads WAI-State.json, WAI-Lugs.jsonl, WAI-State.md
    ↓
Processes inbox (auto-learns pending teachings or lugs)
    ↓
Shows briefing: project identity, active work, context health
    ↓
--- work happens ---
    ↓
Session End (/wai-closeout or /wai-shipit)
    ↓
Agent reconciles autosaves → session-summary lug
Extracts high-impact signals (impact >= 8)
Updates WAI-State.json with session metadata
```

**The agent does this automatically** via hooks (Claude Code) or manual `/wai` (Gemini/other).

---

## File Structure

### Spoke (`WAI-Spoke/`)

```
WAI-Spoke/
├── WAI-State.json          # Project identity, phase, session metadata
├── WAI-State.md            # Strategic vision (human-readable)
├── WAI-Lugs.jsonl          # Work items, signals, decisions (append-only)
├── WAI-Signals.jsonl       # High-impact learnings (impact >= 8)
├── templates/commands/     # Skills (same as framework templates/commands/)
├── lugs/
│   ├── inbox/              # Incoming lugs from hub (auto-processed on wakeup)
│   └── outbox/             # Lugs staged for delivery to hub
├── seed/
│   └── ingest/             # Teaching files (.teaching) staged for adoption
├── sessions/               # Session logs
└── reference/
    ├── auto/               # Auto-generated reference files
    └── manual/             # Files requiring user review before use
```

### Hub (`templates/HUB/`)

```
hub/
├── WAI-Spoke/              # Hub's own spoke
├── hub-profile.json        # Hub identity, fingerprint for HMAC signing
├── hub-registry.json       # Registered spokes
└── wheel-projects.json     # Project registry
```

---

## Skills (Behavioral Protocols)

Skills are markdown files in `templates/commands/`. They define what the agent does.

| Skill | Command | Purpose |
|-------|---------|---------|
| `wai.md` | `/wai` | Wakeup — produces full WAI Point briefing |
| `wai-closeout.md` | `/wai-closeout` | Session end — reconcile, signal, commit |
| `wai-shipit.md` | `/wai-shipit` | Quality gates + closeout + commit |
| `wai-teach.md` | `/wai-teach` | Push templates/lugs to target nodes |
| `wai-learn.md` | `/wai-learn` | Force recheck inbox (auto-runs on wakeup) |
| `wai-lug-advisor.md` | `/wai-lug-advisor` | Lug schema, lifecycle, authoring |
| `wai-foundation.md` | `/wai-foundation` | Project identity and boundaries |
| `wai-ide-setup.md` | `/wai-ide-setup` | Hook configuration for Claude/Gemini/Cursor |
| `wai-complexity-advisor.md` | `/wai-complexity-advisor` | Planning gate (2+ files OR 6+ steps) |
| `wai-rules.md` | `/wai-rules` | Project boundaries |
| `wai-principles.md` | `/wai-principles` | WAI principles P1-P9 |

Skills are the **authoritative source of truth**. All behavioral rules live there.

---

## Lugs (Persistent Memory)

Lugs are JSON objects in `WAI-Lugs.jsonl` (one per line, append-only).

```json
{
  "i": "4f1e687a652f",
  "ty": "task",
  "t": "Fix authentication timeout in session middleware",
  "s": "o",
  "ca": "2026-02-28T10:00:00Z",
  "gb": "claude-sonnet-4-6",
  "description": "Session timeout not being refreshed on user activity.",
  "priority": "high",
  "impact": 6
}
```

**Key fields:** `i`=id, `ty`=type, `t`=title, `s`=status (o/p/c/b), `ca`=created_at

**Types:** `task`, `bug`, `feature`, `signal`, `epic`, `autosave`, `session-summary`, `core-protocol`, `foundation`, `phone-home`

Lugs travel across sessions, models, and projects. They must be self-contained — no "see above" references.

---

## Quick Start: New Spoke

### Option A: Automatic Initialization (Recommended)

From an existing spoke or framework, run `/wai-teach` with a target directory:

```bash
# From any spoke or framework
/wai-teach /path/to/new-project

# Automatically:
# - Detects if target is a spoke
# - If not, copies templates/spoke/ and initializes
# - Configures WAI-State.json with smart defaults
# - Registers spoke in hub registry
```

**Benefit**: No manual configuration needed. Use `/wai-teach` to initialize any project as a spoke.

### Option B: Manual Initialization

```bash
cp -r /path/to/framework/templates/spoke/ your-project/WAI-Spoke/
```

### 2. Initialize WAI-State.json (manual only)

Edit `WAI-Spoke/WAI-State.json`:
- Set `wheel.name`, `wheel.one_liner`, `wheel.spoke_id`
- Set `foundation.scope.in_scope` and `out_of_scope`

### 3. Set up IDE hooks (manual only)

Follow the `/wai-ide-setup` skill (`templates/commands/wai-ide-setup.md`) to configure:
- `.claude/hooks/user-prompt-submit.sh` (Claude Code)
- `.claude/settings.json` hook registration

### 4. Start your first session (manual only)

Open Claude Code (or your AI tool) in the project directory.
The hook runs automatically and the agent produces the WAI Point briefing.

---

## Quick Start: New Hub

```bash
cp -r /path/to/framework/templates/HUB/ ~/my-hub/
```

Edit `hub-profile.json`:
- Set `hub_id`, `hub_name`, `hub_fingerprint` (used for HMAC signing)

Register spokes in `hub-registry.json`. Use `/wai-teach` to distribute skills/lugs to spokes.

---

## IDE Integration

### Claude Code (automatic)

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": ".*",
      "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit.sh"}]
    }]
  }
}
```

Hook detects new sessions, injects wakeup directive, and the agent follows `/wai`.

### Gemini / Other AI Tools

Add to `GEMINI.md` or equivalent:
```markdown
On session start: read templates/commands/wai.md and follow the wakeup protocol.
```

See `/wai-ide-setup` for Cursor, VS Code, and generic AI agent setup.

---

## Session Commands

```
/wai              — Unified wakeup briefing
/wai-closeout     — End session (reconcile, signal, update state)
/wai-shipit       — Quality gates + closeout + git commit
/wai-teach        — Push skills/lugs to hub or spoke
/wai-learn        — Force reprocess inbox
/wai-time         — Token usage estimate
/wai-rules        — Show project boundaries
```

---

## Hub-Spoke Communication

**Teach** = push (active, sender-initiated):
- Hub creates `upgrade-adoption-plan.json` + `.teaching` files
- Copies files to spoke's `seed/ingest/`
- Signs with `hub_fingerprint` (HMAC-SHA256)

**Learn** = pull (passive, automatic on wakeup):
- Agent scans `seed/ingest/` for `.teaching` files
- Runs verification ceremony (RECEIVE → SUMMARIZE → EXPLAIN → WAIT → PROCEED)
- Adopts approved teachings to `templates/commands/`
- Moves originals to `seed/ingest/processed/`

The inbox is a **mailroom** — lugs are routed and stored, never executed.

---

## No Python Required

The framework is pure template assets:
- **Skills** = `.md` files the agent reads
- **Lugs** = `.jsonl` files the agent reads and appends to
- **Hooks** = thin bash scripts (jq required for session detection)
- **Agent** = your AI (Claude, Gemini, Cursor, etc.)

There is no CLI, no runtime, no package to install.

---

## Repository Structure

```
framework/
├── templates/
│   ├── commands/       # Skills (distributed to hub and spokes)
│   ├── spoke/          # Spoke template (copy to start a new spoke)
│   ├── HUB/            # Hub template (copy to start a new hub)
│   ├── claude/         # Claude Code IDE config templates
│   ├── gemini/         # Gemini config templates
│   ├── cursor/         # Cursor config templates
│   └── ...
├── WAI-Spoke/          # This framework's own spoke
├── CLAUDE.md           # Thin pointer → wai.md
├── GEMINI.md           # Thin pointer → wai.md
└── LICENSE
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Credits

Created by **Mario Vaccari**

[GitHub](https://github.com/wheelwright-ai)

---

*Skills and lugs. Sessions that roll forward.*
