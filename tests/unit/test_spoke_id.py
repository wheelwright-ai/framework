"""
Unit tests for spoke_id module.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from wai.spoke_id import (
    generate_spoke_id,
    validate_spoke_id,
    get_spoke_id,
    set_spoke_id,
    SpokeRegistry,
)


class TestSpokeIDGeneration:
    """Test spoke_id generation."""
    
    def test_generate_deterministic(self):
        """spoke_id generation should be deterministic."""
        sid1 = generate_spoke_id("Test Project", "2026-02-01T12:00:00Z")
        sid2 = generate_spoke_id("Test Project", "2026-02-01T12:00:00Z")
        assert sid1 == sid2
    
    def test_generate_length(self):
        """spoke_id should be exactly 12 characters."""
        sid = generate_spoke_id("Test Project", "2026-02-01T12:00:00Z")
        assert len(sid) == 12
    
    def test_generate_hex_format(self):
        """spoke_id should be valid hex."""
        sid = generate_spoke_id("Test Project", "2026-02-01T12:00:00Z")
        assert all(c in "0123456789abcdef" for c in sid)
    
    def test_generate_different_inputs(self):
        """Different inputs should produce different spoke_ids."""
        sid1 = generate_spoke_id("Project A", "2026-02-01T12:00:00Z")
        sid2 = generate_spoke_id("Project B", "2026-02-01T12:00:00Z")
        assert sid1 != sid2
    
    def test_generate_with_default_timestamp(self):
        """Should generate spoke_id without timestamp (uses current time)."""
        sid = generate_spoke_id("Test Project")
        assert len(sid) == 12
        assert all(c in "0123456789abcdef" for c in sid)


class TestSpokeIDValidation:
    """Test spoke_id validation."""
    
    def test_validate_valid(self):
        """Valid spoke_id should pass validation."""
        assert validate_spoke_id("7a1d9c5b3e2f") is True
    
    def test_validate_invalid_length(self):
        """Invalid length should fail."""
        assert validate_spoke_id("7a1d9c5b3e") is False  # 11 chars
        assert validate_spoke_id("7a1d9c5b3e2f00") is False  # 14 chars
    
    def test_validate_invalid_hex(self):
        """Non-hex characters should fail."""
        assert validate_spoke_id("7a1d9c5b3e2g") is False  # 'g' not hex
        assert validate_spoke_id("gggggggggggg") is False
    
    def test_validate_non_string(self):
        """Non-string input should fail."""
        assert validate_spoke_id(12345678901) is False
        assert validate_spoke_id(None) is False


class TestSpokeIDPersistence:
    """Test reading/writing spoke_id to files."""
    
    def test_get_spoke_id_from_state(self, tmp_path):
        """Should extract spoke_id from WAI-State.json."""
        spoke_dir = tmp_path / "WAI-Spoke"
        spoke_dir.mkdir()
        
        state = {
            "wheel": {
                "spoke_id": "7a1d9c5b3e2f",
                "name": "Test Project"
            }
        }
        
        state_path = spoke_dir / "WAI-State.json"
        with open(state_path, "w") as f:
            json.dump(state, f)
        
        result = get_spoke_id(str(tmp_path))
        assert result == "7a1d9c5b3e2f"
    
    def test_get_spoke_id_missing(self, tmp_path):
        """Should return None if WAI-State.json missing."""
        result = get_spoke_id(str(tmp_path))
        assert result is None
    
    def test_set_spoke_id(self, tmp_path):
        """Should update spoke_id in WAI-State.json."""
        spoke_dir = tmp_path / "WAI-Spoke"
        spoke_dir.mkdir()
        
        state = {
            "_file_meta": {"last_updated": "2026-02-01T00:00:00Z"},
            "wheel": {"name": "Test Project"}
        }
        
        state_path = spoke_dir / "WAI-State.json"
        with open(state_path, "w") as f:
            json.dump(state, f)
        
        success = set_spoke_id(str(tmp_path), "7a1d9c5b3e2f")
        assert success is True
        
        # Verify it was written
        with open(state_path, "r") as f:
            updated = json.load(f)
        assert updated["wheel"]["spoke_id"] == "7a1d9c5b3e2f"
    
    def test_set_spoke_id_invalid(self, tmp_path):
        """Should reject invalid spoke_id."""
        spoke_dir = tmp_path / "WAI-Spoke"
        spoke_dir.mkdir()
        
        state = {"wheel": {"name": "Test"}}
        state_path = spoke_dir / "WAI-State.json"
        with open(state_path, "w") as f:
            json.dump(state, f)
        
        with pytest.raises(ValueError):
            set_spoke_id(str(tmp_path), "invalid")


class TestSpokeRegistry:
    """Test spoke registry."""
    
    def test_registry_register(self, tmp_path):
        """Should register spokes."""
        registry = SpokeRegistry(tmp_path)
        registry.register("7a1d9c5b3e2f", "Test Project", str(tmp_path / "project"))
        
        result = registry.get_project("7a1d9c5b3e2f")
        assert result["name"] == "Test Project"
    
    def test_registry_detect_mismatch(self, tmp_path):
        """Should detect mixed spoke_ids."""
        registry = SpokeRegistry(tmp_path)
        registry.register("7a1d9c5b3e2f", "Project A", str(tmp_path / "a"))
        registry.register("a1b2c3d4e5f6", "Project B", str(tmp_path / "b"))
        
        warning = registry.detect_mismatch(["7a1d9c5b3e2f", "a1b2c3d4e5f6"])
        assert warning is not None
        assert "Cross-project" in warning
    
    def test_registry_no_mismatch_single(self):
        """Should not warn on single spoke_id."""
        registry = SpokeRegistry()
        warning = registry.detect_mismatch(["7a1d9c5b3e2f"])
        assert warning is None
    
    def test_registry_no_mismatch_duplicate(self):
        """Should not warn on duplicate spoke_ids."""
        registry = SpokeRegistry()
        warning = registry.detect_mismatch(["7a1d9c5b3e2f", "7a1d9c5b3e2f"])
        assert warning is None
