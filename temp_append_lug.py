import json

lug_file_path = "WAI-Spoke/WAI-Lugs.jsonl"

new_lug = {
    "i": "agent-learning-2026-02-15-file-mod-brittleness",
    "t": "Agent Failure Mode: Brittle Code Modification & File Integrity Management",
    "ty": "learning",
    "s": "open",
    "status": "open",
    "description": """The agent exhibited a recurring failure when attempting multi-line code modifications and file content reconstruction in Python files (`wai/teach_reconciliation.py`, `wai/hub.py`). This was primarily due to:
1.  **Brittleness of `replace` tool:** Inability to reliably match and replace large, multi-line blocks of code due to subtle whitespace, indentation, and newline differences. This tool proved insufficient for complex Python refactoring.
2.  **Misunderstanding `write_file` behavior:** Repeatedly overwriting entire file content when the intention was to append or make targeted insertions, leading to loss of file imports, other functions, and general file corruption.
3.  **Inadequate error recovery:** Failure to properly identify and correct the root cause of these issues in a timely manner, leading to prolonged unproductive loops and wasted compute cycles.
4.  **Lack of robust Python code manipulation strategy:** Reliance on string-based manipulation rather than a more robust method for Python code, such as AST manipulation or line-by-line programmatic reconstruction that accounts for full file context.

**Impact:** Significant delay in task completion, waste of user's time and agent's tokens, and failure to maintain project integrity during critical development phases.""",
    "priority": "high",
    "impact": 10,
    "value": 1,
    "scope": "agent-capability",
    "tags": ["agent-failure", "code-modification", "file-integrity", "tool-limitation", "learning", "process-improvement"],
    "created_at": "2026-02-15T00:00:00Z",
    "blocks": [],
    "blocked_by": []
}

with open(lug_file_path, "a") as f:
    f.write("\n" + json.dumps(new_lug))

print("Successfully appended lug to WAI-Spoke/WAI-Lugs.jsonl")