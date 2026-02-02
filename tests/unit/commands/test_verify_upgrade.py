"""
Unit tests for upgrade verification and adoption.

Test-driven implementation of:
- verify_upgrade_command: Load plan and verify integrity
- Signature verification (hub key validation)
- File hash verification
- Adoption decision generation
- File adoption execution
"""

import json
import hashlib
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestVerifyUpgradeLoading:
    """Test loading upgrade-adoption-plan.json from spoke."""

    def test_load_plan_from_spoke(self, tmp_path):
        """Load upgrade-adoption-plan.json from spoke root."""
        from wai.commands.verify_upgrade import _load_plan_file
        
        # Create test plan
        plan = {
            "metadata": {
                "version": "3.0.0",
                "framework_version": "3.0.0",
                "created_at": "2026-02-01T00:00:00Z"
            },
            "verification": {
                "hub_fingerprint": "test-sig",
                "hash_algorithm": "sha256-hmac"
            },
            "files": [],
            "hub_files": []
        }
        
        plan_path = tmp_path / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(plan))
        
        loaded = _load_plan_file(tmp_path)
        assert loaded is not None
        assert loaded["metadata"]["framework_version"] == "3.0.0"

    def test_load_plan_missing_returns_none(self, tmp_path):
        """Load returns None if plan doesn't exist."""
        from wai.commands.verify_upgrade import _load_plan_file
        
        loaded = _load_plan_file(tmp_path)
        assert loaded is None


class TestVerifyIntegrity:
    """Test file hash verification."""

    def test_verify_plan_integrity_all_files_present(self, tmp_path):
        """Verify all files in plan are present in ingest."""
        from wai.commands.verify_upgrade import _verify_plan_integrity
        from wai.reference_manager import TeachingManager
        
        # Create test files
        content = "test content"
        file_hash = "sha256:" + hashlib.sha256(content.encode()).hexdigest()
        
        # Setup ingest directory
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        (ingest_dir / "test.md.teaching").write_text(content)
        
        # Create plan
        plan = {
            "files": [
                {
                    "name": "test.md",
                    "hash": file_hash,
                    "path": "WAI-Spoke/test.md"
                }
            ],
            "hub_files": []
        }
        
        # Mock TeachingManager
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        is_valid, errors = _verify_plan_integrity(plan, teach_manager)
        assert is_valid
        assert len(errors) == 0

    def test_verify_plan_integrity_missing_file(self, tmp_path):
        """Detect when file is missing from ingest."""
        from wai.commands.verify_upgrade import _verify_plan_integrity
        
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        
        plan = {
            "files": [
                {
                    "name": "missing.md",
                    "hash": "sha256:abc123",
                    "path": "WAI-Spoke/missing.md"
                }
            ],
            "hub_files": []
        }
        
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        is_valid, errors = _verify_plan_integrity(plan, teach_manager)
        assert not is_valid
        assert any("Missing file" in err for err in errors)

    def test_verify_plan_integrity_hash_mismatch(self, tmp_path):
        """Detect when file hash doesn't match."""
        from wai.commands.verify_upgrade import _verify_plan_integrity
        
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        
        content = "actual content"
        wrong_hash = "sha256:wronghash123456789"
        
        (ingest_dir / "test.md.teaching").write_text(content)
        
        plan = {
            "files": [
                {
                    "name": "test.md",
                    "hash": wrong_hash,
                    "path": "WAI-Spoke/test.md"
                }
            ],
            "hub_files": []
        }
        
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        is_valid, errors = _verify_plan_integrity(plan, teach_manager)
        assert not is_valid
        assert any("Hash mismatch" in err for err in errors)


class TestHubSignatureVerification:
    """Test hub signature verification."""

    def test_verify_hub_signature_valid(self, tmp_path):
        """Verify valid hub signature."""
        from wai.upgrade_adoption import sign_upgrade_plan, verify_hub_signature
        
        # Create plan and sign
        plan = {
            "files": [],
            "hub_files": [],
            "metadata": {"framework_version": "3.0.0"},
            "verification": {
                "hub_fingerprint": None,
                "signed_by": "test"
            }
        }
        
        hub_key = "test-hub-key-secret"
        plan = sign_upgrade_plan(plan, hub_key)
        
        # Verify signature
        assert verify_hub_signature(plan, hub_key)

    def test_verify_hub_signature_invalid_key(self, tmp_path):
        """Reject signature with wrong key."""
        from wai.upgrade_adoption import sign_upgrade_plan, verify_hub_signature
        
        plan = {
            "files": [],
            "hub_files": [],
            "metadata": {"framework_version": "3.0.0"},
            "verification": {
                "hub_fingerprint": None,
                "signed_by": "test"
            }
        }
        
        hub_key = "test-hub-key-secret"
        plan = sign_upgrade_plan(plan, hub_key)
        
        # Try with wrong key
        assert not verify_hub_signature(plan, "wrong-key")

    def test_verify_hub_signature_missing(self):
        """Handle missing signature gracefully."""
        from wai.upgrade_adoption import verify_hub_signature
        
        plan = {
            "verification": {
                "hub_fingerprint": None
            }
        }
        
        assert not verify_hub_signature(plan, "any-key")


