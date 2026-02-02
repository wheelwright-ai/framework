"""
Integration test for Lug closeout and shipit flow.
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil
import sys
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai.lugs import LugManager
from wai.closeout import CloseoutProcessor
from wai.point import PointManager
from wai.core import check_spoke_initialized

@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for integration tests."""
    temp_dir = Path(tempfile.mkdtemp())
    # Mock a WAI spoke structure
    wai_spoke = temp_dir / 'WAI-Spoke'
    wai_spoke.mkdir()
    
    # Create required files
    (wai_spoke / 'WAI-State.json').write_text(json.dumps({
        "framework": {"version": "2.0.1"},
        "project": {"name": "Test Project"},
        "_session_state": {
            "current_session": {
                "session_id": "test-session-123",
                "started_at": datetime.now().isoformat()
            }
        }
    }))
    (wai_spoke / 'WAI-State.md').write_text("# State")
    (wai_spoke / 'WAI-Guide.md').write_text("# Guide")
    (wai_spoke / 'WAI-Signals.jsonl').write_text("")
    (wai_spoke / 'WAI-Point.json').write_text("{}")
    
    # Initialize git
    from git import Repo
    repo = Repo.init(temp_dir)
    repo.index.add(['WAI-Spoke/WAI-State.json', 'WAI-Spoke/WAI-State.md', 'WAI-Spoke/WAI-Guide.md'])
    repo.index.commit("Initial commit")
    
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_lug_policy_gate_in_closeout(temp_spoke_dir):
    """Test that closeout respects Lug policy gates."""
    # Create a policy that requires "test_added" for "bug" type
    policies = {
        "lug_policies": {
            "bug": {"close_requires": ["test_added"]}
        }
    }
    (temp_spoke_dir / 'WAI-Spoke' / 'WAI-Policies.json').write_text(json.dumps(policies))
    
    manager = LugManager(temp_spoke_dir)
    # Create a bug Lug for this session
    lug = manager.create_lug(
        title="Bug for testing",
        lug_type="bug",
        extras={"session_id": "test-session-123"}
    )
    
    processor = CloseoutProcessor(temp_spoke_dir)
    # Run closeout - should find violation
    results = processor.process_closeout(interactive=False)
    
    assert any("aborted due to Lug policy violations" in e for e in results.get('errors', []))

def test_lug_archiving_in_shipit_logic(temp_spoke_dir):
    """Test that Lugs are correctly archived during (simulated) shipit logic."""
    manager = LugManager(temp_spoke_dir)
    # Create a task Lug for this session (no policies)
    lug = manager.create_lug(
        title="Simple task",
        lug_type="work",
        extras={"session_id": "test-session-123"}
    )
    
    processor = CloseoutProcessor(temp_spoke_dir)
    # Closeout should pass
    results = processor.process_closeout(interactive=False)
    assert not results.get('errors')
    
    # Simulate shipit Lug closing logic as found in core.py
    # (Since core.py is a CLI class, we test the logic here)
    session_lugs = manager.get_session_lugs("test-session-123")
    assert len(session_lugs) == 1
    
    for l in session_lugs:
        manager.close_lug(l.id, summary="Closed via test")
        
    # Verify it is closed and archived
    assert lug.id not in manager.lugs
    assert (temp_spoke_dir / 'WAI-Spoke' / 'lugs-closed.jsonl').exists()

def test_point_update_in_closeout(temp_spoke_dir):
    """Test that WAI-Point is updated during closeout."""
    processor = CloseoutProcessor(temp_spoke_dir)
    processor.process_closeout(interactive=False)
    
    point_file = temp_spoke_dir / 'WAI-Spoke' / 'WAI-Point.json'
    assert point_file.exists()
    point_data = json.loads(point_file.read_text())
    assert point_data.get('project', {}).get('name') == "Test Project"
