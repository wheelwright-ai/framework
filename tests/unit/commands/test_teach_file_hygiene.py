"""
Unit tests for teach command file hygiene feature.

Tests automatic cleanup of deprecated template files while preserving
user-provided content and teachings from other sources.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from wai.commands.teach import cleanup_deprecated_templates


class TestTeachFileHygiene:
    """Test automatic cleanup of deprecated template files."""

    @pytest.fixture
    def spoke_path(self, tmp_path):
        """Create a test spoke directory structure."""
        spoke = tmp_path / "test-spoke"
        spoke.mkdir()
        (spoke / "WAI-Spoke").mkdir()
        (spoke / "WAI-Spoke" / "seed").mkdir()
        (spoke / "WAI-Spoke" / "seed" / "ingest").mkdir()
        return spoke

    @pytest.fixture
    def hub_fingerprint(self):
        """Return a test hub fingerprint."""
        return "test-hub-fp-12345"

    def test_no_cleanup_without_previous_plan(self, spoke_path, hub_fingerprint):
        """No cleanup when there's no previous upgrade plan."""
        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)
        assert removed == 0

    def test_no_cleanup_when_fingerprint_mismatch(self, spoke_path, hub_fingerprint):
        """Preserve files when hub fingerprint doesn't match (different hub)."""
        # Create previous plan with different fingerprint
        prev_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'},
                {'name': 'old-file.md', 'path': 'WAI-Spoke/old-file.md'}
            ],
            'hub_files': [],
            'verification': {
                'hub_fingerprint': 'different-hub-fp-99999'
            }
        }

        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text(json.dumps(prev_plan))

        # Create old file in ingest
        ingest_dir = spoke_path / 'WAI-Spoke' / 'seed' / 'ingest'
        (ingest_dir / 'old-file.md.teaching').write_text('old content')

        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)

        assert removed == 0
        assert (ingest_dir / 'old-file.md.teaching').exists()  # Preserved

    def test_removes_deprecated_template_files(self, spoke_path, hub_fingerprint):
        """Remove files that were in previous plan but not in current plan."""
        # Create previous plan
        prev_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'},
                {'name': 'old-template.md', 'path': 'WAI-Spoke/old-template.md'}
            ],
            'hub_files': [
                {'name': 'hub-old-file.json', 'path': 'hub-old-file.json'}
            ],
            'verification': {
                'hub_fingerprint': hub_fingerprint
            }
        }

        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text(json.dumps(prev_plan))

        # Create deprecated files in ingest
        ingest_dir = spoke_path / 'WAI-Spoke' / 'seed' / 'ingest'
        (ingest_dir / 'old-template.md.teaching').write_text('deprecated')
        (ingest_dir / 'hub-old-file.json').write_text('deprecated hub file')

        # Current plan doesn't include these files
        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)

        assert removed == 2
        assert not (ingest_dir / 'old-template.md.teaching').exists()
        assert not (ingest_dir / 'hub-old-file.json').exists()

    def test_preserves_current_template_files(self, spoke_path, hub_fingerprint):
        """Don't remove files that are still in the current plan."""
        # Create previous plan
        prev_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': [],
            'verification': {
                'hub_fingerprint': hub_fingerprint
            }
        }

        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text(json.dumps(prev_plan))

        # Create current file in ingest
        ingest_dir = spoke_path / 'WAI-Spoke' / 'seed' / 'ingest'
        (ingest_dir / 'WAI-Guide.md.teaching').write_text('current content')

        # Current plan still includes this file
        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)

        assert removed == 0
        assert (ingest_dir / 'WAI-Guide.md.teaching').exists()  # Preserved

    def test_preserves_user_provided_files(self, spoke_path, hub_fingerprint):
        """Don't remove files that were never in any plan (user-provided)."""
        # Create previous plan (doesn't include custom-file.json)
        prev_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': [],
            'verification': {
                'hub_fingerprint': hub_fingerprint
            }
        }

        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text(json.dumps(prev_plan))

        # Create user-provided file (not in any plan)
        ingest_dir = spoke_path / 'WAI-Spoke' / 'seed' / 'ingest'
        (ingest_dir / 'custom-file.json').write_text('user content')

        # Current plan also doesn't include it
        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)

        assert removed == 0
        assert (ingest_dir / 'custom-file.json').exists()  # User file preserved

    def test_handles_missing_ingest_directory(self, spoke_path, hub_fingerprint):
        """Handle case where ingest directory doesn't exist."""
        current_plan = {
            'files': [{'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}],
            'hub_files': []
        }

        # Remove ingest directory
        import shutil
        shutil.rmtree(spoke_path / 'WAI-Spoke' / 'seed' / 'ingest')

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)
        assert removed == 0  # No error, just returns 0

    def test_handles_corrupted_previous_plan(self, spoke_path, hub_fingerprint):
        """Handle case where previous plan JSON is corrupted."""
        # Create corrupted plan file
        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text('invalid json {{{')

        current_plan = {
            'files': [{'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}],
            'hub_files': []
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)
        assert removed == 0  # Gracefully handles error

    def test_removes_both_spoke_and_hub_deprecated_files(self, spoke_path, hub_fingerprint):
        """Remove deprecated files from both spoke and hub file lists."""
        # Create previous plan with both types
        prev_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'},
                {'name': 'old-spoke-file.md', 'path': 'WAI-Spoke/old-spoke-file.md'}
            ],
            'hub_files': [
                {'name': 'AGENTS.md', 'path': 'AGENTS.md'},
                {'name': 'hub-registry.json', 'path': 'hub-registry.json'}
            ],
            'verification': {
                'hub_fingerprint': hub_fingerprint
            }
        }

        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        plan_path.write_text(json.dumps(prev_plan))

        # Create deprecated files
        ingest_dir = spoke_path / 'WAI-Spoke' / 'seed' / 'ingest'
        (ingest_dir / 'old-spoke-file.md.teaching').write_text('deprecated spoke')
        (ingest_dir / 'AGENTS.md').write_text('deprecated hub file')
        (ingest_dir / 'hub-registry.json').write_text('deprecated hub file')

        # Current plan doesn't include deprecated files
        current_plan = {
            'files': [
                {'name': 'WAI-Guide.md', 'path': 'WAI-Spoke/WAI-Guide.md'}
            ],
            'hub_files': []  # No hub files for spokes anymore
        }

        removed = cleanup_deprecated_templates(spoke_path, current_plan, hub_fingerprint)

        assert removed == 3
        assert not (ingest_dir / 'old-spoke-file.md.teaching').exists()
        assert not (ingest_dir / 'AGENTS.md').exists()
        assert not (ingest_dir / 'hub-registry.json').exists()


class TestHubFileDistribution:
    """Test that hub files are only sent to hubs, not spokes."""

    def test_hub_files_only_for_hub_targets(self):
        """Hub files should only be distributed when is_hub_target is True."""
        # This is tested through integration, but the key logic is:
        # In teach.py, hub file distribution is wrapped in:
        # if is_hub_target and 'hub_files' in locals():
        #     distribute hub files
        # This ensures hub files never go to regular spokes
        pass  # Covered by integration tests
