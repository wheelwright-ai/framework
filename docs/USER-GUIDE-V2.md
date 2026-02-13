# Wheelwright v2 User Guide

**Welcome to Wheelwright Framework v2.0** - AI-first session continuity and collective learning

**Version:** 2.0.0
**Audience:** Developers using Claude Code with Wheelwright
**Last Updated:** 2026-02-12

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Session Workflow](#session-workflow)
4. [Core Concepts](#core-concepts)
5. [Commands Reference](#commands-reference)
6. [Skills System](#skills-system)
7. [Cross-Node Signals](#cross-node-signals)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Wheelwright?

Wheelwright is a framework for **session continuity** and **collective learning** when working with AI agents (specifically Claude Code). It provides:

- **Session continuity:** Pick up where you left off across sessions
- **Observation system:** Track high-impact work automatically
- **Skills system:** Behavioral guards, advisors, and watchers
- **Cross-node signals:** Share learnings across projects
- **Machine-aware:** Optimizes recommendations for your hardware

### Why Wheelwright?

**Problem:** AI agents have no memory between sessions. Each conversation starts fresh.

**Solution:** Wheelwright provides:
1. **Lugs** (work items) - Persistent task/decision records
2. **Observations** - Event stream of high-impact work
3. **Compact actions** - 3-6 steps to resume work
4. **BRIEF cascade** - Behavioral rules (Hub → Project → Spoke)
5. **Cross-node signals** - Share discoveries across projects

---

## Getting Started

### Prerequisites

- Claude Code CLI installed
- Python 3.8+ (for Wheelwright framework)
- Git repository (recommended)

### Installation

1. **Install Wheelwright framework:**
```bash
pip install wheelwright-framework
```

2. **Initialize Wheelwright in your project:**
```bash
cd your-project/
python -m wai init
```

This creates:
- `WAI-Spoke/` directory (state, Lugs, observations)
- `CLAUDE.md` (instructions for Claude)
- `WAI-Manifest.yaml` (extension registry)

3. **Verify installation:**
```bash
python -m wai.closeout_validator --check
```

Expected output:
```
✅ Git status: Clean
✅ Framework: v2.0.0 (importable)
✅ Machine profile: exists
✅ Spoke directory: WAI-Spoke/ present
```

---

## Session Workflow

### Session Start (Automatic)

When Claude Code starts a session in a Wheelwright-enabled project:

1. **Integration check** - Verifies environment
2. **Briefing displays** - Shows:
   - Machine status (classification, RAM)
   - Recent work summary
   - Compact action (resume steps from last session)
   - Failed observations (if any)
3. **Context loaded** - WAI-State.json, BRIEF.md, Skills

**What you see:**
```
# Session Start Briefing

Machine: workstation (HIGH-PERFORMANCE, 64GB RAM)
Project: My Awesome Project
Last session: Implemented authentication module

**Compact Action (Resume):**
1. Test authentication flow end-to-end
2. Add error handling for edge cases
3. Document API endpoints
4. Update integration tests
5. Closeout with learnings

---

**What to do next:**
1. Review compact action above
2. Continue with your work
3. New observations will be logged automatically
```

### During Session

**Automatic behaviors:**
- **safe-refactor:** Creates git checkpoint before structural changes
- **qc-check:** Runs quality gates (tests, coverage) before commits
- **hub-watcher:** Checks for signals on session_start
- **brief-advisor:** Checks BRIEF alignment for high-impact decisions
- **session-observer:** Logs high-impact events (impact >= 6)
- **wai-signal-advisor:** Publishes high-impact learnings (impact >= 8)

**You work normally** - Skills operate in background

### Session End (Manual)

**Option 1: /wai-closeout**
```bash
/wai-closeout
```
- Synthesizes session summary
- Creates compact action for next session
- Validates git status, observations logged

**Option 2: /wai-shipit** (Closeout + Commit + Push)
```bash
/wai-shipit
```
- Runs closeout + quality gates
- Stages all files (git add -A)
- Commits with structured message
- Pushes to remote (if configured)

**Structured commit message:**
```
Phase 5: Authentication module implementation

## Completed
- Implemented JWT authentication
- Added refresh token support
- Created middleware for protected routes
- Added integration tests

## Impact
User authentication now secure and performant. Refresh tokens
reduce re-login frequency by 80%.

## Next: Phase 6
Authorization and role-based access control

## Compact Action for Phase 6
1. Design role hierarchy (admin, user, guest)
2. Implement permission checks
3. Add role assignment API
4. Test authorization flows
5. Document permissions model

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Core Concepts

### 1. Lugs (Work Items)

**Lug = task, decision, observation, or signal**

**Types:**
- `task`: Work to be done
- `decision`: Architectural or significant choice
- `observation`: Learning or event
- `signal`: Cross-node discovery

**Example Lug:**
```json
{
  "lug_id": "decision-jwt-refresh-2026-02-12",
  "type": "decision",
  "title": "Adopt JWT refresh token pattern",
  "body": "Implement sliding window refresh...",
  "pev": {
    "perceive": "Frequent token expiration caused UX issues",
    "execute": "200+ refresh calls/hour, user complaints",
    "verify": "Sliding window reduced overhead 40%"
  },
  "impact": 9,
  "status": "resolved"
}
```

### 2. PEV (Perspective-Evidence-Verdict)

**Structured reasoning for important Lugs:**

- **Perspective:** What was the context/problem?
- **Evidence:** What data supported the decision?
- **Verdict:** What was concluded/chosen?

### 3. Compact Action

**3-6 actionable steps for next session**

**Good compact action:**
```
1. Test authentication flow end-to-end
2. Add error handling for edge cases
3. Document API endpoints
4. Update integration tests
5. Closeout with learnings
```

**Bad compact action:**
```
1. Continue work
2. Fix bugs
3. Test stuff
```
(Too vague, not actionable)

### 4. BRIEF Cascade

**Behavioral rules hierarchy:**

```
Hub BRIEF (universal)
  ↓ inherits
Project BRIEF (shared)
  ↓ inherits
Spoke BRIEF (local)
```

**Hub rules:** Non-negotiable (all spokes)
**Project rules:** Shared (all spokes in project)
**Spoke rules:** Local customization

### 5. Skills

**Behavioral automations:**

- **Guardians:** Block unsafe actions (safe-refactor, integration-check)
- **Reviewers:** Validate quality (qc-check, file-audit)
- **Advisors:** Suggest best practices (brief-advisor, wai-signal-advisor)
- **Watchers:** Monitor environment (hub-watcher, session-observer)
- **Workers:** Coordinate tasks (wai-shipit, framework-updater)

---

## Commands Reference

### Session Management

**`/wai`** - Unified briefing
```bash
/wai
```
Shows: machine status, recent work, compact action, action items

**`/wai-status`** - Health check
```bash
/wai-status
```
Shows: git status, observations count, framework version, health score

**`/wai-closeout`** - End session ceremony
```bash
/wai-closeout
```
Creates: session summary Lug, compact action, validates environment

**`/wai-shipit`** - Closeout + commit + push
```bash
/wai-shipit
```
Orchestrates: closeout → quality gates → stage → commit → push

### Quality & Validation

**`/check-brief`** - BRIEF alignment check
```bash
/check-brief
```
Checks: decision alignment with BRIEF cascade

**`/audit-files`** - File organization health
```bash
/audit-files
```
Detects: sprawl, disorganization, health score

### Framework Updates

**`/framework-update`** - Cascade template updates
```bash
/framework-update
```
Updates: templates when framework version changes

### Cross-Node Signals

**`/wai-learn`** - Review hub signals
```bash
python -m wai.signal_reviewer
```
Reviews: pending signals in hub/intake/, adopt or acknowledge

### Information

**`/wai-time`** - Token usage summary
```bash
/wai-time
```
Shows: context usage, remaining tokens

**`/wai-rules`** - Show BRIEF cascade
```bash
/wai-rules
```
Displays: Hub + Project + Spoke rules

---

## Skills System

### 10 Built-in Skills

**1. safe-refactor** (guardian)
- Creates git checkpoint before structural changes
- Prevents data loss (Hub destroyed 2026-02-10 → this Skill created)

**2. qc-check** (reviewer)
- Runs tests, validates startup, checks coverage
- Pre-commit warnings (secrets, large files, debug statements, TODOs)

**3. hub-watcher** (watcher)
- Checks hub on session_start
- Notifies about framework updates and pending signals

**4. framework-updater** (worker)
- Cascades template updates from hub to spoke
- Human gate if spoke modified template

**5. brief-advisor** (advisor)
- Checks decision alignment with BRIEF cascade
- Learns user preferences from decision history

**6. session-observer** (watcher)
- Logs high-impact events (impact >= 6)
- Synthesizes session summary on closeout

**7. file-audit** (reviewer)
- Detects sprawl (flat root, config sprawl, orphans)
- Health score 0-10 based on organization

**8. integration-check** (guardian)
- Verifies environment on session_start
- Checks: Wheelwright detectable, git available, machine profile exists

**9. wai-shipit** (worker)
- Orchestrates closeout + commit + push workflow
- 7 steps: pre-flight → synthesis → QC → checkpoint → stage → commit → push

**10. wai-signal-advisor** (advisor)
- Publishes high-impact learnings (impact >= 8) to hub/intake/
- Duplicate detection, opt-out support

### Customizing Skills

**Spoke-level overrides:**

Create `spoke/skills/{skill-name}.yaml` to override framework defaults.

**Example: Custom QC commands**

`spoke/skills/qc-check.yaml`:
```yaml
custom_commands:
  - "npm run lint"
  - "npm test"
  - "npm run type-check"
coverage_threshold: 85
startup_command: "node server.js --help"
```

---

## Cross-Node Signals

### What Are Signals?

**High-impact discoveries shared across spokes**

**Signal flow:**
```
Spoke A discovers pattern (impact: 9)
  ↓
wai-signal-advisor → hub/intake/
  ↓
Spoke B session_start → hub-watcher notifies
  ↓
User runs /wai-learn → Reviews signal
  ↓
Adopt or acknowledge → hub/archive/
```

### Creating Signals (Automatic)

**Criteria:**
- Impact >= 8
- Applicable beyond your spoke
- Not duplicate
- Not temporary workaround

**wai-signal-advisor** publishes automatically when:
- Decision Lug created with impact >= 8
- Observation Lug created with impact >= 8
- `cross_node_signals: true` in manifest

### Reviewing Signals

**1. Check hub-watcher notification (session_start):**
```
Hub Status:
  Pending Signals: 3
  - JWT refresh strategy (impact: 9)
  - Co-located tests pattern (impact: 8)
  - Race condition fix (impact: 10)

Run /wai-learn to review.
```

**2. Run /wai-learn:**
```bash
python -m wai.signal_reviewer
```

**3. Review each signal:**
- **[A]dopt:** Create local Lug + archive signal
- **[K]nowledge:** Archive without adopting
- **[S]kip:** Leave in queue for later
- **[Q]uit:** Pause review

### Opt-Out

**Disable signal participation:**

`WAI-Manifest.yaml`:
```yaml
signals:
  cross_node_signals: false  # Don't publish signals
```

---

## Best Practices

### 1. Session Hygiene

**Do:**
- ✅ Run /wai-shipit at end of each session
- ✅ Create compact actions (3-6 specific steps)
- ✅ Log high-impact decisions (impact >= 7) as Lugs
- ✅ Review signals weekly (/wai-learn)

**Don't:**
- ❌ Leave sessions without closeout (no continuity)
- ❌ Skip quality gates (tests, startup checks)
- ❌ Commit without structured message
- ❌ Ignore hub-watcher notifications

### 2. Lug Quality

**Do:**
- ✅ Use PEV for important Lugs (decisions, observations)
- ✅ Set realistic impact scores (1-10)
- ✅ Include resolution_reason for decisions
- ✅ Tag Lugs appropriately

**Don't:**
- ❌ Inflate impact scores (all 10s = meaningless)
- ❌ Skip PEV for high-impact Lugs
- ❌ Create Lugs for trivial work

### 3. Signal Etiquette

**Do:**
- ✅ Review signals within 7 days
- ✅ Adopt applicable patterns
- ✅ Acknowledge signals you've reviewed
- ✅ Publish high-impact discoveries

**Don't:**
- ❌ Let signals sit unreviewed > 30 days
- ❌ Publish low-impact signals (< 8)
- ❌ Include sensitive data in signals
- ❌ Create duplicate signals

### 4. Machine Awareness

**Do:**
- ✅ Check machine classification (briefing shows it)
- ✅ Adjust expectations based on hardware
- ✅ Accept conservative recommendations on LOW-POWER
- ✅ Leverage aggressive features on HIGH-PERFORMANCE

**Don't:**
- ❌ Ignore machine warnings
- ❌ Enable workspace analysis on LOW-POWER
- ❌ Expect instant responses on constrained hardware

---

## Troubleshooting

### Common Issues

**1. Session briefing not showing**

**Cause:** CLAUDE.md not being read or session_hook not working

**Fix:**
```bash
# Verify framework importable
python -c "from wai.session_hook import get_session_start_briefing; print('OK')"

# Check CLAUDE.md exists
ls CLAUDE.md
```

**2. /wai-shipit failing**

**Cause:** Quality gates failing or git errors

**Check:**
```bash
# Run tests manually
pytest

# Check git status
git status

# Verify no secrets staged
git diff --cached | grep -i "password\|secret\|key"
```

**3. Signals not appearing**

**Cause:** Hub path not configured or cross_node disabled

**Fix:**
```yaml
# Check WAI-State.json
{
  "wheel": {
    "hub_path": "/path/to/hub"  # Must be set
  }
}

# Check WAI-Manifest.yaml
signals:
  cross_node_signals: true  # Must be true
```

**4. Compact action not in briefing**

**Cause:** No session summary Lug with compact_action

**Fix:**
```bash
# Verify Lugs file exists
ls WAI-Spoke/WAI-Lugs.jsonl

# Check for compact_action in recent Lugs
tail -5 WAI-Spoke/WAI-Lugs.jsonl | grep "compact_action"
```

### Getting Help

**Check documentation:**
- `docs/CROSS-NODE-SIGNALS.md` - Signal protocol
- `docs/BRIEF-CASCADE.md` - BRIEF hierarchy
- `docs/COMMAND-MAPPING.md` - Command reference
- `docs/SIGNAL-BEST-PRACTICES.md` - Signal guidelines

**Run health check:**
```bash
/wai-status
```

**Check framework version:**
```bash
python -m wai --version
```

---

## Appendix

### File Structure

```
your-project/
├── WAI-Spoke/                # Wheelwright state
│   ├── WAI-State.json        # Project state
│   ├── WAI-State.md          # Strategic vision
│   ├── WAI-Lugs.jsonl        # Work items
│   ├── observations.jsonl    # Event stream
│   └── WAI-Session-Log.jsonl # Conversation history
├── CLAUDE.md                 # Instructions for Claude
├── BRIEF.md                  # Behavioral rules (spoke level)
├── WAI-Manifest.yaml         # Extension registry entry
└── [your project files]
```

### Glossary

- **Hub:** Central coordination point (registry, signals, health)
- **Spoke:** Individual project/extension
- **Lug:** Work item (task, decision, observation, signal)
- **PEV:** Perspective-Evidence-Verdict (reasoning structure)
- **Compact action:** 3-6 resume steps for next session
- **BRIEF:** Behavioral rules cascade (Hub → Project → Spoke)
- **Skill:** Behavioral automation (guardian, reviewer, advisor, watcher, worker)
- **Signal:** Cross-node discovery (high-impact learning)
- **Herald pattern:** Hub writes, spokes read (decoupled communication)

### Version History

**v2.0.0** (Current)
- Registry architecture (Hub-Project-Spoke)
- 10 Skills with comprehensive use cases
- BRIEF cascade (3-level hierarchy)
- Cross-node signals (collective learning)
- Shipit workflow automation
- Compact actions (session continuity)
- Machine-aware optimization

**v1.x** (Legacy)
- WAI-Backpressure.yaml (migrated to qc-check)
- WAI-Rules.md (absorbed into Skills + BRIEF)
- Single-level architecture (no Hub)

---

**Welcome to Wheelwright v2!** 🎉

For questions, issues, or contributions:
- GitHub: https://github.com/wheelwright-ai/framework
- Docs: https://wheelwright.ai/docs (if exists)

**Happy building with AI continuity!**
