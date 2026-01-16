# WAI Wakeup

Load Wheelwright context and brief the user.

## Instructions

1. Read these files to load context:
   - `WAI-Spoke/WAI-Guide.md` (behavioral guidelines)
   - `WAI-Spoke/WAI-State.json` (project state, decisions)

2. Run integration verification:
   - Check if hub is connected (`wheelwright.hub_path` in WAI-State.json)
   - Check days since last sync (`wheelwright.development_health.days_since_sync`)
   - Check for uncommitted changes (`git status`)
   - Check if foundation is complete (`_project_foundation.completed`)

3. Check multi-environment sessions:
   - Scan `WAI-Spoke/sessions/` for other environment logs
   - Note if other environments have recent activity
   - Auto-detect current environment (tool + machine)
   - Start session for current environment if not already tracking

4. Brief the user with this format:
   ```
   **Wheelwright Ready** - [Project Name]
   Last session: [date] by [AI name]
   Environment: [tool] on [machine] ([os])

   [Any warnings: sync stale, uncommitted changes, foundation incomplete]
   [If other environments active: "Also active: cursor on desktop (2 days ago)"]

   **Commands:** Status | Time | Rules | Closeout | Shipit
   ```

5. If issues detected, prompt user with fix options.
