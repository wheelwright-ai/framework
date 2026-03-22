# WAI Guide v2.0 - Skill Index

**Status:** Knowledge migrated to skills (v2.0 transition complete)  
**Legacy:** v1.0 content archived in `WAI-Spoke/reference/auto/WAI-Guide-v1.md`

This file now serves as the skill directory. Full behavioral content lives in individual skill files.

---

## What is Wheelwright?

Wheelwright builds AI wheels that remember everything. Instead of losing context when sessions end, your wheel rolls forward continuously - maintaining memory, learning patterns, and extending capabilities.

**The Wheel Metaphor:**
- **Hub** = Central memory and consolidated knowledge
- **Spokes** = Specialized capabilities (analysis, consultation, code review)
- **Rim** = The interface connecting to any LLM
- **Rolling** = Each turn moves forward, never losing ground

**Framework Version:** 2.0  
**Repository:** https://github.com/wheelwright-ai/framework

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

---

## For AI Assistants

**Start here:**
1. Read `CLAUDE.md` or `GEMINI.md` (your integration file)
2. Load skill registry: `WAI-Spoke/WAI-Skills.jsonl`
3. Reference skills below as needed

**Core files:**
- `WAI-State.json` - Technical spec, foundation, session state (UPDATE)
- `WAI-State.md` - Strategic context, vision (UPDATE)
- `WAI-Skills.jsonl` - Skill registry with metadata (READ)
- `WAI-Lugs.jsonl` - Active work and task graph (UPDATE)
- `WAI-Lugs.jsonl` - High-impact signals stored as lugs with `impact >= 8` (APPEND — `WAI-Signals.jsonl` is retired)

---

## Skill Index

### Core Skills

**[wai](/wai) - WAI Wakeup**  
10-step wakeup protocol with teaching discovery, track detection, skill loading, and briefing generation.  
📄 `templates/commands/wai.md`  
**Use when:** Session start, context resume, teaching discovery

**[wai-closeout](/wai-closeout) - Closeout Protocol**  
Session preservation - extract signals, reconcile state, update session metadata.  
📄 `templates/commands/wai-closeout.md`  
**Use when:** Session end, state preservation, signal extraction

**[wai-shipit](/wai-shipit) - Ship It**  
Quality gate + closeout + git commit workflow with test execution and README sync.  
📄 `templates/commands/wai-shipit.md`  
**Use when:** Release, quality gate, commit

---

### Advisory Skills

**[wai-complexity-advisor](/wai-complexity-advisor) - Complexity Planning Advisor**  
Triggers planning gate when work affects 2+ files OR requires 6+ steps - exempts utility commands.  
📄 `templates/commands/wai-complexity-advisor.md`  
**Triggers:** Changes to 2+ files, 6+ implementation steps, architectural decisions  
**Auto-watch:** Enabled

**[wai-stewardship-advisor](/wai-stewardship-advisor) - Stewardship Advisor**  
Detects scope drift, enforces boundaries, requires explicit acknowledgment for direction changes.  
📄 `templates/commands/wai-stewardship-advisor.md`  
**Triggers:** Scope drift, boundary violation, foundation evolution  
**Auto-watch:** Enabled

**[wai-context-advisor](/wai-context-advisor) - Context Efficiency Advisor**  
Enforces lazy-loading patterns, prevents unnecessary file reads, optimizes token usage.  
📄 `templates/commands/wai-context-advisor.md`  
**Triggers:** Loading reference files, reading deprecated content, context bloat  
**Auto-watch:** Enabled

**[wai-foundation-advisor](/wai-foundation-advisor) - Foundation Completeness Advisor**  
Enforces foundation completion before work starts - guides users through identity, boundaries, approach.  
📄 `templates/commands/wai-foundation-advisor.md`  
**Triggers:** Incomplete foundation, missing setup, work before initialization  
**Auto-watch:** Enabled

**[wai-signal-advisor](/wai-signal-advisor) - Signal Capture Advisor**  
Triggers signal capture for high-impact decisions (impact >= 8) - ensures learnings are preserved.  
📄 `templates/commands/wai-signal-advisor.md`  
**Triggers:** Impact >= 8, high-impact decisions, significant learnings  
**Auto-watch:** Enabled

**[wai-lug-advisor](/wai-lug-advisor) - Lug System Advisor**  
Advisory skill for lug authoring - schema enforcement, lifecycle guidance, cross-session clarity.  
📄 `templates/commands/wai-lug-advisor.md`  
**Triggers:** Lug creation, schema changes, lifecycle operations  
**Auto-watch:** Enabled

---

### Utility Skills

**[wai-status](/wai-status) - Health Check**  
Quick health check with context status, active work summary, and recommendations.  
📄 `templates/commands/wai-status.md`

**[wai-time](/wai-time) - Token Check**  
Intelligent token usage estimate with 80% capacity warnings and efficiency metrics.  
📄 `templates/commands/wai-time.md`

**[wai-mode](/wai-mode) - Session Mode**  
Set session mode (execution, interactive, planning, review, deploy) to control advisory behavior.  
📄 `templates/commands/wai-mode.md`

