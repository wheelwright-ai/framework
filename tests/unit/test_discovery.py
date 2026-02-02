"""
Unit tests for spoke discovery module.
"""

import json
import pytest
from pathlib import Path
from wai.discovery import SpokeDiscovery, discover_hub_spokes


class TestSpokeDiscovery:
    """Test spoke discovery."""
    
    def create_test_spoke(self, tmp_path: Path, project_name: str, 
                         spoke_id: str = None) -> Path:
        """Create a test spoke project."""
        project_dir = tmp_path / project_name
        project_dir.mkdir()
        
        spoke_dir = project_dir / "WAI-Spoke"
        spoke_dir.mkdir()
        
        state = {
            "_file_meta": {"last_updated": "2026-02-02T00:00:00Z"},
            "wheel": {
                "name": project_name,
                "version": "1.0.0",
                "status": "active",
            }
        }
        
        if spoke_id:
            state["wheel"]["spoke_id"] = spoke_id
        
        state_path = spoke_dir / "WAI-State.json"
        with open(state_path, "w") as f:
            json.dump(state, f)
        
        return project_dir
    
    def test_scan_finds_spokes(self, tmp_path):
        """Should find all WAI-Spoke directories."""
        # Create test spokes
        self.create_test_spoke(tmp_path, "project-a", "7a1d9c5b3e2f")
        self.create_test_spoke(tmp_path, "project-b", "a1b2c3d4e5f6")
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        spokes = discovery.scan()
        
        assert len(spokes) == 2
        assert any("project-a" in p for p in spokes.keys())
        assert any("project-b" in p for p in spokes.keys())
    
    def test_scan_extracts_metadata(self, tmp_path):
        """Should extract wheel metadata."""
        self.create_test_spoke(tmp_path, "test-project", "7a1d9c5b3e2f")
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        spokes = discovery.scan()
        
        metadata = list(spokes.values())[0]
        assert metadata["name"] == "test-project"
        assert metadata["spoke_id"] == "7a1d9c5b3e2f"
        assert metadata["status"] == "active"
    
    def test_detects_missing_ids(self, tmp_path):
        """Should detect projects missing spoke_id."""
        self.create_test_spoke(tmp_path, "has-id", "7a1d9c5b3e2f")
        self.create_test_spoke(tmp_path, "no-id", None)
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        discovery.scan()
        
        assert len(discovery.spokes_missing_id) == 1
        assert discovery.spokes_missing_id[0]["name"] == "no-id"
    
    def test_assign_missing_ids(self, tmp_path):
        """Should assign spoke_ids to projects missing them."""
        self.create_test_spoke(tmp_path, "project", None)
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        discovery.scan()
        
        assigned, ids = discovery.assign_missing_ids()
        assert assigned == 1
        assert len(ids) == 1
        assert all(len(sid) == 12 for sid in ids)
    
    def test_build_registry(self, tmp_path):
        """Should build registry from discovered spokes."""
        self.create_test_spoke(tmp_path, "proj-a", "7a1d9c5b3e2f")
        self.create_test_spoke(tmp_path, "proj-b", "a1b2c3d4e5f6")
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        discovery.discovered_spokes = discovery.scan()
        registry = discovery.build_registry()
        
        assert len(registry) == 2
        assert "7a1d9c5b3e2f" in registry
        assert "a1b2c3d4e5f6" in registry
        assert registry["7a1d9c5b3e2f"]["name"] == "proj-a"
    
    def test_save_registry(self, tmp_path):
        """Should save registry to .WAI-registry/spokes.json."""
        registry = {
            "7a1d9c5b3e2f": {
                "name": "test-project",
                "path": "/path/to/project",
                "version": "1.0.0"
            }
        }
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        success = discovery.save_registry(registry)
        
        assert success is True
        
        # Verify it was written
        registry_path = tmp_path / ".WAI-registry" / "spokes.json"
        assert registry_path.exists()
        
        with open(registry_path, "r") as f:
            saved = json.load(f)
        assert saved == registry
    
    def test_discover_and_register_workflow(self, tmp_path):
        """Should complete full discovery workflow."""
        self.create_test_spoke(tmp_path, "proj-a", "7a1d9c5b3e2f")
        self.create_test_spoke(tmp_path, "proj-b", None)
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        total, assigned, registry_count = discovery.discover_and_register()
        
        assert total == 2
        assert assigned == 1
        assert registry_count == 2
        
        # Verify registry was saved
        registry_path = tmp_path / ".WAI-registry" / "spokes.json"
        assert registry_path.exists()
    
    def test_report_generation(self, tmp_path):
        """Should generate discovery report."""
        self.create_test_spoke(tmp_path, "test-project", "7a1d9c5b3e2f")
        
        discovery = SpokeDiscovery(str(tmp_path), verbose=False)
        discovery.discovered_spokes = discovery.scan()
        report = discovery.get_report()
        
        assert "Spoke Discovery Report" in report
        assert "test-project" in report
        assert "7a1d9c5b3e2f" in report


class TestDiscoverHubSpokes:
    """Test standalone discovery function."""
    
    def test_discover_hub_spokes(self, tmp_path):
        """Should discover spokes in hub."""
        # Create test structure
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        
        spoke_dir = project_dir / "WAI-Spoke"
        spoke_dir.mkdir()
        
        state = {
            "_file_meta": {"last_updated": "2026-02-02T00:00:00Z"},
            "wheel": {
                "name": "my-project",
                "spoke_id": "7a1d9c5b3e2f",
                "version": "1.0.0"
            }
        }
        
        with open(spoke_dir / "WAI-State.json", "w") as f:
            json.dump(state, f)
        
        total, registry = discover_hub_spokes(str(tmp_path), verbose=False)
        
        assert total == 1
        assert len(registry) == 1
        assert "7a1d9c5b3e2f" in registry
