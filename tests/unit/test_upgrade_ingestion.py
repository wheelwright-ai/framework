"""
Unit tests for thorough upgrade ingestion verification.

Tests comprehensive tracking and verification of teaching files:
- All files in plan are tracked
- Orphaned files are detected
- Unprocessed files are detected
- Processing metadata is maintained
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from wai.upgrade_adoption import (
    verify_upgrade_ingestion_complete,
    ensure_upgrade_adoption_tracked,
    UpgradeAdoptionPlanBuilder
)


@pytest.fixture
def temp_ingest_dir(tmp_path):
    """Create temporary ingest directory."""
    ingest_dir = tmp_path / "seed" / "ingest"
    ingest_dir.mkdir(parents=True, exist_ok=True)
    return ingest_dir


@pytest.fixture
def sample_upgrade_plan():
    """Create a sample upgrade adoption plan."""
    builder = UpgradeAdoptionPlanBuilder(
        framework_version="3.1.0",
        spoke_structure_version="3.0"
    )
    
    plan = {
        "metadata": {
            "version": "3.1.0",
            "framework_version": "3.1.0",
            "created_at": datetime.utcnow().isoformat() + "Z"
        },
        "files": [
            {
                "name": "WAI-Guide.md",
                "path": "WAI-Spoke/WAI-Guide.md",
                "version": "3.1.0",
                "safe_to_auto_adopt": True
            },
            {
                "name": "WAI-State.json",
                "path": "WAI-Spoke/WAI-State.json",
                "version": "3.1.0",
                "safe_to_auto_adopt": False
            }
        ],
        "hub_files": [
            {
                "name": "hub-registry.json",
                "path": "hub-registry.json",
                "version": "3.1.0",
                "safe_to_auto_adopt": True
            }
        ]
    }
    
    return plan


class TestUpgradeIngestionVerification:
    """Test thorough upgrade ingestion verification."""
    
    def test_empty_ingest_no_plan(self, temp_ingest_dir):
        """Empty ingest dir with no plan returns empty result."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert result["is_complete"] is True
        assert result["pending"] == []
        assert result["orphaned"] == []
        assert result["issues"] == []
    
    def test_no_ingest_dir(self, tmp_path, sample_upgrade_plan):
        """Missing ingest dir returns empty result."""
        plan_path = tmp_path / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        ingest_dir = tmp_path / "nonexistent" / "ingest"
        
        result = verify_upgrade_ingestion_complete(plan_path, ingest_dir)
        
        assert result["is_complete"] is True
    
    def test_detects_unprocessed_teaching_files(self, temp_ingest_dir, sample_upgrade_plan):
        """Detects .teaching files that haven't been processed."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Create unprocessed teaching files
        (temp_ingest_dir / "WAI-Guide.md.teaching").write_text("content")
        (temp_ingest_dir / "WAI-State.json.teaching").write_text("content")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert result["is_complete"] is False
        assert len(result["pending"]) == 2
        assert "WAI-Guide.md.teaching" in result["pending"]
        assert "WAI-State.json.teaching" in result["pending"]
        assert any("unprocessed" in issue for issue in result["issues"])
    
    def test_detects_orphaned_teaching_files(self, temp_ingest_dir, sample_upgrade_plan):
        """Detects .teaching files not in upgrade plan."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Create orphaned file not in plan
        (temp_ingest_dir / "unknown-file.teaching").write_text("content")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert result["is_complete"] is False
        assert "unknown-file.teaching" in result["orphaned"]
        assert any("orphaned" in issue for issue in result["issues"])
    
    def test_ignores_metadata_files(self, temp_ingest_dir, sample_upgrade_plan):
        """Ignores .teaching files in metadata like manifest, disposition."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Create metadata files - should be ignored
        (temp_ingest_dir / "manifest.json").write_text("{}")
        (temp_ingest_dir / "disposition-log.jsonl").write_text("")
        (temp_ingest_dir / "upgrade-adoption-plan.json").write_text("{}")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert result["is_complete"] is True
        assert result["orphaned"] == []
    
    def test_multiple_orphaned_files_truncated_in_message(self, temp_ingest_dir, sample_upgrade_plan):
        """Issue message truncates orphaned file list after 3."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Create 5 orphaned files
        for i in range(5):
            (temp_ingest_dir / f"orphan-{i}.teaching").write_text("content")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert len(result["orphaned"]) == 5
        issue_msg = result["issues"][0]
        # Check that only first 3 are mentioned in message
        assert "orphan-0" in issue_msg or "orphan-1" in issue_msg or "orphan-2" in issue_msg
    
    def test_plan_with_mixed_pending_and_orphaned(self, temp_ingest_dir, sample_upgrade_plan):
        """Correctly identifies both pending (tracked) and orphaned (untracked) files."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Unprocessed tracked files
        (temp_ingest_dir / "WAI-Guide.md.teaching").write_text("content")
        
        # Orphaned untracked file
        (temp_ingest_dir / "unknown.teaching").write_text("content")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        assert result["is_complete"] is False
        assert "WAI-Guide.md.teaching" in result["pending"]
        assert "unknown.teaching" in result["orphaned"]
        assert len(result["issues"]) >= 2
    
    def test_clean_ingest_with_tracked_files(self, temp_ingest_dir, sample_upgrade_plan):
        """All tracked files present and unprocessed is detected correctly."""
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(sample_upgrade_plan))
        
        # Add ALL tracked files
        (temp_ingest_dir / "WAI-Guide.md.teaching").write_text("content")
        (temp_ingest_dir / "WAI-State.json.teaching").write_text("content")
        (temp_ingest_dir / "hub-registry.json").write_text("content")
        
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        
        # Not complete because .teaching files are unprocessed
        assert result["is_complete"] is False
        assert len(result["pending"]) == 2
        assert result["orphaned"] == []


class TestUpgradeAdoptionTracking:
    """Test upgrade adoption plan tracking metadata."""
    
    def test_ensure_tracking_metadata_added(self, sample_upgrade_plan):
        """Tracking metadata is added to plan."""
        temp_dir = Path("/tmp/test")
        
        ensure_upgrade_adoption_tracked(sample_upgrade_plan, temp_dir)
        
        assert "processing_metadata" in sample_upgrade_plan
        metadata = sample_upgrade_plan["processing_metadata"]
        assert "tracked_files" in metadata
        assert "ingestion_timestamp" in metadata
        assert "files_verified" in metadata
        assert "files_processed" in metadata
    
    def test_tracked_files_list_built_correctly(self, sample_upgrade_plan):
        """Tracked files list includes all files from files and hub_files."""
        temp_dir = Path("/tmp/test")
        
        ensure_upgrade_adoption_tracked(sample_upgrade_plan, temp_dir)
        
        tracked = sample_upgrade_plan["processing_metadata"]["tracked_files"]
        assert "WAI-Guide.md" in tracked
        assert "WAI-State.json" in tracked
        assert "hub-registry.json" in tracked
        assert len(tracked) == 3
    
    def test_tracked_files_deduplicated_and_sorted(self, sample_upgrade_plan):
        """Tracked files are deduplicated and sorted."""
        # Add duplicate entry
        sample_upgrade_plan["files"].append({
            "name": "WAI-Guide.md",
            "path": "WAI-Spoke/WAI-Guide.md"
        })
        
        temp_dir = Path("/tmp/test")
        ensure_upgrade_adoption_tracked(sample_upgrade_plan, temp_dir)
        
        tracked = sample_upgrade_plan["processing_metadata"]["tracked_files"]
        # Should be deduped
        assert tracked.count("WAI-Guide.md") == 1
        # Should be sorted
        assert tracked == sorted(tracked)


class TestUpgradeIngestionIntegration:
    """Integration tests for complete upgrade ingestion workflow."""
    
    def test_first_teach_creates_clean_plan(self, temp_ingest_dir):
        """First teach creates plan with tracking metadata."""
        plan = {
            "metadata": {"version": "3.1.0"},
            "files": [{"name": "test-file.md"}],
            "hub_files": []
        }
        
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(plan))
        
        ensure_upgrade_adoption_tracked(plan, temp_ingest_dir)
        
        # Verify
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        assert result["is_complete"] is True  # No files yet
    
    def test_teach_cycle_with_distribution_and_processing(self, temp_ingest_dir):
        """Complete teach-distribute-process-verify cycle."""
        # Create plan with multiple files
        plan = {
            "metadata": {"version": "3.1.0"},
            "files": [
                {"name": "file-1.md"},
                {"name": "file-2.md"}
            ],
            "hub_files": []
        }
        
        plan_path = temp_ingest_dir.parent.parent / "upgrade-adoption-plan.json"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Phase 1: Create and track plan
        ensure_upgrade_adoption_tracked(plan, temp_ingest_dir)
        plan_path.write_text(json.dumps(plan))
        
        # Phase 2: Distribute files
        (temp_ingest_dir / "file-1.md.teaching").write_text("content1")
        (temp_ingest_dir / "file-2.md.teaching").write_text("content2")
        
        # Phase 3: Verify unprocessed
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        assert result["is_complete"] is False
        assert len(result["pending"]) == 2
        
        # Phase 4: Simulate processing (remove one file)
        (temp_ingest_dir / "file-1.md.teaching").unlink()
        
        # Verify still incomplete (one file unprocessed)
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        assert result["is_complete"] is False
        assert "file-2.md.teaching" in result["pending"]
        assert "file-1.md.teaching" not in result["pending"]
        
        # Phase 5: Process remaining file
        (temp_ingest_dir / "file-2.md.teaching").unlink()
        
        # Verify complete
        result = verify_upgrade_ingestion_complete(plan_path, temp_ingest_dir)
        assert result["is_complete"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
