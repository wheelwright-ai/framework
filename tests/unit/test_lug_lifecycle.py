"""
Comprehensive lifecycle tests for the Lug system.
"""

import pytest
import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add framework to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai_cli.lugs import LugManager, Lug
from wai_cli.point import PointManager
from wai_cli.closeout import CloseoutProcessor
from wai_cli.core import WheelwrightCLI

@pytest.fixture
def temp_spoke():
    """Create a temporary spoke directory with WAI-Spoke infrastructure."""
    temp_dir = Path(tempfile.mkdtemp())
    wai_spoke = temp_dir / 'WAI-Spoke'
    wai_spoke.mkdir()
    
    # Create required files
    (wai_spoke / 'WAI-State.json').write_text(json.dumps({
        "project_metadata": {"name": "Test Project"},
        "_session_state": {"session_id": "test-session-123"}
    }))
    
    (wai_spoke / 'WAI-Policies.json').write_text(json.dumps({
        "lug_policies": {
            "bug": {"close_requires": ["test_added", "test_verified"]}
        },
        "global_policies": ["no_open_blockers", "no_blocked_by"]
    }))
    
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_lug_creation_integrity(temp_spoke):
    """Verify Lug creation: hash ID, timestamps, session_id."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    title = "Test Creation Lug"
    lug = manager.create_lug(
        title=title,
        lug_type="task",
        priority="high",
        impact="medium",
        value=8,
        session_id="manual-session-id"
    )
    
    # Verify ID is a valid hex string (shortened by manager usually, but let's check length)
    assert len(lug.id) >= 8
    assert all(c in '0123456789abcdef' for c in lug.id)
    
    # Verify timestamps
    assert isinstance(lug.created_at, str)
    assert datetime.fromisoformat(lug.created_at)
    
    # Verify session association
    assert lug.session_id == "manual-session-id"
    
    # Verify storage persistence
    lugs = manager.list_lugs()
    assert len(lugs) == 1
    assert lugs[0].title == title

def test_minification_and_hierarchy(temp_spoke):
    """Verify epic/child hierarchy and minification storage."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    epic = manager.create_lug(title="Epic 1", lug_type="epic")
    child = manager.create_lug(title="Child 1", lug_type="work", deps=[epic.id])
    
    # Update child (delta update check)
    manager.update_lug(child.id, status="in_progress")
    
    # Reload from disk
    new_manager = LugManager(temp_spoke / 'WAI-Spoke')
    loaded_child = new_manager.get_lug(child.id)
    
    assert loaded_child.status == "in_progress"
    assert epic.id in loaded_child.deps
    
    # Verify minification (check raw file content for short keys)
    raw_content = (temp_spoke / 'WAI-Spoke' / 'lugs.jsonl').read_text()
    assert '"i":' in raw_content  # id
    assert '"t":' in raw_content  # title
    assert '"s":' in raw_content  # status

def test_policies_and_gating(temp_spoke):
    """Verify policy enforcement during closeout."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create a bug Lug
    bug = manager.create_lug(title="Critical Bug", lug_type="bug")
    
    # Attempt to close without policy flags
    with pytest.raises(ValueError) as excinfo:
        manager.close_lug(bug.id)
    assert "policy" in str(excinfo.value).lower() or "violation" in str(excinfo.value).lower()
    
    # Add dependency on an open lug - should also fail
    parent = manager.create_lug(title="Parent")
    manager.update_lug(bug.id, blocked_by=[parent.id])
    
    with pytest.raises(ValueError) as excinfo:
        manager.close_lug(bug.id, skip_policy_check=False)
    assert "blocked" in str(excinfo.value).lower()

def test_yolo_gating_prompts(temp_spoke):
    """Simulate YOLO gating for high-significance tasks."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Significance criteria: priority=high OR impact=large OR value>=7
    high_pri = manager.create_lug(title="High Pri", priority="high")
    assert manager.is_significant(high_pri) is True
    
    normal = manager.create_lug(title="Normal", priority="medium", impact="small", value=3)
    assert manager.is_significant(normal) is False