class TestAdoptionDecisions:
    """Test adoption decision generation."""

    def test_get_adoption_decisions_auto_adopt(self):
        """Auto-adopt safe files."""
        from wai.commands.verify_upgrade import get_adoption_decisions
        
        plan = {
            "files": [
                {
                    "name": "file1.md",
                    "safe_to_auto_adopt": True,
                    "requires_review": False
                }
            ]
        }
        
        decisions = get_adoption_decisions(plan)
        assert "file1.md" in decisions["adopt"]
        assert "file1.md" not in decisions["review"]
        assert "file1.md" not in decisions["defer"]

    def test_get_adoption_decisions_requires_review(self):
        """Mark files needing review."""
        from wai.commands.verify_upgrade import get_adoption_decisions
        
        plan = {
            "files": [
                {
                    "name": "file2.json",
                    "safe_to_auto_adopt": False,
                    "requires_review": True
                }
            ]
        }
        
        decisions = get_adoption_decisions(plan)
        assert "file2.json" in decisions["review"]
        assert "file2.json" not in decisions["adopt"]

    def test_get_adoption_decisions_mixed(self):
        """Handle mix of safe and review files."""
        from wai.commands.verify_upgrade import get_adoption_decisions
        
        plan = {
            "files": [
                {
                    "name": "safe.md",
                    "safe_to_auto_adopt": True,
                    "requires_review": False
                },
                {
                    "name": "review.json",
                    "safe_to_auto_adopt": False,
                    "requires_review": True
                }
            ]
        }
        
        decisions = get_adoption_decisions(plan)
        assert "safe.md" in decisions["adopt"]
        assert "review.json" in decisions["review"]


class TestExecuteAdoptions:
    """Test file adoption execution."""

    def test_execute_adoptions_copies_files(self, tmp_path):
        """Execute adoption copies files from ingest to final location."""
        from wai.commands.verify_upgrade import execute_adoptions
        
        # Setup
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        
        content = "file content"
        (ingest_dir / "test.md.teaching").write_text(content)
        
        plan = {
            "files": [
                {
                    "name": "test.md",
                    "path": "WAI-Spoke/test.md"
                }
            ],
            "hub_files": []
        }
        
        decisions = {
            "adopt": ["test.md"],
            "review": [],
            "defer": []
        }
        
        # Mock TeachingManager
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        with patch('wai.commands.verify_upgrade.TeachingManager', return_value=teach_manager):
            result = execute_adoptions(tmp_path, plan, decisions)
        
        # Verify file was copied
        target = tmp_path / "WAI-Spoke" / "test.md"
        assert target.exists()
        assert target.read_text() == content

    def test_execute_adoptions_creates_directories(self, tmp_path):
        """Create necessary directories when adopting."""
        from wai.commands.verify_upgrade import execute_adoptions
        
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        
        (ingest_dir / "nested.md.teaching").write_text("content")
        
        plan = {
            "files": [
                {
                    "name": "nested.md",
                    "path": "WAI-Spoke/nested/deep/file.md"
                }
            ],
            "hub_files": []
        }
        
        decisions = {
            "adopt": ["nested.md"],
            "review": [],
            "defer": []
        }
        
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        with patch('wai.commands.verify_upgrade.TeachingManager', return_value=teach_manager):
            result = execute_adoptions(tmp_path, plan, decisions)
        
        # Verify directory structure created
        target = tmp_path / "WAI-Spoke" / "nested" / "deep"
        assert target.exists()
        assert target.is_dir()

    def test_execute_adoptions_skip_missing_files(self, tmp_path):
        """Skip adoption if ingest file is missing."""
        from wai.commands.verify_upgrade import execute_adoptions
        
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        
        plan = {
            "files": [
                {
                    "name": "missing.md",
                    "path": "WAI-Spoke/missing.md"
                }
            ],
            "hub_files": []
        }
        
        decisions = {
            "adopt": ["missing.md"],
            "review": [],
            "defer": []
        }
        
        teach_manager = Mock()
        teach_manager.ingest_dir = ingest_dir
        
        with patch('wai.commands.verify_upgrade.TeachingManager', return_value=teach_manager):
            result = execute_adoptions(tmp_path, plan, decisions)
        
        # Should still return but with error count
        target = tmp_path / "WAI-Spoke" / "missing.md"
        assert not target.exists()


