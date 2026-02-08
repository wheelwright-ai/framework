# Gemini Integration Instructions for Wheelwright

**CRITICAL: This project uses Wheelwright for session continuity.**

**Multi-Agent Enabled**: WAI supports parallel work across multiple AI tools and machines. Each environment tracks its own session without collision.

---

## Priority 0: Session Start Protocol

When you first receive a message in this project directory, execute the session start protocol:

1. **Load WAI Context**:
   - Read `WAI-Spoke/WAI-AI-ONBOARDING.md` (AI quick start guide)
   - Read `WAI-Spoke/WAI-Guide.md` (full project instructions)
   - Read `WAI-Spoke/WAI-State.json` (project state, decisions)
   - Read `WAI-Spoke/WAI-State.md` (strategic vision)

2. **Check Environment Sessions**:
   - Scan `WAI-Spoke/sessions/` for other environment logs
   - Note if other AI tools/machines have recent activity
   - Your session tracked in `WAI-Spoke/sessions/gemini-{machine}.jsonl`

3. **Brief the User**:
   - Project name and summary
   - Last session info from WAI-State.json
   - Current environment (Gemini on {machine})
   - Other active environments if any

4. **Check Uncommitted Work**:
   - Run git status via bash
   - If uncommitted changes, ask if resuming previous session or starting fresh

5. **Check for Teachings**:
   - Look in `WAI-Spoke/seed/ingest/` for `*.teaching` files
   - If present, propose adoption plan before other work
   - See WAI-MERGE-PROTOCOLS.md for merge guidance

---

## Priority 1: AI Interaction Model

**CRITICAL: WAI Commands as Internal Directives**

WAI commands (like "WAI closeout", "WAI shipit") are **internal directives for you to interpret**, NOT shell commands to execute.

**DO NOT** run commands like:
```bash
# WRONG - Do not execute WAI as shell command
./WAI closeout
bash WAI verify-upgrade
```

**DO** interpret WAI commands as instructions:
```
User says: "WAI closeout"
You interpret: Execute closeout logic
  1. Extract high-impact signals from session
  2. Create lugs for decisions (impact >= 8)
  3. Update WAI-State.json
  4. Clear WAI-Session-Log.jsonl
  5. Present session summary
```

See **WAI-AI-ONBOARDING.md** for complete command reference.

---

## Priority 2: Lug System (Signal Storage)

**File:** `WAI-Spoke/WAI-Lugs.jsonl`

**NOT:** `wheel-signals.jsonl`, `WAI-Signals.jsonl`, or `signals.jsonl`

### When to Create Lugs:

Create lugs for high-impact signals:
- Decisions with impact >= 8
- New features or epics
- Architectural changes
- Policy updates
- Bugs discovered
- Learnings extracted

### Lug Format (JSONL):

```json
{"i":"unique-id","t":"Title","ty":"type","s":"status","status":"open","description":"Detailed description","priority":"high","impact":9,"value":9,"scope":"framework","tags":["tag1","tag2"],"created_at":"2026-02-06T16:00:00Z","blocks":[],"blocked_by":[]}
```

### Lug Types (`ty` field):

- `epic` - Large features or initiatives
- `feature` - Specific functionality
- `bug` - Issues to fix
- `signal` - Observations or recommendations
- `policy` - Behavioral rules
- `learning` - Extracted patterns
- `decision` - High-impact choices

### How to Write Lugs:

```bash
# Append to WAI-Lugs.jsonl (one lug per line)
cat >> WAI-Spoke/WAI-Lugs.jsonl << 'EOF'
{"i":"gemini-session-001","t":"Implement voice command routing","ty":"feature","s":"o","status":"open","description":"Add routing layer for voice commands to plugin system","priority":"high","impact":8,"value":9,"scope":"application","tags":["voice","plugins","routing"],"created_at":"2026-02-06T18:00:00Z","blocks":[],"blocked_by":[]}
EOF
```

**NEVER** create separate signal files. Always use `WAI-Lugs.jsonl`.

---

## Priority 3: Session Logging

**File:** `WAI-Spoke/WAI-Session-Log.jsonl`

Log every user and assistant turn to this file for closeout processing.

### Log Format:

```json
{"timestamp":"2026-02-06T18:00:00Z","role":"user","content":"Add logging to the formatter","turn":1}
{"timestamp":"2026-02-06T18:00:15Z","role":"assistant","content":"I'll add logging to the formatter...","turn":2}
```

### When to Log:

- Every user message received
- Every assistant response sent
- Cleared during WAI closeout

---

## Priority 4: WAI Commands

Commands work with or without `WAI` prefix:

| Command | What It Does |
|---------|--------------|
| **WAI** | Load context files, verify integration, brief user |
| **Status** | Show hub connection, sync age, session health |
| **Time** | Estimate token usage, warn if approaching limits |
| **Rules** | Display project identity, scope, constraints |
| **Closeout** | Extract signals, update state, clear session log |
| **Compact** | Summarize resolved discussions mid-session |
| **Shipit** | Closeout + commit WAI files + ask about push |
| **Teach** | Pull new learnings from hub into spoke |
| **Learn** | Push high-impact signals to hub |

