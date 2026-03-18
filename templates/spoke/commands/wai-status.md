# WAI Status

Health check with hub connection, sync age, session health, recommendations.

## What It Does

Quick snapshot of project health:

1. **Hub connection** — Connected? Last sync when?
2. **Session health** — Current turn count, context usage
3. **Recommendations** — What action to take (closeout? teach? sync?)

Lightweight check, complements full /wai briefing.

## When to Use

- **Quick check:** After 10+ turns
- **Uncertain sync:** Hub out of date?
- **Decision point:** Should I closeout or continue?
- **Health monitoring:** Periodic during long sessions

## How It Works

1. Check hub connection status from WAI-State.json
2. Calculate sync age (now - last_sync)
3. Check session metrics:
   - Current turn count
   - Context usage percentage
   - Files modified in this session
4. Generate recommendations based on thresholds:
   - context > 70% → recommend closeout
   - hub_sync > 7 days → recommend teach
   - turn_count > 20 → recommend context check

## Example

User: /wai-status

AI Output:


Another Example (Needs Action):

User: /wai-status

AI Output:


## Related Skills

- /wai-time — Detailed context usage
- /wai (Step 9b: auto-teach on closeout) — Sync with hub
- /wai-closeout — End session ceremony