class TestMergeStrategy:
    """Test merge strategy support."""

    def test_file_entry_includes_merge_strategy(self, tmp_path):
        """File entries can specify merge strategy."""
        test_file = tmp_path / "state.json"
        test_file.write_text("{}")
        
        from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder
        
        builder = UpgradeAdoptionPlanBuilder("3.0.0", "3.0")
        builder.add_file(
            name="WAI-State.json",
            path="WAI-Spoke/WAI-State.json",
            source_path=str(test_file),
            merge_strategy="merge_sections",
            sections_to_preserve=["_session_state", "_project_foundation"],
            sections_to_update=["wheelwright"]
        )
        plan = builder.build()
        
        file_entry = plan["files"][0]
        assert file_entry["merge_strategy"] == "merge_sections"
        assert "_session_state" in file_entry["sections_to_preserve"]
        assert "wheelwright" in file_entry["sections_to_update"]


class TestVerifyUpgradeCommand:
    """Test verify_upgrade_command main function."""

    def test_verify_upgrade_command_success(self, tmp_path):
        """verify_upgrade_command returns True for valid plan."""
        from wai.commands.verify_upgrade import verify_upgrade_command
        from wai.upgrade_adoption import sign_upgrade_plan
        
        # Setup plan
        content = "test"
        file_hash = "sha256:" + hashlib.sha256(content.encode()).hexdigest()
        
        plan = {
            "metadata": {
                "framework_version": "3.0.0",
                "created_at": "2026-02-01T00:00:00Z"
            },
            "verification": {
                "hub_fingerprint": None,
                "signed_by": "test"
            },
            "files": [
                {
                    "name": "test.md",
                    "hash": file_hash,
                    "safe_to_auto_adopt": True,
                    "requires_review": False,
                    "applies_to": ["spoke"],
                    "version": "3.0.0",
                    "changed_from": "2.0.0",
                    "why_changed": "Test",
                    "mentions": []
                }
            ],
            "hub_files": [],
            "adoption_guidance": {}
        }
        
        # Sign plan
        hub_key = "test-key"
        plan = sign_upgrade_plan(plan, hub_key)
        
        # Save plan
        plan_path = tmp_path / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(plan))
        
        # Create ingest file
        ingest_dir = tmp_path / "seed" / "ingest"
        ingest_dir.mkdir(parents=True)
        (ingest_dir / "test.md.teaching").write_text(content)
        
        # Mock TeachingManager
        with patch('wai.commands.verify_upgrade.TeachingManager') as tm:
            tm.return_value.ingest_dir = ingest_dir
            result = verify_upgrade_command(tmp_path, hub_key)
        
        assert result is True

    def test_verify_upgrade_command_no_plan(self, tmp_path):
        """verify_upgrade_command returns False if no plan exists."""
        from wai.commands.verify_upgrade import verify_upgrade_command
        
        result = verify_upgrade_command(tmp_path)
        assert result is False

    def test_verify_upgrade_command_invalid_signature(self, tmp_path):
        """verify_upgrade_command returns False for invalid signature."""
        from wai.commands.verify_upgrade import verify_upgrade_command
        from wai.upgrade_adoption import sign_upgrade_plan
        
        plan = {
            "metadata": {
                "framework_version": "3.0.0",
                "created_at": "2026-02-01T00:00:00Z"
            },
            "verification": {
                "hub_fingerprint": None,
                "signed_by": "test"
            },
            "files": [],
            "hub_files": [],
            "adoption_guidance": {}
        }
        
        # Sign with one key
        plan = sign_upgrade_plan(plan, "key1")
        
        # Save
        plan_path = tmp_path / "upgrade-adoption-plan.json"
        plan_path.write_text(json.dumps(plan))
        
        # Try to verify with different key
        result = verify_upgrade_command(tmp_path, "key2")
        assert result is False