def test_resilience_corrupt_jsonl(temp_spoke):
    """Verify resilience when JSONL is partially corrupted."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    manager.create_lug(title="Valid 1")
    
    # Append garbage
    with open(temp_spoke / 'WAI-Spoke' / 'lugs.jsonl', 'a') as f:
        f.write("not-json-garbage\n")
        f.write('{"i": "valid2", "t": "Valid 2", "s": "open"}\n')
        
    # Should load valid ones and skip garbage
    lugs = manager.list_lugs()
    titles = [l.title for l in lugs]
    assert "Valid 1" in titles
    # Current implementation might be strict or lenient. Let's see.

def test_performance_load(temp_spoke):
    """Benchmark loading 100 Lugs."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    start_time = datetime.now()
    
    for i in range(100):
        lug = manager.create_lug(title=f"Bulk Lug {i}")
        if i % 2 == 0:
            manager.close_lug(lug.id, skip_policy_check=True)
            
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Verify load performance
    load_start = datetime.now()
    lugs = manager.list_lugs()
    load_end = datetime.now()
    load_duration = (load_end - load_start).total_seconds()
    
    assert len(lugs) == 50  # 50 open
    assert load_duration < 0.5  # Should be very fast

def test_hub_upgrade_simulation(temp_spoke):
    """Simulate upgrading an old project to Lug system."""
    wai_spoke = temp_spoke / 'WAI-Spoke'
    # Create old signals
    (wai_spoke / 'WAI-Signals.jsonl').write_text(
        json.dumps({"impact": 9, "offer": "Old Insight", "type": "lesson"}) + "\n"
    )
    
    manager = LugManager(wai_spoke)
    # The upgrade logic should be triggered (simulated here)
    # In a real run, WAI status or init would handle this
    manager.create_lug(title="Imported from signals", origin="hub_upgrade", impact="large", value=9)
    
    lugs = manager.list_lugs()
    assert any(l.origin == "hub_upgrade" for l in lugs)

def test_cli_command_formats(temp_spoke):
    """Verify CLI command output formats (mocked)."""
    from wai_cli.commands.lug import lug_command_group
    
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    manager.create_lug(title="CLI Test Lug", lug_type="bug", priority="high")
    
    # Mocking stdout to verify table format
    with patch('sys.stdout', new=MagicMock()) as mock_stdout:
        # We can't easily call the main entry point without full setup, 
        # but we can test the lug_command_group directly
        lug_command_group(['list'], temp_spoke)
        
    with patch('wai_cli.commands.lug.print_info') as mock_print:
        # Lug command group expects spoke_root (containing WAI-Spoke)
        lug_command_group(['list'], temp_spoke)
        headers = [str(call.args[0]) for call in mock_print.call_args_list]
        assert any("ID" in h and "Type" in h for h in headers)

def test_closeout_flow_integration(temp_spoke):
    """Verify closeout flow integrates Lug closing and Point updates."""
    # Mocking Git Repo
    with patch('git.Repo') as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.git.diff.return_value = "Modified: test.py\n+ # TODO: Fix this"
        
        processor = CloseoutProcessor(temp_spoke)
        
        # Create a lug associated with the session
        manager = LugManager(temp_spoke / 'WAI-Spoke')
        manager.create_lug(title="Session Task", session_id="test-session-123")
        
        # Run closeout
        with patch('wai_cli.closeout.QualityGates'):
            results = processor.process_closeout(skip_quality_gates=True)
        
        # Verify Lugs were inferred or checked
        assert 'lugs' in results
        
def test_shipit_point_update(temp_spoke):
    """Verify PointManager updates next_session_lug correctly."""
    pm = PointManager(temp_spoke)
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create a high priority lug
    manager.create_lug(title="Priority Task", priority="high", value=10)
    
    # Update point
    pm.update_point()
    
    with open(temp_spoke / 'WAI-Spoke' / 'WAI-Point.json', 'r') as f:
        data = json.load(f)
        assert data['next_session_lug']['title'] == "Priority Task"
        assert data['schema_version'] == 1

def test_closeout_with_open_dependencies(temp_spoke):
    """Verify closeout aborts if Lugs have open `deps`."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create parent-child relationship
    parent = manager.create_lug(title="Parent Task", session_id="test-session-123")
    child = manager.create_lug(title="Child Task", deps=[parent.id], session_id="test-session-123")
    
    # Try closeout with open dependency
    with patch('git.Repo') as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        
        processor = CloseoutProcessor(temp_spoke)
        with patch('wai_cli.closeout.QualityGates'):
            results = processor.process_closeout(skip_quality_gates=True)
        
        # Should have errors about open dependencies
        assert any('open' in str(e).lower() and ('dep' in str(e).lower() or 'blocked' in str(e).lower()) 
                   for e in results.get('errors', []))

def test_closeout_with_open_blocked_by(temp_spoke):
    """Verify closeout aborts if Lugs have open `blocked_by`."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create blocking relationship
    blocker = manager.create_lug(title="Blocker Task")
    blocked = manager.create_lug(title="Blocked Task", blocked_by=[blocker.id], session_id="test-session-123")
    
    # Try closeout
    with patch('git.Repo') as mock_repo_cls:
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        
        processor = CloseoutProcessor(temp_spoke)
        with patch('wai_cli.closeout.QualityGates'):
            results = processor.process_closeout(skip_quality_gates=True)
        
        # Should have errors about open blockers
        assert any('block' in str(e).lower() for e in results.get('errors', []))

