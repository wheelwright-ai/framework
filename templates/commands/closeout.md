# WAI Closeout Protocol

This document outlines the standard procedure for an AI agent to perform a `closeout` operation. This is an internal directive, not a shell command.

**Objective:** To conclude a work session by capturing learnings, updating state, versioning the work, and committing it to the repository, ensuring a clean and persistent state for the next session.

### Closeout Procedure

1.  **Signal Extraction (P6, P7):**
    *   Review the current session log (`WAI-Spoke/WAI-Session-Log.jsonl`).
    *   Identify any decisions, learnings, or observations with a high impact (impact >= 8).

2.  **Lug Creation (P6, P7):**
    *   For each high-impact signal identified, create a new lug.
    *   Append the new lug as a single JSON line to `WAI-Spoke/WAI-Lugs.jsonl`.

3.  **Increment Version (P7):**
    *   Read `WAI-Spoke/WAI-State.json`.
    *   Increment the patch number of the `wheelwright.version` field (e.g., 3.1.0 -> 3.1.1).

4.  **State Update (P1):**
    *   Update the `_session_state.last_closeout` field with the current UTC timestamp in ISO 8601 format.
    *   Write the modified content (with updated version and timestamp) back to `WAI-State.json`.

5.  **Session Log Archival (P1):**
    *   Clear the contents of `WAI-Spoke/WAI-Session-Log.jsonl` to prepare it for the next session.

6.  **Summarize (P2, P7):**
    *   Generate a concise, markdown-formatted summary of the session's activities.
    *   Include the new version number and links to any new lugs created.
    *   Present this summary to the user.

7.  **Stage, Commit, and Push (P7):**
    *   Stage all modified files (`git add .`).
    *   Commit the changes using the session summary as the commit message (`git commit -m "WAI Session Closeout: [Summary]"`).
    *   **Ask the user for explicit confirmation** before pushing to the remote repository.
    *   If confirmed, push the changes (`git push`).

**Success Criteria:**
*   High-impact signals are persisted as lugs.
*   The project version is incremented.
*   `WAI-State.json` is updated.
*   `WAI-Session-Log.jsonl` is cleared.
*   All changes are committed with a descriptive message.
*   The user is prompted before any changes are pushed to the remote.