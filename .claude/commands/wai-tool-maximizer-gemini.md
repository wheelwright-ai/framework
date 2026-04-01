# WAI Tool Maximizer: Gemini

Proactive Gemini CLI optimization audit. Detects underweight configs and surfaces gaps with prioritized fixes.

## Type

`guard` (advisory) — same pattern as wai-tool-maximizer-claude.

## When to Trigger

| Condition | Detection |
|-----------|-----------|
| Missing GEMINI.md | Project root has no GEMINI.md |
| No WAI wakeup directive | GEMINI.md exists but lacks WAI protocol reference |
| No .geminiignore | Large dirs (node_modules, WAI-Spoke/sessions) not excluded |
| No settings.json | `.gemini/settings.json` missing or default |
| No @imports | GEMINI.md doesn't reference WAI-Guide or AGENTS.md |
| New spoke onboarding | WAI-State.json exists but Gemini config is absent |

## Audit Checklist

### 1. GEMINI.md (Critical)

**Check for:**
- Project context block (spoke name, stack, phase)
- WAI wakeup directive (read AGENTS.md, WAI-State.json, run protocol)
- Development workflow block (build/test/lint commands)
- Standing rules block (security, style, boundaries)
- @import of AGENTS.md and WAI-Guide.md

**Ideal:** 80+ lines with WAI integration, stack context, and @imports for modular loading.

### 2. .geminiignore (Critical)

**Check for:**
- `node_modules/`, `build/`, `dist/` excluded
- `WAI-Spoke/sessions/` excluded (token-heavy session tracks)
- `WAI-Spoke/seed/` excluded (teaching archives)
- `.env` and credentials excluded
- Large binary or generated files excluded

**Ideal:** Comprehensive ignore file preventing token waste on non-code files.

### 3. settings.json (High)

**Read:** `.gemini/settings.json` (project) and `~/.gemini/settings.json` (global)

**Check for:**
- `model.name` set (not relying on default)
- `checkpointing.enabled: true`
- `coreTools` configured (safety restrictions)
- `chatCompression.contextPercentageThreshold` tuned
- `context.fileName` includes `["GEMINI.md", "AGENTS.md"]`

**Ideal:** Model selection matches task complexity. Checkpointing enabled. Compression tuned for WAI context tiers.

### 4. @Imports & Modular Context (High)

**Check GEMINI.md for:**
- `@./AGENTS.md` — universal WAI bootstrap
- `@./WAI-Spoke/WAI-Guide.md` — protocol documentation (if exists)
- Any shared style guides or architecture docs

**Ideal:** Main GEMINI.md is lean; heavy context loaded via @imports.

### 5. MCP Servers (Medium)

**Read:** `.mcp.json` at project root (shared between tools)

**Check for:**
- GitHub MCP for PR management
- Project-specific integrations

**Ideal:** Same .mcp.json serves both Claude and Gemini sessions.

### 6. Model Selection Strategy (Medium)

**Check for awareness of:**
- `gemini-2.5-pro` — deep reasoning, architecture, complex tasks
- `gemini-2.5-flash` — fast iteration, simple tasks, high-volume work
- Task-model alignment documented in GEMINI.md or settings

**Ideal:** Model selection guidance in GEMINI.md so Gemini knows when to suggest switching.

### 7. Custom Firmware (Low)

**Check for:**
- `GEMINI_SYSTEM_MD=1` in `.env` or shell profile
- `~/.gemini/system.md` with WAI-aware system prompt

**Ideal:** Custom firmware replaces default system prompt with WAI-native behavior.

### 8. Cross-Tool Continuity (Low)

**Check for:**
- AGENTS.md present (universal fallback for any AI tool)
- WAI-Spoke tracks readable by Gemini (no Claude-specific assumptions)
- Session tracks use tool-agnostic format

**Ideal:** A Gemini session can pick up where a Claude session left off — same WAI-Spoke, same lugs, same state.

## Gap Report Format

```
┌─ GEMINI OPTIMIZATION AUDIT ────────────────────┐
│ Spoke: {name}  Phase: {phase}  Score: {N}/8     │
├─────────────────────────────────────────────────┤
│ Area            │ Status │ Priority │ Action     │
│─────────────────│────────│──────────│────────────│
│ GEMINI.md       │ [gap]  │ Critical │ [fix]      │
│ .geminiignore   │ [gap]  │ Critical │ [fix]      │
│ settings.json   │ [gap]  │ High     │ [fix]      │
│ ...             │        │          │            │
└─────────────────────────────────────────────────┘
```

## Fix Mode

When asked to fix a specific gap:
1. Load `wai-tool-maximizer-gemini-reference.md` for templates and examples
2. Read the current file that needs patching
3. Generate a patch that is **additive** — merge into existing config
4. Present the patch for approval
5. Apply and verify

## Context Budget

- This skill file: load at audit time
- Reference file: load **on-demand only** when generating a fix
- Never load reference file at wakeup

## Related Skills

- `/wai-tool-maximizer-claude` — Claude Code equivalent
- `/wai-ide-setup` — Hook configuration guide
- `/wai-status` — Quick health check
