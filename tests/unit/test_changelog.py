"""
Unit tests for ChangelogGenerator.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai_cli.changelog import ChangelogGenerator
from wai_cli.lugs import LugManager

@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / 'WAI-Spoke').mkdir()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_generate_changelog_content(temp_spoke_dir):
    """Test generating markdown content from closed Lugs."""
    manager = LugManager(temp_spoke_dir)
    
    # Create and close some Lugs
    lug1 = manager.create_lug(title="Feature A", lug_type="feat")
    manager.close_lug(lug1.id, summary="Implemented Feature A")
    
    lug2 = manager.create_lug(title="Bug B", lug_type="bug")
    manager.close_lug(lug2.id, summary="Fixed Bug B")
    
    generator = ChangelogGenerator(temp_spoke_dir)
    content = generator.generate_changelog_content()
    
    assert "🚀 Features" in content
    assert "Feature A" in content
    assert "🐛 Bug Fixes" in content
    assert "Bug B" in content
    assert f"## Release {datetime.now().strftime('%Y-%m-%d')}" in content

def test_update_changelog_file(temp_spoke_dir):
    """Test updating CHANGELOG.md file."""
    manager = LugManager(temp_spoke_dir)
    lug1 = manager.create_lug(title="Feature A", lug_type="feat")
    manager.close_lug(lug1.id)
    
    generator = ChangelogGenerator(temp_spoke_dir)
    changelog_file = temp_spoke_dir / "CHANGELOG.md"
    
    # First update
    generator.update_changelog_file(changelog_file)
    assert changelog_file.exists()
    content = changelog_file.read_text()
    assert "# Changelog" in content
    assert "Feature A" in content
    
    # Second update (prepending)
    lug2 = manager.create_lug(title="Feature B", lug_type="feat")
    manager.close_lug(lug2.id)
    
    # We need a new generator or clear cache if manager was reused, 
    # but manager reloads from file, so it should be fine.
    generator.update_changelog_file(changelog_file)
    content = changelog_file.read_text()
    assert content.count("## Release") == 2
    # Feature B (newer) should be before Feature A (older)
    assert content.find("Feature B") < content.find("Feature A")