**[wai-red-light](/wai-red-light) - Red Light**  
Inspect autosave checkpoints and assess crash recovery readiness.  
📄 `templates/commands/wai-red-light.md`

**[wai-green-light](/wai-green-light) - Green Light**  
Resume from last autosave checkpoint - restore session state and continue work.  
📄 `templates/commands/wai-green-light.md`

**[wai-track-generate](/wai-track-generate) - Track Generator**  
Generate high-fidelity session tracks for cross-tool context continuity.  
📄 `templates/commands/wai-track-generate.md`

**[wai-chat-to-track](/wai-chat-to-track) - Chat to Track**  
Convert external AI chat sessions to WAI track format for cross-tool context continuity.  
📄 `templates/commands/wai-chat-to-track.md`

**[wai-ide-setup](/wai-ide-setup) - IDE Setup**  
Configure IDE-specific hooks and integrations for Claude Code, Cursor, VS Code, etc.  
📄 `templates/commands/wai-ide-setup.md`

**[wai-benchmark](/wai-benchmark) - Benchmark**  
Dual-purpose benchmarking - performance measurement + feature regression testing.  
📄 `templates/commands/wai-benchmark.md`

**[wai-init-v2](/wai-init-v2) - Init v2** ⚠️  
Initialize new spoke with templates and structure - WARNING: Creates/modifies files.  
📄 `templates/commands/wai-init-v2.md`

**[wai-sync-v2](/wai-sync-v2) - Sync v2** ⚠️  
Sync spoke with hub - distribute teachings and upgrade templates.  
📄 `templates/commands/wai-sync-v2.md`

---

### Governance Skills

**[wai-foundation](/wai-foundation) - Foundation**  
Project foundation definition - identity, boundaries, approach, and philosophy.  
📄 `templates/commands/wai-foundation.md`

**[wai-principles](/wai-principles) - Principles**  
Core principles P1-P9 that govern WAI behavior and decision-making.  
📄 `templates/commands/wai-principles.md`

**[wai-rules](/wai-rules) - Rules**  
Show active project boundaries, constraints, and behavioral guidelines.  
📄 `templates/commands/wai-rules.md`

**[wai-stewardship-framework](/wai-stewardship-framework) - Stewardship Framework**  
AI as responsible partner framework - detect drift, require acknowledgment, prefer verification.  
📄 `templates/commands/wai-stewardship-framework.md`

**[wai-improve](/wai-improve) - Improve**  
Framework self-improvement protocol - propose and implement WAI enhancements.  
📄 `templates/commands/wai-improve.md`

---

## Skill Registry

All skills are registered in `WAI-Spoke/WAI-Skills.jsonl` with metadata:

```bash
cat WAI-Spoke/WAI-Skills.jsonl
```

**Registry Fields:**
- `id` - Skill identifier (command name without `wai-` prefix)
- `name` - Human-readable name
- `type` - core | advisory | utility | governance
- `lifecycle` - stable | beta | deprecated | superseded
- `scope` - spoke | hub | framework
- `safety_level` - 1-10 (10 = always safe, 1 = destructive)
- `advisory` - Boolean (triggers on patterns vs explicit invocation)
- `watchers` - Array of patterns that trigger advisory
- `objects` - Files this skill reads/writes
- `use_cases` - When to use this skill
- `command_file` - Filename in `commands/`
- `description` - One-line summary

---

## Quick Start Patterns

### Session Start
```
1. Load skills: cat WAI-Spoke/WAI-Skills.jsonl
2. Check mode: jq '._session_state.mode' WAI-Spoke/WAI-State.json
3. Run wakeup: /wai
4. Review briefing and active work
```

### Session End
```
1. Extract signals: /wai-closeout
2. Commit changes: /wai-shipit (includes quality gates)
```

### Task Management
```
1. View work: jq 'select(.status == "open" or .status == "in_progress")' WAI-Spoke/WAI-Lugs.jsonl
2. Track decisions: Advisory skills auto-capture high-impact items
3. Review signals: jq 'select(.type == "signal" or .ty == "signal")' WAI-Spoke/WAI-Lugs.jsonl
```

---

## Migration Notes

**v1.0 → v2.0 Changes:**
- Knowledge moved from WAI-Guide.md to skill files
- Behavioral rules now live in skill Context blocks
- WAI-Guide.md simplified to skill index only
- Legacy content archived in `reference/auto/WAI-Guide-v1.md`

**Backward Compatibility:**
- All v1 commands still work
- Skill registry adds metadata, doesn't break existing workflows
- Advisory skills enhance, don't replace, existing behaviors

---

## Related Files

- `CLAUDE.md` - Claude Code integration instructions
- `GEMINI.md` - Gemini integration instructions  
- `WAI-Spoke/WAI-Skills.jsonl` - Skill registry
- `WAI-Spoke/WAI-State.json` - Session state
- `templates/commands/` - Skill source files

---

*WAI Guide v2.0 - Skill System Active*  
*Framework: https://github.com/wheelwright-ai/framework*
