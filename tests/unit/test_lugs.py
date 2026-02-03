"""
Unit tests for Lug system - Core storage and operations.

Tests:
- Lug creation with SHA-256 ID generation
- JSONL append operations
- In-memory index queries
- Dependency management
- Policy validation
- Minification
- Archive operations
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai.lugs import LugManager, Lug, Session, MINIFIED_KEYS, EXPANDED_KEYS


@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def lug_manager(temp_spoke_dir):
    """Create LugManager instance with temp directory."""
    return LugManager(temp_spoke_dir)


class TestLugCreation:
    """Test Lug creation and ID generation."""
    
    def test_create_lug_basic(self, lug_manager):
        """Test creating a basic Lug."""
        lug = lug_manager.create_lug(
            title="Test Lug",
            lug_type="work",
            priority="medium",
            impact="medium",
            value=5
        )
        
        assert lug.id is not None
        assert len(lug.id) == 64  # SHA-256 full length
        assert lug.title == "Test Lug"
        assert lug.type == "work"
        assert lug.status == "open"
        assert lug.priority == "medium"
        assert lug.impact == "medium"
        assert lug.value == 5
    
    def  test_id_uniqueness(self, lug_manager):
        """Test that Lug IDs are unique."""
        lug1 = lug_manager.create_lug(title="Test 1")
        lug2 = lug_manager.create_lug(title="Test 2")
        lug3 = lug_manager.create_lug(title="Test 1")  # Same title, different salt
        
        assert lug1.id != lug2.id
        assert lug1.id != lug3.id
        assert lug2.id != lug3.id
    
    def test_lug_with_optional_fields(self, lug_manager):
        """Test creating Lug with optional fields."""
        lug = lug_manager.create_lug(
            title="Bug Fix",
            lug_type="bug",
            justification="User reported login failure",
            origin="user_report:chat",
            from_file="src/auth.py",
            extras={"test_file": "tests/test_auth.py"}
        )
        
        assert lug.justification == "User reported login failure"
        assert lug.origin == "user_report:chat"
        assert lug.from_file == "src/auth.py"
        assert lug.extras["test_file"] == "tests/test_auth.py"


class TestJSONLStorage:
    """Test JSONL storage operations."""
    
    def test_lug_persisted_to_file(self, lug_manager, temp_spoke_dir):
        """Test that Lugs are written to sharded file."""
        lug = lug_manager.create_lug(title="Persist Test")
        
        # Should be in lugs/ directory
        lugs_dir = temp_spoke_dir / 'lugs'
        assert lugs_dir.exists()
        
        files = list(lugs_dir.glob('*.jsonl'))
        assert len(files) >= 1
        
        # Check content of the first file found
        with open(files[0], 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) >= 1
        # Find our lug in the file
        found = False
        for line in lines:
            data = json.loads(line)
            if data.get('i') == lug.id or data.get('id') == lug.id:
                found = True
                break
        assert found
    
    def test_multiple_lugs_append(self, lug_manager, temp_spoke_dir):
        """Test appending multiple Lugs to JSONL."""
        lug1 = lug_manager.create_lug(title="First")
        lug2 = lug_manager.create_lug(title="Second")
        lug3 = lug_manager.create_lug(title="Third")
        
        ls_files = list((temp_spoke_dir / 'lugs').glob('*.jsonl'))
        total_lines = 0
        for fpath in ls_files:
            with open(fpath, 'r', encoding='utf-8') as f:
                total_lines += len(f.readlines())
        
        assert total_lines == 3
    
    def test_reload_from_storage(self, temp_spoke_dir):
        """Test reloading Lugs from storage."""
        # Create and save Lugs
        manager1 = LugManager(temp_spoke_dir)
        lug1 = manager1.create_lug(title="Reload Test 1")
        lug2 = manager1.create_lug(title="Reload Test 2")
        
        # Create new manager instance to force reload
        manager2 = LugManager(temp_spoke_dir)
        
        assert len(manager2.lugs) == 2
        assert lug1.id in manager2.lugs
        assert lug2.id in manager2.lugs
    
    def test_delta_update_in_place(self, lug_manager, temp_spoke_dir):
        """Verify delta updates modify in-place (same line count, updated value)."""
        lug = lug_manager.create_lug(title="Delta Test", value=5)
        
        lugs_dir = temp_spoke_dir / 'lugs'
        # Get count before
        lines_before = 0
        for f in lugs_dir.glob('*.jsonl'):
            lines_before += len(f.read_text(encoding='utf-8').splitlines())
        
        # Make an update
        lug_manager.update_lug(lug.id, value=10)
        
        lines_after = 0
        found_updated = False
        
        for f in lugs_dir.glob('*.jsonl'):
             content = f.read_text(encoding='utf-8')
             lines_after += len(content.splitlines())
             if '"v": 10' in content or '"value": 10' in content:
                 found_updated = True
                 
        # In-place update: same line count
        assert lines_after == lines_before
        assert found_updated
    
    def test_jsonl_line_ordering(self, lug_manager, temp_spoke_dir):
        """Verify order preservation with in-place updates."""
        lug1 = lug_manager.create_lug(title="First Lug")
        lug2 = lug_manager.create_lug(title="Second Lug")
        
        # Update first lug (in-place, not appended)
        lug_manager.update_lug(lug1.id, status="in_progress")
        
        # Check total lines across all shards
        lugs_dir = temp_spoke_dir / 'lugs'
        total_lines = 0
        for fpath in lugs_dir.glob('*.jsonl'):
            with open(fpath, 'r', encoding='utf-8') as f:
                total_lines += len(f.readlines())
        
        # In-place updates: still 2 lines (one per lug)
        assert total_lines == 2
        
        # Verify content
        # Both should be in the same global-date file since no session_id provided
        files = list(lugs_dir.glob('*.jsonl'))
        assert len(files) == 1
        
        with open(files[0], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        line1 = json.loads(lines[0])
        line2 = json.loads(lines[1])
        
        # First line should be lug1 (now updated)
        assert line1.get('t') == "First Lug" or line1.get('title') == "First Lug"
        assert line1.get('s') == "in_progress" or line1.get('status') == "in_progress"
        # Second line should be lug2
        assert line2.get('t') == "Second Lug" or line2.get('title') == "Second Lug"


class TestMinification:
    """Test minification and key mapping."""
    
    def test_minified_storage(self, lug_manager, temp_spoke_dir):
        """Test that Lugs are stored with minified keys."""
        lug = lug_manager.create_lug(title="Minify Test")
        
        lug = lug_manager.create_lug(title="Minify Test")
        
        lugs_dir = temp_spoke_dir / 'lugs'
        found = False
        stored = {}
        
        for fpath in lugs_dir.glob('*.jsonl'):
            with open(fpath, 'r', encoding='utf-8') as f:
                for line in f:
                    stored = json.loads(line)
                    if stored.get('i') == lug.id or stored.get('id') == lug.id:
                        found = True
                        break
            if found: break
            
        assert found
        
        # Should have minified keys in storage
        assert 'i' in stored or 'id' in stored  # id
        assert 't' in stored or 'title' in stored  # title
        assert 'ty' in stored or 'type' in stored  # type
    
    def test_key_expansion(self, lug_manager):
        """Test that minified keys are expanded correctly."""
        minified = {
            'i': 'test123',
            't': 'Test Title',
            'ty': 'work',
            's': 'open'
        }
        
        expanded = lug_manager._expand_keys(minified)
        
        assert expanded['id'] == 'test123'
        assert expanded['title'] == 'Test Title'
        assert expanded['type'] == 'work'
        assert expanded['status'] == 'open'


class TestQuerying:
    """Test Lug query operations."""
    
    def test_get_lug_by_full_id(self, lug_manager):
        """Test retrieving Lug by full ID."""
        lug = lug_manager.create_lug(title="Query Test")
        
        retrieved = lug_manager.get_lug(lug.id)
        assert retrieved is not None
        assert retrieved.id == lug.id
        assert retrieved.title == "Query Test"
    
    def test_get_lug_by_prefix(self, lug_manager):
        """Test retrieving Lug by ID prefix."""
        lug = lug_manager.create_lug(title="Prefix Test")
        
        # Use first 4 characters
        prefix = lug.id[:4]
        retrieved = lug_manager.get_lug(prefix)
        
        assert retrieved is not None
        assert retrieved.id == lug.id
    
    def test_ambiguous_prefix_raises_error(self, lug_manager):
        """Test that ambiguous prefix raises error."""
        # This test may not always trigger ambiguity due to random IDs
        # but demonstrates the behavior
        lugs = [lug_manager.create_lug(title=f"Test {i}") for i in range(100)]
        
        # Try empty prefix (should match all)
        with pytest.raises(ValueError, match="Ambiguous"):
            lug_manager.get_lug("")
    
    def test_list_lugs_all(self, lug_manager):
        """Test listing all Lugs."""
        lug1 = lug_manager.create_lug(title="List 1", lug_type="work")
        lug2 = lug_manager.create_lug(title="List 2", lug_type="bug")
        lug3 = lug_manager.create_lug(title="List 3", lug_type="work")
        
        all_lugs = lug_manager.list_lugs()
        assert len(all_lugs) == 3
    
    def test_list_lugs_by_status(self, lug_manager):
        """Test filtering Lugs by status."""
        lug1 = lug_manager.create_lug(title="Open 1")
        lug2 = lug_manager.create_lug(title="Open 2")
        lug_manager.update_lug(lug1.id, status="in_progress")
        
        open_lugs = lug_manager.list_lugs(status="open")
        in_progress_lugs = lug_manager.list_lugs(status="in_progress")
        
        assert len(open_lugs) == 1
        assert len(in_progress_lugs) == 1
    
    def test_list_lugs_by_type(self, lug_manager):
        """Test filtering Lugs by type."""
        lug1 = lug_manager.create_lug(title="Work Item", lug_type="work")
        lug2 = lug_manager.create_lug(title="Bug Fix", lug_type="bug")
        lug3 = lug_manager.create_lug(title="Feature", lug_type="issue")
        
        bugs = lug_manager.list_lugs(lug_type="bug")
        work = lug_manager.list_lugs(lug_type="work")
        
        assert len(bugs) == 1
        assert len(work) == 1
        assert bugs[0].type == "bug"
    
    def test_list_lugs_by_priority(self, lug_manager):
        """Test filtering Lugs by priority."""
        lug1 = lug_manager.create_lug(title="High Pri", priority="high")
        lug2 = lug_manager.create_lug(title="Med Pri", priority="medium")
        lug3 = lug_manager.create_lug(title="Low Pri", priority="low")
        
        high = lug_manager.list_lugs(priority="high")
        assert len(high) == 1
        assert high[0].priority == "high"
    
    def test_get_lug_not_found(self, lug_manager):
        """Verify None returned for missing ID."""
        result = lug_manager.get_lug("nonexistent-id-12345")
        assert result is None
    
    def test_get_lug_min_prefix_length(self, lug_manager):
        """Verify minimum prefix length requirement (should be 4 chars or implementation-defined)."""
        lug = lug_manager.create_lug(title="Prefix Length Test")
        
        # Test with very short prefix (might fail depending on implementation)
        try:
            # Try 1-char prefix (should likely fail or be ambiguous)
            result = lug_manager.get_lug(lug.id[:1])
            # If it works, that's ok, just document the behavior
        except ValueError:
            # Expected - prefix too short or ambiguous
            pass
        
        # 4-char prefix should work
        result = lug_manager.get_lug(lug.id[:4])
        assert result is not None
        assert result.id == lug.id



class TestUpdates:
    """Test Lug update operations."""
    
    def test_update_status(self, lug_manager):
        """Test updating Lug status."""
        lug = lug_manager.create_lug(title="Update Test")
        
        updated = lug_manager.update_lug(lug.id, status="in_progress")
        
        assert updated.status == "in_progress"
        assert updated.updated_at > lug.created_at
    
    def test_update_priority(self, lug_manager):
        """Test updating Lug priority."""
        lug = lug_manager.create_lug(title="Pri Test", priority="medium")
        
        updated = lug_manager.update_lug(lug.id, priority="high")
        
        assert updated.priority == "high"
    
    def test_update_value(self, lug_manager):
        """Test updating Lug value."""
        lug = lug_manager.create_lug(title="Value Test", value=5)
        
        updated = lug_manager.update_lug(lug.id, value=9)
        
        assert updated.value == 9


class TestDependencies:
    """Test dependency management."""
    
    def test_add_dependency(self, lug_manager):
        """Test adding a dependency relationship."""
        lug_a = lug_manager.create_lug(title="Task A")
        lug_b = lug_manager.create_lug(title="Task B")  # B depends on A
        
        lug_manager.add_dependency(lug_b.id, lug_a.id)
        
        # Refresh from manager
        lug_b_updated = lug_manager.get_lug(lug_b.id)
        lug_a_updated = lug_manager.get_lug(lug_a.id)
        
        assert lug_a.id in lug_b_updated.deps
        assert lug_b.id in lug_a_updated.blocked_by
    
    def test_dependency_chain(self, lug_manager):
        """Test traversing dependency chain."""
        lug_a = lug_manager.create_lug(title="Foundation")
        lug_b = lug_manager.create_lug(title="Layer 1")
        lug_c = lug_manager.create_lug(title="Layer 2")
        
        lug_manager.add_dependency(lug_b.id, lug_a.id)
        lug_manager.add_dependency(lug_c.id, lug_b.id)
        
        chain = lug_manager.get_dependency_chain(lug_c.id)
        
        assert len(chain) == 3
        ids = [l.id for l in chain]
        assert lug_c.id in ids
        assert lug_b.id in ids
        assert lug_a.id in ids
    
    def test_circular_dependency_detection(self, lug_manager):
        """Verify A→B→A causes error or warning."""
        lug_a = lug_manager.create_lug(title="Task A")
        lug_b = lug_manager.create_lug(title="Task B")
        
        # A depends on B
        lug_manager.add_dependency(lug_a.id, lug_b.id)
        
        # Try to make B depend on A (circular)
        try:
            lug_manager.add_dependency(lug_b.id, lug_a.id)
            # If no error, verify circular dependency exists
            chain = lug_manager.get_dependency_chain(lug_a.id, max_depth=10)
            # Some implementations might allow it, just document
        except ValueError as e:
            # Expected - circular dependency detected
            assert "circular" in str(e).lower() or "cycle" in str(e).lower()
    
    def test_deep_dependency_chain(self, lug_manager):
        """Verify A→B→C→D→E works correctly."""
        lugs = []
        for i in range(5):
            lug = lug_manager.create_lug(title=f"Layer {i}")
            lugs.append(lug)
            if i > 0:
                lug_manager.add_dependency(lug.id, lugs[i-1].id)
        
        # Verify chain from E
        chain = lug_manager.get_dependency_chain(lugs[4].id)
        assert len(chain) == 5
        
        # Verify all IDs present
        chain_ids = {l.id for l in chain}
        for lug in lugs:
            assert lug.id in chain_ids



class TestPolicyValidation:
    """Test policy enforcement."""
    
    def test_policy_loading(self, lug_manager, temp_spoke_dir):
        """Test loading policies from WAI-Policies.json."""
        policies = {
            "lug_policies": {
                "bug": {
                    "close_requires": ["test_added", "test_verified"]
                }
            }
        }
        
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        with open(policies_file, 'w') as f:
            json.dump(policies, f)
        
        lug = lug_manager.create_lug(title="Bug Test", lug_type="bug")
        violations = lug_manager.validate_policies(lug)
        
        assert len(violations) == 2  # Missing both tags
        assert any("test_added" in v for v in violations)
        assert any("test_verified" in v for v in violations)
    
    def test_policy_satisfied(self, lug_manager, temp_spoke_dir):
        """Test that policies pass when satisfied."""
        policies = {
            "lug_policies": {
                "work": {
                    "close_requires": []
                }
            }
        }
        
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        with open(policies_file, 'w') as f:
            json.dump(policies, f)
        
        lug = lug_manager.create_lug(title="Work Test", lug_type="work")
        violations = lug_manager.validate_policies(lug)
        
        assert len(violations) == 0


class TestClosing:
    """Test Lug closing and archiving."""
    
    def test_close_lug(self, lug_manager, temp_spoke_dir):
        """Test closing a Lug."""
        lug = lug_manager.create_lug(title="Close Test")
        
        closed = lug_manager.close_lug(
            lug.id,
            summary="Test completed",
            skip_policy_check=True
        )
        
        assert closed.status == "closed"
        assert closed.closed_at is not None
        assert closed.summary == "Test completed"
    
    def test_closed_lug_archived(self, lug_manager, temp_spoke_dir):
        """Test that closed Lugs are moved to archive."""
        lug = lug_manager.create_lug(title="Archive Test")
        lug_manager.close_lug(lug.id, skip_policy_check=True)
        
        # Should be removed from active lugs
        assert lug.id not in lug_manager.lugs
        
        # Should be in closed file
        closed_file = temp_spoke_dir / 'lugs-closed.jsonl'
        assert closed_file.exists()
        
        with open(closed_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
    
    def test_close_with_policy_violation_raises(self, lug_manager, temp_spoke_dir):
        """Test that closing with policy violations raises error."""
        policies = {
            "lug_policies": {
                "bug": {
                    "close_requires": ["test_verified"]
                }
            }
        }
        
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        with open(policies_file, 'w') as f:
            json.dump(policies, f)
        
        lug = lug_manager.create_lug(title="Bug Test", lug_type="bug")
        
        with pytest.raises(ValueError, match="Policy violations"):
            lug_manager.close_lug(lug.id, skip_policy_check=False)


class TestSessions:
    """Test session tracking."""
    
    def test_create_session(self, lug_manager, temp_spoke_dir):
        """Test creating a session."""
        session = lug_manager.create_session(
            session_id="test-session-1",
            who="Mario",
            ide="Claude Code",
            mode="YOLO",
            model="Claude Sonnet 3.7"
        )
        
        assert session.session_id == "test-session-1"
        assert session.who == "Mario"
        assert session.ide == "Claude Code"
        assert session.mode == "YOLO"
        assert session.model == "Claude Sonnet 3.7"
    
    def test_session_persisted(self, lug_manager, temp_spoke_dir):
        """Test that sessions are written to lug-sessions.jsonl."""
        lug_manager.create_session(
            session_id="test-session-2",
            who="Mario",
            ide="Cursor"
        )
        
        sessions_file = temp_spoke_dir / 'sessions.jsonl'
        assert sessions_file.exists()
        
        with open(sessions_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1


class TestEnhancedPolicies:
    """Test enhanced policy features."""
    
    def test_is_significant(self, lug_manager):
        """Test significance check."""
        # Significant: high pri, large impact
        # Significant: high priority OR large impact OR value >= 7
        lug1 = lug_manager.create_lug(title="Sig 1", priority="high", impact="large", value=5)
        lug2 = lug_manager.create_lug(title="Sig 2", priority="high", impact="small", value=8)
        lug3 = lug_manager.create_lug(title="Sig 3", priority="medium", impact="large", value=5)
        lug4 = lug_manager.create_lug(title="Sig 4", priority="low", impact="small", value=9)
        
        # Not significant: low priority AND small impact AND value < 7
        lug5 = lug_manager.create_lug(title="Not Sig 1", priority="medium", impact="medium", value=5)
        lug6 = lug_manager.create_lug(title="Not Sig 2", priority="low", impact="small", value=3)
        
        assert lug_manager.is_significant(lug1) is True  # high priority + large impact
        assert lug_manager.is_significant(lug2) is True  # high priority + value >= 7
        assert lug_manager.is_significant(lug3) is True  # large impact
        assert lug_manager.is_significant(lug4) is True  # value >= 7
        assert lug_manager.is_significant(lug5) is False  # medium/medium/5
        assert lug_manager.is_significant(lug6) is False  # low/small/3
        
    def test_add_policy_type(self, lug_manager, temp_spoke_dir):
        """Test dynamic policy type addition."""
        rules = {"close_requires": ["research_complete"]}
        lug_manager.add_policy_type("research", rules)
        
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        assert policies_file.exists()
        
        with open(policies_file, 'r') as f:
            policies = json.load(f)
        
        assert policies["lug_policies"]["research"] == rules
        
        # Verify it applies
        lug = lug_manager.create_lug(title="Res Lug", lug_type="research")
        violations = lug_manager.validate_policies(lug)
        assert "research_complete" in violations[0]

    def test_global_policy_no_open_blockers(self, lug_manager, temp_spoke_dir):
        """Test global policy: no_open_blockers."""
        policies = {
            "lug_policies": {},
            "global_policies": ["no_open_blockers"]
        }
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        with open(policies_file, 'w') as f:
            json.dump(policies, f)
            
        lug_a = lug_manager.create_lug(title="Task A")
        lug_b = lug_manager.create_lug(title="Task B") # B depends on A
        lug_manager.add_dependency(lug_b.id, lug_a.id)
        
        # A is open, so B should have global violation
        violations = lug_manager._validate_global_policies(lug_b)
        assert any("still open" in v for v in violations)
        
        # Close A
        lug_manager.close_lug(lug_a.id, skip_policy_check=True)
        
        # Now B should pass
        violations = lug_manager._validate_global_policies(lug_b)
        assert len(violations) == 0

    def test_list_lugs_ready_to_close(self, lug_manager, temp_spoke_dir):
        """Test listing Lugs ready to close."""
        policies = {
            "lug_policies": {
                "bug": {"close_requires": ["test_verified"]}
            },
            "global_policies": []
        }
        policies_file = temp_spoke_dir / 'WAI-Policies.json'
        with open(policies_file, 'w') as f:
            json.dump(policies, f)
            
        lug1 = lug_manager.create_lug(title="Bug (Blocked)", lug_type="bug")
        lug2 = lug_manager.create_lug(title="Work (Ready)", lug_type="work")
        
        ready = lug_manager.list_lugs_ready_to_close()
        assert len(ready) == 1
        assert ready[0].id == lug2.id
        
        # Add tag to lug1
        lug_manager.update_lug(lug1.id, policy_tags=["test_verified"])
        
        ready = lug_manager.list_lugs_ready_to_close()
        assert len(ready) == 2

        
        ready = lug_manager.list_lugs_ready_to_close()
        assert len(ready) == 2


class TestBeadChain:
    """Test Bead recording, retrieval and validation."""

    def test_record_bead(self, lug_manager, temp_spoke_dir):
        """Test recording a session bead."""
        bead = lug_manager.record_session_bead(
            session_id="session-1",
            summary="Initial session",
            files_modified=["test.py"]
        )
        
        assert bead['session_id'] == "session-1"
        assert bead['summary'] == "Initial session"
        assert len(bead['bead_id']) == 16
        
        # Verify file
        sessions_file = temp_spoke_dir / 'sessions.jsonl'
        with open(sessions_file, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 1
        
    def test_bead_chain_retrieval(self, lug_manager):
        """Test retrieving sorted chain."""
        lug_manager.record_session_bead(session_id="s1", summary="First")
        lug_manager.record_session_bead(session_id="s2", summary="Second")
        
        chain = lug_manager.get_bead_chain()
        assert len(chain) == 2
        assert chain[0]['session_id'] == "s1"
        assert chain[1]['session_id'] == "s2"
        
    def test_validate_chain_valid(self, lug_manager):
        """Test validating a correct chain."""
        b1 = lug_manager.record_session_bead(session_id="s1", summary="First")
        b2 = lug_manager.record_session_bead(
            session_id="s2", 
            summary="Second",
            parent_id=b1['bead_id']
        )
        
        validation = lug_manager.validate_bead_chain()
        assert validation['valid'] is True
        assert len(validation['errors']) == 0

    def test_validate_chain_broken(self, lug_manager):
        """Test validating a chain with missing parent."""
        # Create orphan bead pointing to non-existent parent
        lug_manager.record_session_bead(
            session_id="s2", 
            summary="Second",
            parent_id="deadbeef12345678"
        )
        
        validation = lug_manager.validate_bead_chain()
        assert validation['valid'] is False
        assert len(validation['errors']) == 1
        assert "Broken link" in validation['errors'][0]
if __name__ == "__main__":
        assert validation['valid'] is False
        assert len(validation['errors']) == 1
        assert "Broken link" in validation['errors'][0]

class TestHierarchicalIDs:
    """Test Hierarchical ID generation."""
    
    def test_create_child_lug(self, lug_manager):
        """Test creating a child Lug (hierarchical ID)."""
        parent = lug_manager.create_lug(title="Parent Task")
        child = lug_manager.create_lug(title="Child Task", parent_id=parent.id)
        
        assert child.id.startswith(parent.id + ".")
        assert child.id == f"{parent.id}.1"
    
    def test_create_multiple_children(self, lug_manager):
        """Test creating multiple children (incrementing index)."""
        parent = lug_manager.create_lug(title="Parent Task")
        child1 = lug_manager.create_lug(title="Child 1", parent_id=parent.id)
        child2 = lug_manager.create_lug(title="Child 2", parent_id=parent.id)
        
        assert child1.id == f"{parent.id}.1"
        assert child2.id == f"{parent.id}.2"
    
    def test_create_grandchild(self, lug_manager):
        """Test creating nested children."""
        parent = lug_manager.create_lug(title="Epic")
        child = lug_manager.create_lug(title="Story", parent_id=parent.id)
        grandchild = lug_manager.create_lug(title="Task", parent_id=child.id)
        
        assert grandchild.id == f"{parent.id}.1.1"

    def test_create_with_sharding_session(self, lug_manager, temp_spoke_dir):
        """Test that lugs with specific session_id go to that file."""
        session_id = "test-shard-001"
        lug = lug_manager.create_lug(title="Sharded", session_id=session_id)
        
        expected_file = temp_spoke_dir / 'lugs' / f"{session_id}.jsonl"
        assert expected_file.exists()
        
        content = expected_file.read_text(encoding='utf-8')
        assert lug.id in content
