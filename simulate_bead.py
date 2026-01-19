import json
from pathlib import Path
from wai_cli.closeout import CloseoutProcessor
from wai_cli.lugs import LugManager

# Setup mock data using real classes
spoke_dir = Path(".").resolve()
processor = CloseoutProcessor(spoke_dir)

# Mock session summary
summary = {
    'summary': "Bead Integration Test",
    'files_modified': ["test_file.py"],
    'turns': 5
}

# Override state to simulate an active session
state_path = spoke_dir / "WAI-Spoke/WAI-State.json"
original_state = state_path.read_text()
state = json.loads(original_state)
state['_session_state']['current_session'] = {
    'session_id': "sim-session-001",
    'started_at': "2026-01-01T00:00:00"
}
state_path.write_text(json.dumps(state, indent=2))

# Run finalize (which triggers bead recording)
print("Running _finalize_closeout...")
try:
    processor._finalize_closeout(summary)
    print("Finalize executed.")
except Exception as e:
    print(f"Error: {e}")

# Check for bead file
sessions_file = spoke_dir / "WAI-Spoke/lug-sessions.jsonl"
if sessions_file.exists():
    print(f"Success: {sessions_file} exists.")
    print("Content:")
    print(sessions_file.read_text())
else:
    print("Failure: lug-sessions.jsonl not found.")

# Restore state
state_path.write_text(original_state)
