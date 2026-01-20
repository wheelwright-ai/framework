# Setting up Multi-Agent Orchestration

**The Hub is your village brain.** It allows multiple independent agents (Architects, Builders, Reviewers) to coordinate without direct communication, using the Lug system as a persistent state layer.

## The Architecture: "Shared Brain"

Instead of "passing the baton" (handoffs), agents orbit a central **Shared Brain** (the Hub).

- **Architect Agent:** Breaks big ideas into Lugs.
- **Builder Agent:** Picks up "ready" Lugs and implements them.
- **The Hub:** Tracks state, blocks dependent work, and consolidates learnings.

## 1. Defining Agent Roles

Agents must know their role to behave correctly. You define this per-session using environment variables or the `agent_id/agent_role` fields.

| Role | Environment Variable | Responsibility | Behavioral Rules |
|------|----------------------|----------------|------------------|
| **Architect** | `WAI_ROLE=architect` | Planning, decomp, review | Focus on `WAI-State.json` & `Lugs`. No code implementation. |
| **Builder** | `WAI_ROLE=builder` | Implementation, testing | Focus on code. Must follow "System Sketch" before coding. |
| **Reviewer** | `WAI_ROLE=reviewer` | QA, security audit | Verifies `WAI-Guide.md` compliance. |

### Example Configuration (CLI)
```bash
# Terminal 1: Architect (Claude)
export WAI_AGENT_ID="claude-arch"
export WAI_AGENT_ROLE="architect"

# Terminal 2: Builder (Cursor)
export WAI_AGENT_ID="cursor-dev"
export WAI_AGENT_ROLE="builder"
```

## 2. The "Ready Queue" Workflow

Unlike linear workflows, WAI uses a **Pull-Based System** via the `wai ready` command.

### Step 1: The Architect Plans
The Architect breaks a feature into Lugs with dependencies.

```bash
# Architect creates the roadmap
WAI lug create "Implement Auth System" --priority high
WAI lug create "Setup Database" --priority high
WAI lug create "Create Login UI" --priority medium --deps <db_lug_id>
```

### Step 2: The Builder Pulls Work
The Builder doesn't ask "what's next?"—it asks the Hub.

```bash
WAI ready
```

**Output:**
```
[P1] Setup Database (Lug: a1b2) - Unblocked
```
*(Note: "Create Login UI" is hidden because it's blocked by DB)*

### Step 3: Implementation & System Sketch
Before writing code, the Builder **MUST** complete the System Sketch (Lug 6.1) as defined in `WAI-Guide.md`.

**Critical Questions:**
1.  Likelihood of Change?
2.  DRY?
3.  Source of Truth?
4.  Criticality?
5.  Testability?

### Step 4: Closing & Unblocking
When the Builder finishes:

```bash
WAI lug close a1b2
```

Now, if another Builder runs `wai ready`, they will see:
```
[P2] Create Login UI (Lug: c3d4) - Unblocked
```

The Hub automatically unblocks the next task.

## 3. Multi-Environment Synchronization

Agents likely run in different environments (VS Code vs Terminal vs Cloud).

- **FileSystem is King:** All state lives in `WAI-Spoke/`.
- **Sync Often:** Agents should run `WAI sync` (or the framework auto-syncs) to push/pull Hub state.
- **Locking:** WAI-Lugs uses optimistic locking. If two agents try to modify the same Lug, the second one will get a conflict error and must re-read.

## 4. Manager View (Reconciliation)

To see the heartbeat of your agent colony:

```bash
WAI status
```

This shows:
- Active Sessions (Who is working?)
- Recent High-Impact Decisions
- Blocked vs Unblocked Lugs

## Summary Checklist

- [ ] Define **Architect** and **Builder** roles.
- [ ] Architect breaks work into dependent **Lugs**.
- [ ] Builders use `wai ready` to find work.
- [ ] Builders fill out **System Sketch** before coding.
- [ ] Close Lugs to unblock the rest of the colony.
