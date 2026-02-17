# WAI Learn

**Automatic inbox processing on wakeup.**

---

## Concept

Learning is **passive and automatic** — it happens when a node wakes up and processes its inbox.

```
┌─────────────────────────────────────────────────────────────┐
│  teach = PUSH (active)                                      │
│  learn = PULL (passive, automatic on wakeup)                │
└─────────────────────────────────────────────────────────────┘
```

**You don't invoke `/wai-learn`** — learning happens automatically during `/wai` wakeup.

---

## How Learning Works

### On Wakeup (`/wai`)

1. **Check inbox** — `WAI-Spoke/lugs/inbox/`
2. **Process pending lugs** — tasks, signals, configs
3. **Report what was learned** — show new items in briefing
4. **Mark as processed** — move to processed/ or update status

### What Gets Learned

| Lug Type | Processing |
|----------|------------|
| `task` | Added to active work queue |
| `signal` | Integrated into knowledge base |
| `config` | Applied to node configuration |
| `task-result` | Updates task status in registry |
| `delivery_confirmation` | Acknowledges successful delivery |

---

## The Teach/Learn Protocol

```
NODE A                              NODE B
┌──────────────┐                    ┌──────────────┐
│   outbox/    │ ──[A teaches B]──► │   inbox/     │
│              │                    │              │
│   inbox/     │ ◄──[B teaches A]── │   outbox/    │
└──────────────┘                    └──────────────┘

• A teaches B = A pushes A's outbox → B's inbox
• B learns = B processes B's inbox on wakeup (automatic)
```

### Direction Clarity

| Verb | Direction | Actor | Action |
|------|-----------|-------|--------|
| **teach** | push | sender | "I teach you" = I send to your inbox |
| **learn** | pull | receiver | "I learn" = I process my inbox |

---

## To Send Something

Use **teach**, not learn:

```bash
# Framework sends to spoke
/wai-teach basher

# Spoke sends to hub (teach hub)
/wai-teach hub
```

Teach pushes from your `outbox/` to target's `inbox/`.

---

## To Receive Something

Just wake up:

```bash
/wai
```

Wakeup automatically:
1. Checks your `inbox/`
2. Processes any pending lugs
3. Shows what was learned in the briefing

---

## Related Commands

- `/wai` — Wakeup (triggers automatic learning)
- `/wai-teach` — Push your outbox to target's inbox

---

*Learn = Automatic. Teach = Intentional.*
