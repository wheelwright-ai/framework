import json
import datetime
import os

lug_file = 'WAI-Spoke/WAI-Lugs.jsonl'

# Check if WAI-Spoke directory exists, if not, create it
wai_spoke_dir = os.path.dirname(lug_file)
if not os.path.exists(wai_spoke_dir):
    os.makedirs(wai_spoke_dir)

new_lug_2 = {
    "id": "gemini-ledger-verified",
    "type": "decision",
    "title": "WAI-Ledger.jsonl append-only pattern verified",
    "status": "open",
    "description": "Successfully created and appended a test ledger entry to WAI-Spoke/WAI-Ledger.jsonl, confirming its append-only nature and the pattern for recording commitments.",
    "impact": 8,
    "created_by": "agent",
    "node": "wheelwright/framework",
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "tags": ["ledger", "append-only", "verification", "critical-function"]
}

# Ensure the JSON string itself has the newline
json_line_2 = json.dumps(new_lug_2) + '\n'

with open(lug_file, 'a') as f:
    f.write(json_line_2)

print(json.dumps(new_lug_2, indent=2))