If unsure whether a command like "Status" refers to WAI, ask: *"Did you mean WAI Status?"*

---

## Priority 5: Teaching Adoption

When teaching files appear in `WAI-Spoke/seed/ingest/`:

1. **Read manifest.json** for file list and metadata
2. **For each teaching file**:
   - Check `safe_to_auto_adopt` flag
   - If `true`: Copy to target location automatically
   - If `false`: Use WAI-MERGE-PROTOCOLS.md to merge carefully
3. **Update manifest status**: `pending_adoption` → `adopted`
4. **Create adoption lug** documenting changes
5. **Move teaching files** to `seed/ingest/processed/`

See **WAI-MERGE-PROTOCOLS.md** for detailed merge guidance.

---

## Project-Specific Context

Project name, goals, and current phase are in **WAI-State.json**.

Key files to load on session start:
- `WAI-Spoke/WAI-AI-ONBOARDING.md` - AI quick start
- `WAI-Spoke/WAI-Guide.md` - Full project instructions
- `WAI-Spoke/WAI-State.json` - Current project state
- `WAI-Spoke/WAI-State.md` - Strategic vision

---

## Gemini-Specific Features

### Gemini CLI Memories

Store Gemini-specific context in:
- `WAI-Spoke/seed/ingest/gemini-cli-memories.md`

This file can capture Gemini conversation context for future sessions.

### Multi-Tool Awareness

Check `WAI-Spoke/sessions/` for other AI tool sessions:
- `claude-code-{machine}.jsonl` - Claude Code sessions
- `gemini-cli-{machine}.jsonl` - Your sessions
- `cursor-{machine}.jsonl` - Cursor sessions

No session collision - you can work in parallel with other tools.

---

## Version Reference

See **WAI-VERSION-GUIDE.md** for details on version indicators.

Quick reference:
- `wheelwright.version` - Framework release (check for feature availability)
- `wheelwright.structure_version` - Directory layout version
- `upgrade_plan_version` - Teaching file schema version

---

## Common Patterns

### Pattern: Closeout
1. Review `WAI-Session-Log.jsonl` for high-impact signals
2. Create lugs for decisions with impact >= 8
3. Update `WAI-State.json` (last_session, last_closeout)
4. Clear `WAI-Session-Log.jsonl`
5. Present session summary

### Pattern: Shipit
1. Run closeout logic
2. `git add WAI-Spoke/`
3. `git commit -m "session summary"`
4. Ask user: "Push to remote? [y/n]"

### Pattern: Teaching Adoption
1. Read `WAI-Spoke/seed/ingest/manifest.json`
2. For each file:
   - `safe_to_auto_adopt: true` → Auto-copy
   - `safe_to_auto_adopt: false` → Careful merge (use WAI-MERGE-PROTOCOLS.md)
3. Create adoption lug
4. Move teaching files to `processed/`

---

## File Structure

```
WAI-Spoke/
├── WAI-AI-ONBOARDING.md      # AI quick start (load always)
├── WAI-Guide.md              # Full instructions (load always)
├── WAI-State.json            # Project state (load always)
├── WAI-State.md              # Strategic vision (load always)
├── WAI-Lugs.jsonl            # Signal storage (append-only)
├── WAI-Session-Log.jsonl     # Current session turns
├── WAI-File-Index.json       # File metadata
├── reference/                # Knowledge base
│   ├── auto/                 # Hub-synced reference
│   ├── manual/               # Project-specific reference
│   ├── WAI-VERSION-GUIDE.md  # Version documentation
│   ├── WAI-MERGE-PROTOCOLS.md # Merge guidance
│   └── WAI-AI-ONBOARDING.md  # This shows up here too
├── seed/                     # Inbound teachings
│   └── ingest/               # Teaching files from hub
│       ├── manifest.json
│       ├── *.teaching
│       └── gemini-cli-memories.md
└── sessions/                 # Multi-environment tracking
    ├── gemini-cli-machine.jsonl
    └── claude-code-machine.jsonl
```

---

## Critical Reminders

1. **WAI commands are directives**, not shell commands
2. **Use WAI-Lugs.jsonl**, not wheel-signals.jsonl or other files
3. **Log all turns** to WAI-Session-Log.jsonl
4. **Load WAI-AI-ONBOARDING.md** on session start
5. **Check for teachings** before starting work
6. **Use WAI-MERGE-PROTOCOLS.md** for complex merges
7. **Create lugs** for high-impact decisions (impact >= 8)

---

## Getting Help

If unclear on any directive:
1. Check **WAI-AI-ONBOARDING.md** first
2. Reference **WAI-Guide.md** for project context
3. Check **WAI-VERSION-GUIDE.md** for version questions
4. Check **WAI-MERGE-PROTOCOLS.md** for merge questions
5. Ask user: "I need clarification on [specific directive]"

---

*This file was auto-generated for Gemini integration.*
*Framework Version: 3.1.0*
*Last Updated: 2026-02-06*
