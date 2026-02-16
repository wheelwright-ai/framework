import json
import datetime
import os

lug_file = 'WAI-Spoke/WAI-Lugs.jsonl'

# Check if WAI-Spoke directory exists, if not, create it
wai_spoke_dir = os.path.dirname(lug_file)
if not os.path.exists(wai_spoke_dir):
    os.makedirs(wai_spoke_dir)

new_lug_1 = {
    "id": "gemini-manifest-inference",
    "type": "decision",
    "title": "Inferred node_path and framework_version due to missing WAI-Spoke/WAI-Manifest.yaml",
    "status": "open",
    "description": "WAI-Spoke/WAI-Manifest.yaml was requested but not found. Inferred node_path as current working directory and framework_version from WAI-Spoke/WAI-State.json. This could be a critical issue if WAI-Manifest.yaml is mandatory or has other essential fields.",
    "impact": 8,
    "created_by": "agent",
    "node": "wheelwright/framework",
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "tags": ["manifest", "missing-file", "inference", "state-management"]
}

# Ensure the JSON string itself has the newline
json_line_1 = json.dumps(new_lug_1) + '\n'

with open(lug_file, 'a') as f:
    f.write(json_line_1)

print(json.dumps(new_lug_1, indent=2))