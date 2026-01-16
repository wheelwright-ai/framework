# WAI Shipit

Closeout + git commit in one command.

## Instructions

1. First, execute the full Closeout protocol (see `/wai-closeout`)

2. After closeout completes, run git operations:
   ```bash
   git add -A
   git status
   ```

3. Generate a commit message summarizing the session:
   - What was accomplished
   - Key decisions made
   - Reference session number

4. Commit with the generated message:
   ```bash
   git commit -m "Session closeout: [brief summary]"
   ```

5. Ask user if they want to push:
   ```
   **Committed.** Push to remote? (yes/no)
   ```

Output format:
```
**Shipit Complete**

Closeout: Done
Commit: [commit hash]
Message: "Session closeout: [summary]"

Push to remote? (yes/no)
```
