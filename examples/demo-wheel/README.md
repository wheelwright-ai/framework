# Demo Wheel

This is an example Wheelwright project demonstrating context persistence.

## Purpose

This demo shows:
- How `.wwai/` directory structure works
- What each WWAI file contains
- How AI sessions maintain context

## Files

```
demo-wheel/
├── .wwai/
│   ├── WWAI-State.json      # Machine-readable state
│   ├── WWAI-State.md        # Human-readable context
│   ├── wheel-signals.jsonl  # High-impact learnings
│   └── kb-sync.json         # Hub sync status
└── README.md                # This file
```

## Using This Demo

1. Review each file in `.wwai/` to understand the structure
2. Note how the foundation defines project scope
3. See how decisions are logged with rationale
4. Observe the evolution log tracking changes

## Creating Your Own Wheel

```bash
cd your-project
wwai init
```

## Learn More

- [Wheelwright README](../../README.md)
- [Quickstart Guide](../../docs/QUICKSTART.md)
- [Framework Overview](../../docs/architecture/FRAMEWORK_OVERVIEW.md)

---

*Wheelwright Framework - wheelwright.ai*
