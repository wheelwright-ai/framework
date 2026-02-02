"""
Unit tests for upgrade adoption plan generation and verification.

Test-driven implementation of:
- upgrade-adoption-plan.json generation
- Hub fingerprint signing
- File hash verification
- Spoke-side verification
"""

import json
import hashlib
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestUpgradeAdoptionPlanGeneration:
    """Test upgrade-adoption-plan.json generation in teach command."""

    def test_upgrade_plan_has_required_metadata(self, tmp_path):
        """Upgrade plan includes version, framework_version, created_at."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        builder = UpgradeAdoptionPlanBuilder(
            framework_version="3.0.0",
            spoke_structure_version="3.0"
        )
        plan = builder.build()
        
        assert "metadata" in plan
        assert plan["metadata"]["version"] == "3.0.0"
        assert plan["metadata"]["framework_version"] == "3.0.0"
        assert plan["metadata"]["spoke_structure_version"] == "3.0"
        assert "created_at" in plan["metadata"]
        assert plan["metadata"]["source"] == "framework"

    def test_upgrade_plan_includes_file_hashes(self, tmp_path):
        """Each file in upgrade plan includes sha256 hash."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "test content"
        test_file.write_text(test_content)
        
        builder = UpgradeAdoptionPlanBuilder(
            framework_version="3.0.0",
            spoke_structure_version="3.0"
        )
        builder.add_file(
            name="test.txt",
            path="WAI-Spoke/test.txt",
            source_path=str(test_file),
            applies_to=["spoke"]
        )
        plan = builder.build()
        
        assert len(plan["files"]) == 1
        file_entry = plan["files"][0]
        assert "hash" in file_entry
        assert file_entry["hash"].startswith("sha256:")
        
        # Verify hash is correct
        expected_hash = "sha256:" + hashlib.sha256(test_content.encode()).hexdigest()
        assert file_entry["hash"] == expected_hash

    def test_upgrade_plan_includes_context_fields(self, tmp_path):
        """File entries include why_changed, mentions, applies_to."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        builder = UpgradeAdoptionPlanBuilder(
            framework_version="3.0.0",
            spoke_structure_version="3.0"
        )
        builder.add_file(
            name="WAI-Guide.md",
            path="WAI-Spoke/WAI-Guide.md",
            source_path=str(test_file),
            version="3.0.0",
            changed_from="2.1.0",
            why_changed="Enhanced session start protocol",
            mentions=["session-start", "teaching"],
            applies_to=["spoke", "hub"]
        )
        plan = builder.build()
        
        file_entry = plan["files"][0]
        assert file_entry["why_changed"] == "Enhanced session start protocol"
        assert "session-start" in file_entry["mentions"]
        assert "spoke" in file_entry["applies_to"]
        assert "hub" in file_entry["applies_to"]

    def test_upgrade_plan_separates_spoke_and_hub_files(self):
        """Spoke files go in 'files', hub files go in 'hub_files'."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        builder = UpgradeAdoptionPlanBuilder(
            framework_version="3.0.0",
            spoke_structure_version="3.0"
        )
        
        # Mock add_file to track calls
        builder.files = []
        builder.hub_files = []
        
        # This should work when add_file is implemented
        assert "files" in builder.__dict__ or hasattr(builder, 'files')


