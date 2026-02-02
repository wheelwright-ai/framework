"""
Unit tests for Lug session linkage and attribution.

Tests:
- Session auto-linking from WAI-State
- get_session_lugs() filtering
- Multi-session Lug isolation
- Session metadata tracking (who/when/mode/model)
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai.lugs import LugManager, Session


@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    wai_spoke = temp_dir / 'WAI-Spoke'
    wai_spoke.mkdir()
    
    # Create WAI-State.json with session info
    state = {
        "project_metadata": {"name": "Test Project"},
        "_session_state": {
            "current_session": {
                "session_id": "auto-session-123",
                "started_at": datetime.now().isoformat(),
                "who": "test-agent",
                "mode": "YOLO",
                "model": "claude-3.5-sonnet"
            }
        }
    }
    (wai_spoke / 'WAI-State.json').write_text(json.dumps(state))
    
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_session_auto_linking(temp_spoke_dir):
    """Verify Lugs inherit session_id from WAI-State when not specified."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create Lug without specifying session_id
    lug = manager.create_lug(
        title="Auto Session Test",
        lug_type="task"
    )
    
    # Should auto-link to session from WAI-State
    assert lug.session_id == "auto-session-123"
    
    # Verify persistence
    new_manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    loaded_lug = new_manager.get_lug(lug.id)
    assert loaded_lug.session_id == "auto-session-123"


def test_get_session_lugs(temp_spoke_dir):
    """Verify get_session_lugs() correctly filters by session_id."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create Lugs for different sessions
    lug1 = manager.create_lug(
        title="Session A Lug 1",
        session_id="session-a"
    )
    lug2 = manager.create_lug(
        title="Session A Lug 2",
        session_id="session-a"
    )
    lug3 = manager.create_lug(
        title="Session B Lug 1",
        session_id="session-b"
    )
    
    # Get session A Lugs
    session_a_lugs = manager.get_session_lugs("session-a")
    assert len(session_a_lugs) == 2
    assert all(l.session_id == "session-a" for l in session_a_lugs)
    titles = [l.title for l in session_a_lugs]
    assert "Session A Lug 1" in titles
    assert "Session A Lug 2" in titles
    
    # Get session B Lugs
    session_b_lugs = manager.get_session_lugs("session-b")
    assert len(session_b_lugs) == 1
    assert session_b_lugs[0].session_id == "session-b"
    assert session_b_lugs[0].title == "Session B Lug 1"


def test_multi_session_lugs(temp_spoke_dir):
    """Create Lugs across multiple sessions and verify isolation."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create 10 Lugs across 3 sessions
    for i in range(10):
        session_id = f"session-{i % 3}"
        manager.create_lug(
            title=f"Lug {i}",
            session_id=session_id
        )
    
    # Verify counts per session
    session_0_lugs = manager.get_session_lugs("session-0")
    session_1_lugs = manager.get_session_lugs("session-1")
    session_2_lugs = manager.get_session_lugs("session-2")
    
    assert len(session_0_lugs) == 4  # 0, 3, 6, 9
    assert len(session_1_lugs) == 3  # 1, 4, 7
    assert len(session_2_lugs) == 3  # 2, 5, 8
    
    # Verify no cross-contamination
    all_session_ids_0 = [l.session_id for l in session_0_lugs]
    assert all(sid == "session-0" for sid in all_session_ids_0)


def test_session_metadata_tracking(temp_spoke_dir):
    """Verify session who/when/mode/model tracking."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create a session
    session_data = {
        "session_id": "meta-session-456",
        "who": "claude-agent",
        "when": datetime.now().isoformat(),
        "mode": "ASSISTED",
        "model": "claude-3-opus",
        "duration": 3600.5
    }
    session = manager.create_session(**session_data)
    
    # Verify session object
    assert session.session_id == "meta-session-456"
    assert session.who == "claude-agent"
    assert session.mode == "ASSISTED"
    assert session.model == "claude-3-opus"
    assert session.duration == 3600.5
    assert isinstance(session.when, str)
    assert datetime.fromisoformat(session.when)
    
    # Verify persistence in sessions.jsonl
    sessions_file = temp_spoke_dir / 'WAI-Spoke' / 'sessions.jsonl'
    assert sessions_file.exists()
    
    with open(sessions_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        session_json = json.loads(lines[0])
        assert session_json['session_id'] == "meta-session-456"
        assert session_json['who'] == "claude-agent"
        assert session_json['mode'] == "ASSISTED"
        assert session_json['model'] == "claude-3-opus"
    
    # Verify reload
    new_manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    assert "meta-session-456" in new_manager.sessions
    loaded_session = new_manager.sessions["meta-session-456"]
    assert loaded_session.who == "claude-agent"
    assert loaded_session.mode == "ASSISTED"


def test_session_id_propagation_through_updates(temp_spoke_dir):
    """Verify session_id is preserved across Lug updates."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create Lug with explicit session_id
    lug = manager.create_lug(
        title="Update Test Lug",
        session_id="persistent-session"
    )
    
    initial_session_id = lug.session_id
    assert initial_session_id == "persistent-session"
    
    # Update various fields
    manager.update_lug(lug.id, status="in_progress")
    manager.update_lug(lug.id, priority="high")
    manager.update_lug(lug.id, value=9)
    
    # Verify session_id persists
    updated_lug = manager.get_lug(lug.id)
    assert updated_lug.session_id == "persistent-session"
    
    # Reload from disk
    new_manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    loaded_lug = new_manager.get_lug(lug.id)
    assert loaded_lug.session_id == "persistent-session"


def test_explicit_session_id_overrides_auto_link(temp_spoke_dir):
    """Verify explicit session_id parameter overrides auto-linking from WAI-State."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # WAI-State has auto-session-123, but we override
    lug = manager.create_lug(
        title="Override Test",
        session_id="explicit-override-789"
    )
    
    # Should use explicit session_id, not the auto one from WAI-State
    assert lug.session_id == "explicit-override-789"
    assert lug.session_id != "auto-session-123"


def test_get_session_lugs_empty_result(temp_spoke_dir):
    """Verify get_session_lugs returns empty list for non-existent session."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create some Lugs
    manager.create_lug(title="Lug 1", session_id="session-exists")
    manager.create_lug(title="Lug 2", session_id="session-exists")
    
    # Query non-existent session
    result = manager.get_session_lugs("session-does-not-exist")
    assert isinstance(result, list)
    assert len(result) == 0