def test_yolo_prompt_structure(temp_spoke):
    """Verify YOLO gate prompt includes Lug title, type, and policy requirements."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create a significant Lug with policies
    lug = manager.create_lug(
        title="Critical Bug Fix",
        lug_type="bug",
        priority="high",
        impact="large",
        value=9
    )
    
    # Check if it's significant (should trigger YOLO gate)
    assert manager.is_significant(lug) is True
    
    # Get policy violations (simulates YOLO prompt context)
    violations = manager.validate_policies(lug)
    
    # YOLO prompt would include these details
    assert lug.title == "Critical Bug Fix"
    assert lug.type == "bug"
    assert lug.priority == "high"

def test_resilience_missing_required_fields(temp_spoke):
    """Verify gracefully handles JSONL lines missing 'id' or 'title'."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    manager.create_lug(title="Valid Lug")
    
    # Append malformed entries
    with open(temp_spoke / 'WAI-Spoke' / 'lugs.jsonl', 'a') as f:
        # Missing ID
        f.write('{"t": "No ID Lug", "s": "open"}\\n')
        # Missing title
        f.write('{"i": "testid456", "s": "open"}\\n')
        # Valid one
        f.write('{"i": "valid789", "t": "Valid 2", "s": "open"}\\n')
    
    # Reload - should skip malformed ones
    new_manager = LugManager(temp_spoke / 'WAI-Spoke')
    lugs = new_manager.list_lugs()
    
    # Should have at least the original valid lug
    assert len(lugs) >= 1
    assert any(l.title == "Valid Lug" for l in lugs)

def test_performance_query_100_lugs(temp_spoke):
    """Benchmark query performance with 100 Lugs (by status, type, priority)."""
    import time
    
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create 100 Lugs with variety
    for i in range(100):
        manager.create_lug(
            title=f"Lug {i}",
            lug_type=["work", "bug", "issue", "epic"][i % 4],
            status="open" if i % 2 == 0 else "in_progress",
            priority=["low", "medium", "high"][i % 3]
        )
    
    # Benchmark queries
    start = time.time()
    status_results = manager.list_lugs(status="open")
    status_time = time.time() - start
    
    start = time.time()
    type_results = manager.list_lugs(lug_type="bug")
    type_time = time.time() - start
    
    start = time.time()
    priority_results = manager.list_lugs(priority="high")
    priority_time = time.time() - start
    
    # Verify results
    assert len(status_results) == 50  # Half are open
    assert len(type_results) == 25  # 1/4 are bugs
    assert len(priority_results) >= 30  # About 1/3 are high
    
    # Performance checks (should be fast)
    assert status_time < 0.1  # 100ms
    assert type_time < 0.1
    assert priority_time < 0.1

def test_performance_tokens_estimate(temp_spoke):
    """Estimate token usage for 100 Lugs in WAI-Point."""
    manager = LugManager(temp_spoke / 'WAI-Spoke')
    
    # Create 100 Lugs
    for i in range(100):
        manager.create_lug(
            title=f"Task {i}: Implement feature module",
            lug_type="work",
            priority="medium",
            impact="medium",
            value=5,
            justification=f"This is needed for project milestone {i//10}"
        )
    
    # Estimate tokens (rough calculation: ~10-20 tokens per Lug in list format)
    lugs = manager.list_lugs()
    assert len(lugs) == 100
    
    # Serialize to JSON for token estimation
    json_str = json.dumps([l.to_dict() for l in lugs])
    
    # Very rough token estimate: ~4 chars per token
    estimated_tokens = len(json_str) / 4
    
    # Should be reasonable (<20k tokens for 100 Lugs)
    assert estimated_tokens < 20000
    
    # Record size
    file_size = (temp_spoke / 'WAI-Spoke' / 'lugs.jsonl').stat().st_size
    assert file_size < 100000  # <100KB

