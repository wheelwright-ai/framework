# WAI Green Light

Resume execution from last autosave checkpoint.

## Instructions

1. **Read last unreconciled autosave lug** from WAI-Lugs.jsonl
   (ty=autosave, reconciled=false, latest by created_at)
   If none: "Nothing to resume — starting fresh"

2. **Output**:
   ```
   🟢 Green Light — Resuming

   Task: [task_context]
   Where we left off: [current_state]
   Progress: [completion_estimate]

   **Next step:** [next_step]
   Remaining: [what_remains]
   ```

3. **Continue execution** — proceed with next_step immediately.
