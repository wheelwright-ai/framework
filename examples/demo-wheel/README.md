# Demo Wheel

This is an example Wheelwright project demonstrating context persistence.

## Purpose

This demo shows:
- How `WAI-Spoke/` directory structure works
- What each WAI file contains
- How AI sessions maintain context

## Files

```
demo-wheel/
├── WAI-Spoke/
│   ├── WAI-State.json      # Machine-readable state
│   ├── WAI-State.md        # Human-readable context
│   ├── wheel-signals.jsonl  # High-impact learnings
│   └── kb-sync.json         # Hub sync status
└── README.md                # This file
```

## Using This Demo

1. Review each file in `WAI-Spoke/` to understand the structure
2. Note how the foundation defines project scope
3. See how decisions are logged with rationale
4. Observe the evolution log tracking changes

## Creating Your Own Wheel

Copy `templates/spoke/WAI-Spoke/` from the framework into your project root. See the [Quickstart Guide](../../docs/QUICKSTART.md) for setup instructions.

## Learn More

- [Wheelwright README](../../README.md)
- [Quickstart Guide](../../docs/QUICKSTART.md)
- [Framework Overview](../../docs/architecture/FRAMEWORK_OVERVIEW.md)

---

*Wheelwright Framework - wheelwright.ai*