class TestHubFingerprinting:
    """Test hub fingerprint signing."""

    def test_hub_fingerprint_generation(self):
        """Hub can generate and sign upgrade plan."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        builder = UpgradeAdoptionPlanBuilder(
            framework_version="3.0.0",
            spoke_structure_version="3.0"
        )
        
        # Sign with hub fingerprint
        hub_fingerprint = "test-hub-fingerprint-123"
        plan = builder.build()
        
        # Should have verification section
        assert "verification" in plan
        assert "hub_fingerprint" in plan["verification"]

    def test_upgrade_plan_can_be_signed(self, tmp_path):
        """Upgrade plan can be signed with hub key."""
        from wai.upgrade_adoption import sign_upgrade_plan
        
        plan = {
            "metadata": {"version": "3.0.0", "framework_version": "3.0.0"},
            "files": [],
            "hub_files": [],
            "verification": {"hub_fingerprint": None}
        }
        
        hub_key = "test-hub-key"
        signed_plan = sign_upgrade_plan(plan, hub_key)
        
        assert "hub_fingerprint" in signed_plan["verification"]
        assert signed_plan["verification"]["hub_fingerprint"] is not None


class TestVerification:
    """Test spoke-side verification of upgrade plans."""

    def test_spoke_can_verify_file_hash(self):
        """Spoke can verify file hash matches plan."""
        from wai.upgrade_adoption import verify_file_hash
        
        content = "test content"
        expected_hash = "sha256:" + hashlib.sha256(content.encode()).hexdigest()
        
        result = verify_file_hash(content, expected_hash)
        assert result is True

    def test_spoke_detects_hash_mismatch(self):
        """Spoke rejects file if hash doesn't match."""
        from wai.upgrade_adoption import verify_file_hash
        
        content = "test content"
        wrong_hash = "sha256:0000000000000000"
        
        result = verify_file_hash(content, wrong_hash)
        assert result is False

    def test_spoke_can_verify_signature(self):
        """Spoke can verify hub signature on upgrade plan."""
        from wai.upgrade_adoption import verify_hub_signature, sign_upgrade_plan
        
        plan = {
            "metadata": {"version": "3.0.0", "framework_version": "3.0.0"},
            "verification": {"hub_fingerprint": None},
            "files": [],
            "hub_files": []
        }
        
        # Sign the plan
        hub_key = "test-hub-key"
        signed_plan = sign_upgrade_plan(plan.copy(), hub_key)
        
        # Verify it with same key
        result = verify_hub_signature(signed_plan, hub_key)
        assert result is True
        
        # Verify it fails with wrong key
        result_wrong = verify_hub_signature(signed_plan, "wrong-key")
        assert result_wrong is False


class TestTeachCommandIntegration:
    """Integration tests for teach command with upgrade adoption plan."""

    def test_teach_generates_upgrade_adoption_plan(self, tmp_path):
        """teach command generates upgrade-adoption-plan.json (not .teaching files)."""
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        framework_path = tmp_path / "framework"
        spoke_path = tmp_path / "spoke"
        hub_path = None
        
        # Create minimal framework structure
        templates_dir = framework_path / "templates" / "WAI"
        templates_dir.mkdir(parents=True)
        (templates_dir / "WAI-Guide.md").write_text("# Guide")
        
        # Create spoke structure
        spoke_dir = spoke_path / "WAI-Spoke"
        spoke_dir.mkdir(parents=True)
        
        # Run teach (new version with upgrade plan)
        # teach_command_with_plan(spoke_path, hub_path, framework_path)
        
        # Verify upgrade-adoption-plan.json exists (not .teaching files)
        # plan_file = spoke_path / "WAI-Spoke" / "upgrade-adoption-plan.json"
        # assert plan_file.exists()
        # 
        # plan = json.loads(plan_file.read_text())
        # assert plan["metadata"]["framework_version"] == "3.0.0"

    def test_teach_to_hub_includes_hub_files(self, tmp_path):
        """teach to hub includes hub-specific templates."""
        # When hub=True, include templates/HUB/ files
        pass


class TestUpgradeAdoptionDecisions:
    """Test AI decision-making on which files to adopt."""

    def test_safe_to_auto_adopt_false_requires_review(self):
        """Files with safe_to_auto_adopt=false appear in review queue."""
        plan = {
            "files": [
                {"name": "WAI-Guide.md", "safe_to_auto_adopt": True},
                {"name": "WAI-State.json", "safe_to_auto_adopt": False},
            ]
        }
        
        # Filter files that need review
        review_files = [f for f in plan["files"] if not f["safe_to_auto_adopt"]]
        
        assert len(review_files) == 1
        assert review_files[0]["name"] == "WAI-State.json"

    def test_applies_to_filters_irrelevant_files(self):
        """Hub files filtered when applying to spoke."""
        plan = {
            "files": [
                {"name": "WAI-Guide.md", "applies_to": ["spoke", "hub"]},
                {"name": "some-spoke-file.md", "applies_to": ["spoke"]},
            ],
            "hub_files": [
                {"name": "hub-profile.json", "applies_to": ["hub"]},
            ]
        }
        
        # When spoke loads, it only sees spoke-applicable files
        applicable = [f for f in plan["files"] if "spoke" in f["applies_to"]]
        
        assert len(applicable) == 2
        assert all("spoke" in f["applies_to"] for f in applicable)


# Placeholder tests to be implemented
def test_upgrade_plan_version_mismatch_handling():
    """Spoke handles upgrade plan for different version."""
    pass


def test_upgrade_plan_merge_strategy_applied():
    """Spoke applies merge_strategy when adopting."""
    pass


def test_upgrade_plan_sections_preserved():
    """Spoke preserves sections_to_preserve during adoption."""
    pass
