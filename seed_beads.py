import json
from pathlib import Path
from wai_cli.lugs import LugManager

# Setup correct path for test
wai_spoke = Path("WAI-Spoke").resolve()
wai_spoke.mkdir(exist_ok=True)
sessions_file = wai_spoke / "lug-sessions.jsonl"

# Create dummy beads
# Clear first
if sessions_file.exists():
    sessions_file.unlink()

manager = LugManager(wai_spoke)
b1 = manager.record_session_bead("s1", "Bead 1")
b2 = manager.record_session_bead("s2", "Bead 2", parent_id=b1['bead_id'])

print(f"Created 2 beads in {sessions_file}")
