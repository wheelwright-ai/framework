
import json
import datetime
import os

state_file = 'WAI-Spoke/WAI-State.json'

# Check if WAI-Spoke directory exists, if not, create it
wai_spoke_dir = os.path.dirname(state_file)
if not os.path.exists(wai_spoke_dir):
    os.makedirs(wai_spoke_dir)

# Read the current content of WAI-State.json
with open(state_file, 'r') as f:
    state_data = json.load(f)

# Update the _session_state fields
timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
state_data['_session_state']['last_modified_by'] = 'agent'
state_data['_session_state']['last_modified_at'] = timestamp
state_data['_session_state']['last_closeout'] = timestamp

# Write the updated content back to WAI-State.json
with open(state_file, 'w') as f:
    json.dump(state_data, f, indent=2)

print(json.dumps(state_data, indent=2))
