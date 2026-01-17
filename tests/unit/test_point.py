"""
Unit tests for WAI-Point.json generation.

Tests:
- Bootstrap generation from WAI-State
- Open Lugs summary extraction
- Update on shipit
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai_cli.point import PointManager
from wai_cli.lugs import LugManager


@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / 'WAI-Spoke').mkdir()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def point_manager(temp_spoke_dir):
    """Create PointManager instance."""
    return PointManager(temp_spoke_dir)


class TestPointGeneration:
    """Test WAI-Point.json generation."""
    
    def test_generate_minimal_point(self, point_manager):
        """Test generating Point with no state or Lugs."""
        point = point_manager.generate_point()
        
        assert point['schema_version'] == 1
        assert 'generated_at' in point
        assert 'summary' in point
        assert 'open_lugs_summary' in point
        assert 'last_shipit' in point
        assert 'key_learnings' in point
        assert 'open_lugs' in point
        assert 'next_session_lug' in point
    
    def test_point_with_state(self, point_manager, temp_spoke_dir):
        """Test Point generation with WAI-State.json."""
        state = {
            "wheel": {
                "name": "Test Project",
                "description": "A test project for Point generation"
            },
            "context": {
                "insights": [
                    "Insight 1",
                    "Insight 2",
                    "Insight 3"
                ]
            },
            "_session_state": {
                "last_closeout": {
                    "closed_at": "2026-01-16T12:00:00Z",
                    "summary": "Completed feature X",
                    "key_topics": ["feature-x", "testing"]
                }
            }
        }
        
        state_file = temp_spoke_dir / 'WAI-Spoke' / 'WAI-State.json'
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        point = point_manager.generate_point()
        
        assert point['summary'] == "A test project for Point generation"
        assert point['key_learnings'] == ["Insight 1", "Insight 2", "Insight 3"]
        assert point['last_shipit']['timestamp'] == "2026-01-16T12:00:00Z"
        assert point['last_shipit']['summary'] == "Completed feature X"
        assert point['last_shipit']['key_topics'] == ["feature-x", "testing"]
    
    def test_point_with_open_lugs(self, point_manager, temp_spoke_dir):
        """Test Point generation with open Lugs."""
        # Create some Lugs
        lug_manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
        lug_manager.create_lug(title="High priority task", priority="high", value=9)
        lug_manager.create_lug(title="Medium priority task", priority="medium")
        lug_manager.create_lug(title="Low priority task", priority="low")
        
        point = point_manager.generate_point()
        
        assert "3 open" in point['open_lugs_summary']
        assert "1 high" in point['open_lugs_summary']
        assert "1 medium" in point['open_lugs_summary']
        assert "1 low" in point['open_lugs_summary']
        assert len(point['open_lugs']) == 3
        assert point['next_session_lug']['title'] == "High priority task"
    
    def test_point_with_no_lugs(self, point_manager):
        """Test Point when no Lugs system initialized."""
        point = point_manager.generate_point()
        
        assert point['open_lugs_summary'] == "No Lugs system initialized"


class TestPointUpdate:
    """Test Point update operations."""
    
    def test_update_point(self, point_manager, temp_spoke_dir):
        """Test updating WAI-Point.json."""
        point_manager.update_point(shipit_summary="Completed implementation")
        
        point_file = temp_spoke_dir / 'WAI-Spoke' / 'WAI-Point.json'
        assert point_file.exists()
        
        with open(point_file, 'r') as f:
            point = json.load(f)
        
        assert point['last_shipit']['summary'] == "Completed implementation"
    
    def test_load_existing_point(self, point_manager, temp_spoke_dir):
        """Test loading existing Point file."""
        # Create Point
        point_manager.update_point()
        
        # Load it
        loaded = point_manager.load_point()
        
        assert loaded is not None
        assert loaded['schema_version'] == 1
        assert 'summary' in loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
