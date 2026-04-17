# What is WAI?

**WAI** (Wheelwright AI) is an agent communication protocol. It's how AI agents talk to each other, show their work, and build institutional memory.

## Core Principles

1. **Agents communicate through files** — not APIs, not databases, files
2. **Show your work** — every agent action produces a Lug (audit trail)
3. **Institutional memory** — decision Lugs capture conductor judgment, sub-agents learn over time
4. **Data protection** — WAI-Integrity.md prevents Hub destruction
5. **Multi-agent colonies** — cheap specialists + expensive orchestrator

## The Two Primitives

### Skills

A Skill is a sub-agent with a contract. It declares what it does, when it fires, what model it needs, and what it produces.

See: [skills/overview.md](../skills/overview.md)

### Lugs

A Lug is an actionable record. Diagnosis, prescription, decision, observation, task, signal.

See: [lugs/overview.md](../lugs/overview.md)

## Architecture

Hub-and-spoke model. Hub is shared memory across projects. Spokes are per-project extensions.

See: [architecture.md](./architecture.md)

## For Newcomers

Start here:
1. Read this file (you're here)
2. Read [core-concepts.md](./core-concepts.md)
3. Read [quickstart.md](./quickstart.md)
4. Explore [skills/](../skills/) and [lugs/](../lugs/)

## For Agents

Read the specs at repo root:
- WAI-Lug-Schema-Spec.md
- WAI-Skill-Contract-Spec.md
- WAI-v2-Implementation-Plan-Revised.md

Then read WAI-Integrity.md for data protection rules.
