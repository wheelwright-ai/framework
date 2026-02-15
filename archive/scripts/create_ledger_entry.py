import json
import datetime
import hashlib
import os

ledger_file = 'WAI-Spoke/WAI-Ledger.jsonl'
content = 'Verify WAI v2 working'

# Check if WAI-Spoke directory exists, if not, create it
wai_spoke_dir = os.path.dirname(ledger_file)
if not os.path.exists(wai_spoke_dir):
    os.makedirs(wai_spoke_dir)

timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
entry_id = hashlib.sha256(content.encode()).hexdigest()[:12]

new_entry = {
    'id': f'led-{entry_id}',
    'timestamp': timestamp,
    'session_id': 'test-session-001',
    'type': 'request',
    'content': content,
    'source': 'agent',
    'status': 'open',
    'lug_ids': []
}

# Ensure the JSON string itself has the newline
json_line = json.dumps(new_entry) + '\n'

with open(ledger_file, 'a') as f:
    f.write(json_line)

print(json.dumps(new_entry, indent=2))