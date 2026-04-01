# IDE Optimization Checklist

**Metric:** "Is this environment fully optimized for Agentic AI?"

This checklist defines the "Golden Path" for WAI-compatible development environments. The `wai audit` command uses this to verify IDE health.

## 1. Context & Rules (The Brain)

| File | Purpose | Pass Condition | Remediation |
|------|---------|----------------|-------------|
| `.github/copilot-instructions.md` | Instructions for GitHub Copilot in VS Code | Exists & references `WAI-Spoke/WAI-Guide.md` | Create from template |
| `.cursorrules` | System prompt for Cursor | Exists & references `WAI-Spoke/WAI-Guide.md` | Create from template |
| `.windsurfrules` | System prompt for Windsurf | Exists & references `WAI-Spoke/WAI-Guide.md` | Create from template |
| `CLAUDE.md` | Context for Anthropic CLI/Web | Exists & contains project build/test commands | Create from template |

## 2. Editor Settings (The Body)

| File | Purpose | Pass Condition | Remediation |
|------|---------|----------------|-------------|
| `.vscode/settings.json` | VS Code workspace settings | Exists & excludes `WAI-Spoke/seed/` from search | Add exclusion rules |

## 3. Self-Verification (The Reflexes)

| File | Purpose | Pass Condition | Remediation |
|------|---------|----------------|-------------|
| `WAI-Backpressure.yaml` | Config for `wai check` (auto-verify) | Exists & defines `build`, `test`, `lint` | Run `wai backpressure init` |

## Audit Logic

When `wai audit` runs:
1.  Detects active IDE (e.g., if `.cursor` folder exists, check `.cursorrules`).
2.  Checks for specific file existence.
3.  Greps for critical keywords (e.g., "WAI-Guide.md").
4.  Reports **Pass**, **Warn** (missing optional), or **Fail** (missing critical).
