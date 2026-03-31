# CC Advisor — Reference

On-demand knowledge base. **Do not load at wakeup.** Load when running a full audit or generating proposals.

---

## 8-Area Audit Checks

### 1. CLAUDE.md

Read `CLAUDE.md` at spoke root.

| Check | Pass condition | Maturity |
|-------|---------------|----------|
| Project context block | Spoke name, stack, phase, modules present | All |
| Development workflow block | Ordered build/test/lint commands | All |
| Plan mode block | Thresholds defined for spoke phase | 10+ sessions |
| Slash commands block | WAI core commands listed | 10+ sessions |
| Standing rules block | Security, style, boundaries | All |
| Anti-patterns block | Present and non-empty | 10+ sessions |
| Hooks reference block | Configured hooks documented | All |
| Line count | 100+ lines with all blocks populated | 50+ sessions |

**Ideal:** 100+ lines. Anti-patterns section grows over time.

### 2. Hooks

Read `.claude/settings.json` → `hooks`.

| Hook | Check | Priority |
|------|-------|----------|
| `SessionStart` | WAI wakeup / state loading configured | Critical |
| `UserPromptSubmit` | Session guard / context injection | Critical |
| `PreToolUse` | Destructive operation guard (Bash) | Critical |
| `Stop` | Test suite runner | High |
| `PreCompact` | State preservation before context compaction | High |
| `PostToolUse` | Formatter / typechecker after writes | Medium |

### 3. Permissions

Read `.claude/settings.json` → `permissions`.

| Check | Pass condition |
|-------|---------------|
| `allow` array present | Spoke-specific safe commands listed |
| `deny` array present | Destructive ops blocked (rm -rf, force-push) |
| No `--dangerously-skip-permissions` | Absent from global settings |
| `settings.local.json` clean | < 20 entries, no session-specific paths |

### 4. Statusline

Read `~/.claude/settings.json` → `statusLine`.

| Check | Pass condition |
|-------|---------------|
| Statusline configured | `type: command` present |
| Shows context % | Script outputs context percentage |
| Color thresholds | green <60%, yellow 60-85%, red >85% |

### 5. Slash Commands

Read `.claude/commands/` listing.

| Check | Pass condition |
|-------|---------------|
| WAI core commands | `wai`, `wai-closeout`, `wai-status`, `wai-time` present |
| Utility commands | At least 2 spoke-specific commands |

### 6. Subagents

Read `.claude/agents/` directory.

| Check | Pass condition |
|-------|---------------|
| Agent files present | At least 1 agent definition |
| Memory mode set | `memory: project` or `memory: local` declared per agent |

### 7. MCP Servers

Read `.mcp.json` at spoke root.

| Check | Pass condition |
|-------|---------------|
| File present | `.mcp.json` exists |
| GitHub MCP | `github` server configured (for repos with PRs) |

### 8. Git Worktrees

Run `git worktree list`.

| Check | Pass condition |
|-------|---------------|
| Worktrees available | More than 1 worktree entry |

---

## Gap Report Format

```
┌─ CC OPTIMIZATION AUDIT ─────────────────────────┐
│ Spoke: {name}  Phase: {phase}  Score: {N}/8      │
│ Sessions since last audit: {N}  Delta: {+/-N}    │
├──────────────────────────────────────────────────┤
│ Area            │ Status │ Priority │ Action      │
│─────────────────│────────│──────────│─────────────│
│ CLAUDE.md       │ PASS   │ ─        │             │
│ Hooks           │ FAIL   │ Critical │ Add Stop    │
│ Permissions     │ PASS   │ ─        │             │
│ Statusline      │ FAIL   │ High     │ Configure   │
│ Slash_Commands  │ PASS   │ ─        │             │
│ Subagents       │ PASS   │ ─        │             │
│ MCP_Servers     │ FAIL   │ Low      │ Add GitHub  │
│ Git_Worktrees   │ FAIL   │ Low      │ Consider    │
└──────────────────────────────────────────────────┘

REGRESSION VECTORS:
  - Hooks score dropped -1 (session 104→106): PostToolUse removed
```

---

## Event Log Schemas

### permission-prompts.jsonl

```json
{"ts": "ISO-8601", "session": "session-id-8chars", "spoke": "wheel.name", "event": "permission_request", "data": {"tool": "Bash", "verb": "rm", "command": "rm -f /tmp/x", "classification": "safe|review|deny|unknown"}}
```

### session-events.jsonl

```json
{"ts": "ISO-8601", "session": "session-id", "spoke": "wheel.name", "event": "session_start", "data": {}}
{"ts": "ISO-8601", "session": "session-id", "spoke": "wheel.name", "event": "session_end", "data": {"duration_minutes": 45, "tokens_used": 0, "context_pct_at_end": 0, "compact_count": 0, "permission_prompts": 0}}
```

### hook-events.jsonl

```json
{"ts": "ISO-8601", "session": "session-id", "spoke": "wheel.name", "event": "hook_fire", "data": {"hook_name": "pre-tool-guard", "result": "ok", "duration_ms": 12, "error": null}}
```

---

## Proposal Diff Template

`reports/proposal-YYYYMMDD-{area}.md`:

```markdown
# CC Advisor Proposal: {Area} Gap

**Generated:** {ISO-8601}
**Session:** {session-id}
**Area:** {area}
**Gap:** {description}

## Proposed Change

File: `{target-file}`

```diff
- {old line}
+ {new line}
```

## Why

{rationale — what gap this fixes}

## Apply

Run: `{command to apply}`

**Requires user approval before applying.**
```

---

## Safe Auto-Apply Rules

A command is safe to auto-apply to `permissions.allow` when ALL of these hold:
1. Tool is `Read`, `Glob`, `Grep`, `Bash(cat *)`, `Bash(ls *)`, `Bash(git log *)`, or similar read-only
2. Prompted for permission in 3+ distinct sessions
3. Never caused a write side-effect (no file creation, no git mutations)
4. Not in `permissions.deny` already

Auto-apply action:
1. Add to `settings.json` `permissions.allow[]`
2. Log entry to `logs/auto-apply.jsonl`
3. Update `scan_state.json` `auto_applied_count += 1`
4. Surface to user: "CC Advisor: auto-added `{command}` to allow list (prompted 3+ sessions, read-only)"

---

## Hub CC Advisor (Phase 5)

Location: `{hub_path}/WAI-Hub/advisors/cc-advisor/`
Same structure as spoke advisor: `scan_state.json`, `passes.jsonl`, `vectors.jsonl`, `reports/`

**Cross-spoke pattern detection:**
- Reads signals from `WAI-Hub/signals/incoming/` where `tags` includes `cc-advisor`
- If 2+ spokes report same gap within 30 days → create teaching candidate
- Teaching is `safe_to_auto_adopt: true` for permission additions, `false` for CLAUDE.md/hook changes

**Weekly report:** `WAI-Hub/advisors/cc-advisor/reports/weekly-YYYY-MM-DD.md`
- Aggregate score per spoke
- Fleet average score trend
- Top 3 recurring gaps across fleet
