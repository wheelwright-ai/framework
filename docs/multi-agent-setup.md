# Setting up Multi-Agent Tasks in Wheelwright

Wheelwright allows multiple agents (AI assistants) to work on the same project simultaneously. This is achieved through **Multi-Environment Sessions** and **Lugs**.

## 1. Create a Shared Task (Lug)

Before starting, create a Lug that all agents will reference. This ensures everyone is working toward the same objective.

```bash
WAI lug add "Implement concurrent session handling"
```
*Note the Lug ID (e.g., `a3f2b1`).*

## 2. Configure Your Agents

Each agent must have a unique identity defined by its **Tool** and **Machine**. You can set these using environment variables.

### Agent 1 (e.g., Claude Code on Laptop)
```bash
export WAI_TOOL="claude-code"
export WAI_MACHINE="laptop"
# Start your session here
```

### Agent 2 (e.g., Cursor on Desktop)
```bash
export WAI_TOOL="cursor"
export WAI_MACHINE="desktop"
# Start your session here
```

## 3. Collaborative Workflow

- **Shared Context:** Both agents read from the same `WAI-Spoke/` directory.
- **Decision Tracking:** High-impact decisions (impact >= 8) made by any agent are logged to their specific session file in `WAI-Spoke/sessions/`.
- **Map & Compass:** When an agent starts a session, Wheelwright briefs them on recent activity from other agents.

## 4. Reconciliation (The Manager View)

To see the status of all active agents and reconcile their work:

### View Status
```bash
WAI status
```
This shows all active sessions, unreconciled decisions, and recent turns.

### Finalize & Merge
When the task is complete, run:
```bash
WAI closeout
```
This command acts as the "Manager" by:
1. Scanning all session logs in `WAI-Spoke/sessions/`.
2. Extracting all high-impact decisions to the main `WAI-State.json`.
3. Updating the project's environment registry.
4. Clearing the individual session logs.

## 5. Tips for Success

- **Use Lugs for everything:** Explicitly link your work to a Lug ID so other agents know what you're doing.
- **Check Status often:** Run `WAI status` to stay synced with your colleagues.
- **Shipit:** Use `WAI shipit` for a combined closeout and git commit.
