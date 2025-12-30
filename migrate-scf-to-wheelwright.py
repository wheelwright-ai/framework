#!/usr/bin/env python3
"""
SCF/WWAI to Wheelwright (WAI) Migration Script

One-time converter to migrate SCF or WWAI hub and all registered spoke projects
to current Wheelwright naming conventions with token efficiency schema.

Handles migrations from:
- SCF (Session Continuity Framework) → WAI
- WWAI (intermediate naming) → WAI (current standard)

Usage:
    python3 migrate-scf-to-wheelwright.py [--hub-path PATH] [--dry-run]

If --hub-path is not specified, searches common locations.
"""

import argparse
import json
import shutil
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


class SCFToWheelwrightMigrator:
    """Migrates SCF hub and spokes to Wheelwright format."""

    def __init__(self, hub_path: Path, dry_run: bool = False):
        self.hub_path = hub_path
        self.dry_run = dry_run
        self.migrated_projects = []
        self.errors = []

    def log(self, message: str, indent: int = 0):
        """Print log message."""
        prefix = "  " * indent
        if self.dry_run:
            print(f"{prefix}[DRY-RUN] {message}")
        else:
            print(f"{prefix}{message}")

    def migrate_all(self):
        """Run full migration of hub and all spokes."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║         SCF → Wheelwright Migration Tool                     ║
║                                                              ║
║  "We aren't reinventing the wheel — we're evolving it        ║
║   faster than one person ever could."                        ║
╚══════════════════════════════════════════════════════════════╝
""")

        if self.dry_run:
            print(">>> DRY RUN MODE - No changes will be made <<<\n")

        # Step 1: Migrate the hub
        print(f"Hub path: {self.hub_path}\n")

        if not self.hub_path.exists():
            print(f"ERROR: Hub path does not exist: {self.hub_path}")
            return False

        print("=" * 60)
        print("STEP 1: Migrating Hub")
        print("=" * 60)
        self.migrate_hub()

        # Step 2: Get list of spoke projects
        print("\n" + "=" * 60)
        print("STEP 2: Finding Registered Projects")
        print("=" * 60)
        projects = self.get_registered_projects()

        if not projects:
            print("No projects found in registry.")
        else:
            print(f"Found {len(projects)} registered project(s)")

        # Step 3: Migrate each spoke project
        print("\n" + "=" * 60)
        print("STEP 3: Migrating Projects")
        print("=" * 60)

        for proj in projects:
            proj_path = Path(proj.get('path', ''))
            if proj_path.exists():
                print(f"\n→ {proj.get('name', proj_path.name)}")
                self.migrate_spoke(proj_path)
            else:
                self.log(f"Skipping (path not found): {proj_path}", 1)

        # Summary
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print(f"\nMigrated: {len(self.migrated_projects)} project(s)")
        if self.errors:
            print(f"Errors: {len(self.errors)}")
            for err in self.errors:
                print(f"  - {err}")

        if self.dry_run:
            print("\n>>> This was a DRY RUN. Run without --dry-run to apply changes. <<<")

        return True

    def migrate_hub(self):
        """Migrate the SCF hub to Wheelwright format."""

        # Rename .scf-registry → .WAI-registry
        old_registry = self.hub_path / '.scf-registry'
        old_wwai_registry = self.hub_path / '.wwai-registry'
        new_registry = self.hub_path / '.WAI-registry'

        if old_registry.exists() and not new_registry.exists():
            self.log("Renaming .scf-registry → .WAI-registry", 1)
            if not self.dry_run:
                old_registry.rename(new_registry)
        elif old_wwai_registry.exists() and not new_registry.exists():
            self.log("Renaming .wwai-registry → .WAI-registry", 1)
            if not self.dry_run:
                old_wwai_registry.rename(new_registry)

        # Rename spoke-projects.json → wheel-projects.json
        registry_dir = new_registry if new_registry.exists() else old_registry
        if registry_dir.exists():
            old_spoke_projects = registry_dir / 'spoke-projects.json'
            new_wheel_projects = registry_dir / 'wheel-projects.json'

            if old_spoke_projects.exists() and not new_wheel_projects.exists():
                self.log("Renaming spoke-projects.json → wheel-projects.json", 1)
                if not self.dry_run:
                    # Also update content
                    data = json.loads(old_spoke_projects.read_text())
                    data = self.update_json_content(data)
                    new_wheel_projects.write_text(json.dumps(data, indent=2))
                    old_spoke_projects.unlink()

            # Rename spokes/ → wheels/
            old_spokes_dir = registry_dir / 'spokes'
            new_wheels_dir = registry_dir / 'wheels'
            if old_spokes_dir.exists() and not new_wheels_dir.exists():
                self.log("Renaming spokes/ → wheels/", 1)
                if not self.dry_run:
                    old_spokes_dir.rename(new_wheels_dir)

        # Migrate hub's own .scf → .wwai
        self.migrate_spoke(self.hub_path)

        # Update hub-profile.json
        hub_profile = self.hub_path / 'hub-profile.json'
        if hub_profile.exists():
            self.log("Updating hub-profile.json", 1)
            if not self.dry_run:
                data = json.loads(hub_profile.read_text())
                data = self.update_json_content(data)
                hub_profile.write_text(json.dumps(data, indent=2))

        self.migrated_projects.append(str(self.hub_path))

    def migrate_spoke(self, project_path: Path):
        """Migrate a single spoke project to Wheelwright format."""

        # Rename .scf → .WAI (or .wwai → .WAI)
        old_scf_dir = project_path / '.scf'
        old_wwai_dir = project_path / '.wwai'
        new_wai_dir = project_path / '.WAI'

        if old_scf_dir.exists() and not new_wai_dir.exists():
            self.log("Renaming .scf/ → .WAI/", 1)
            if not self.dry_run:
                old_scf_dir.rename(new_wai_dir)
        elif old_wwai_dir.exists() and not new_wai_dir.exists():
            self.log("Renaming .wwai/ → .WAI/", 1)
            if not self.dry_run:
                old_wwai_dir.rename(new_wai_dir)

        # Work with whichever directory exists
        wai_dir = new_wai_dir if new_wai_dir.exists() else (old_wwai_dir if old_wwai_dir.exists() else old_scf_dir)

        if not wai_dir.exists():
            self.log("No .scf, .wwai, or .WAI directory found, skipping", 1)
            return

        # File renames within the directory
        renames = [
            ('BUILDSTATE.json', 'WAI-State.json'),
            ('buildstate.json', 'WAI-State.json'),
            ('BUILDSTATE.md', 'WAI-State.md'),
            ('buildstate.md', 'WAI-State.md'),
            ('SCF_README.md', 'WAI-Guide.md'),
            ('spoke-signals.jsonl', 'wheel-signals.jsonl'),
            ('WWAI-State.json', 'WAI-State.json'),
            ('WWAI-State.md', 'WAI-State.md'),
            ('WWAI-Guide.md', 'WAI-Guide.md'),
        ]

        for old_name, new_name in renames:
            old_file = wai_dir / old_name
            new_file = wai_dir / new_name

            if old_file.exists() and not new_file.exists():
                self.log(f"Renaming {old_name} → {new_name}", 1)
                if not self.dry_run:
                    if old_name.endswith('.json') and not old_name.endswith('.jsonl'):
                        # Update JSON content
                        try:
                            data = json.loads(old_file.read_text())
                            data = self.update_json_content(data)
                            new_file.write_text(json.dumps(data, indent=2))
                            old_file.unlink()
                        except json.JSONDecodeError:
                            old_file.rename(new_file)
                    elif old_name.endswith('.md'):
                        # Update markdown content
                        content = old_file.read_text()
                        content = self.update_md_content(content)
                        new_file.write_text(content)
                        old_file.unlink()
                    else:
                        old_file.rename(new_file)

        # Handle root-level buildstate files (legacy v1 structure)
        root_renames = [
            ('buildstate.json', '.WAI/WAI-State.json'),
            ('BUILDSTATE.json', '.WAI/WAI-State.json'),
            ('buildstate.md', '.WAI/WAI-State.md'),
            ('BUILDSTATE.md', '.WAI/WAI-State.md'),
        ]

        for old_name, new_path in root_renames:
            old_file = project_path / old_name
            new_file = project_path / new_path

            if old_file.exists() and not new_file.exists():
                self.log(f"Moving {old_name} → {new_path}", 1)
                if not self.dry_run:
                    new_file.parent.mkdir(exist_ok=True)
                    if old_name.endswith('.json'):
                        try:
                            data = json.loads(old_file.read_text())
                            data = self.update_json_content(data)
                            new_file.write_text(json.dumps(data, indent=2))
                            old_file.unlink()
                        except json.JSONDecodeError:
                            shutil.move(str(old_file), str(new_file))
                    else:
                        shutil.move(str(old_file), str(new_file))

        self.migrated_projects.append(str(project_path))

    def update_json_content(self, data: Any) -> Any:
        """Recursively update JSON content with new naming."""
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                # Update keys
                new_key = self.transform_key(key)
                # Recursively update values
                new_data[new_key] = self.update_json_content(value)

            # Add wheelwright metadata if this looks like a state file
            if '_scf_metadata' in data or '_scf_bootstrap' in data:
                # Transform _scf_metadata to wheelwright
                if '_scf_metadata' in new_data:
                    scf_meta = new_data.pop('_scf_metadata', {})
                    new_data['wheelwright'] = {
                        'version': '1.0.0',
                        'structure_version': 'v1',
                        'description': scf_meta.get('description', 'Wheelwright-enabled project'),
                        'framework_path': scf_meta.get('framework_path'),
                        'hub_path': scf_meta.get('hub_path'),
                        'migrated_from_scf': scf_meta.get('version', 'unknown'),
                        'migrated_at': datetime.now(timezone.utc).isoformat()
                    }
                if '_scf_bootstrap' in new_data:
                    bootstrap = new_data.pop('_scf_bootstrap')
                    new_data['_project_foundation'] = self.update_json_content(bootstrap)

            # Add token efficiency schema fields if this looks like WAI-State.json
            if 'context' in new_data and isinstance(new_data['context'], dict):
                # Add complexity_thresholds if missing
                if 'complexity_thresholds' not in new_data['context']:
                    new_data['context']['complexity_thresholds'] = {
                        'multi_file_threshold': 2,
                        'step_count_threshold': 6,
                        'checkpoint_interval': 3,
                        'description': 'Thresholds for ADAPTIVE workflow mode - when to enforce STRICT vs YOLO'
                    }

                # Add capacity_management if missing
                if 'capacity_management' not in new_data['context']:
                    new_data['context']['capacity_management'] = {
                        'current_capacity_estimate': 0.0,
                        'warning_threshold': 0.80,
                        'critical_threshold': 0.90,
                        'last_compact_at': None,
                        'compact_frequency': 'before_closeout_or_shipit',
                        'description': 'Token capacity tracking and auto-compact triggers'
                    }

            # Add token efficiency fields to ai_context if present
            if 'ai_context' in new_data and isinstance(new_data['ai_context'], dict):
                if 'workflow_mode' not in new_data['ai_context']:
                    new_data['ai_context']['workflow_mode'] = 'ADAPTIVE'
                if 'plan_template_version' not in new_data['ai_context']:
                    new_data['ai_context']['plan_template_version'] = 'v1.0'
                if 'token_efficiency_protocols' not in new_data['ai_context']:
                    new_data['ai_context']['token_efficiency_protocols'] = 'v1.0'
                # Add compact command to wwai_commands if present
                if 'wwai_commands' in new_data['ai_context'] and isinstance(new_data['ai_context']['wwai_commands'], dict):
                    if 'compact' not in new_data['ai_context']['wwai_commands']:
                        new_data['ai_context']['wwai_commands']['compact'] = 'Compress context and balance WAI files'

            return new_data

        elif isinstance(data, list):
            return [self.update_json_content(item) for item in data]
        elif isinstance(data, str):
            return self.transform_string(data)
        else:
            return data

    def transform_key(self, key: str) -> str:
        """Transform a JSON key from SCF/WWAI to WAI naming."""
        replacements = {
            '_scf_metadata': 'wheelwright',
            '_scf_bootstrap': '_project_foundation',
            '_wwai_bootstrap': '_project_foundation',
            'scf_enabled': 'wai_enabled',
            'scf_version': 'wai_version',
            'wwai_enabled': 'wai_enabled',
            'wwai_version': 'wai_version',
            'spoke_projects': 'wheel_projects',
            'spoke-signals': 'wheel-signals',
            'wwai_commands': 'wwai_commands',  # Keep as is for now
        }
        return replacements.get(key, key)

    def transform_string(self, text: str) -> str:
        """Transform string content from SCF/WWAI to WAI naming."""
        replacements = [
            # SCF → Wheelwright
            ('Session Continuity Framework', 'Wheelwright Framework'),
            ('SCF Hub', 'Wheelwright Hub'),
            ('SCF-enabled', 'Wheelwright-enabled'),
            # CLI commands
            ('scf hub', 'WAI hub'),
            ('scf init', 'WAI init'),
            ('scf sync', 'WAI sync'),
            ('scf status', 'WAI status'),
            ('./scf ', './WAI '),
            ('wwai hub', 'WAI hub'),
            ('wwai init', 'WAI init'),
            ('wwai sync', 'WAI sync'),
            ('wwai status', 'WAI status'),
            ('./wwai ', './WAI '),
            # Directories
            ('scf-hub', 'wheelwright-hub'),
            ('.scf-hub', '.wheelwright-hub'),
            ('.scf/', '.WAI/'),
            ('.wwai/', '.WAI/'),
            ('.scf-registry', '.WAI-registry'),
            ('.wwai-registry', '.WAI-registry'),
            # Files
            ('BUILDSTATE.json', 'WAI-State.json'),
            ('BUILDSTATE.md', 'WAI-State.md'),
            ('buildstate.json', 'WAI-State.json'),
            ('buildstate.md', 'WAI-State.md'),
            ('SCF_README.md', 'WAI-Guide.md'),
            ('WWAI-State.json', 'WAI-State.json'),
            ('WWAI-State.md', 'WAI-State.md'),
            ('WWAI-Guide.md', 'WAI-Guide.md'),
            ('spoke-signals.jsonl', 'wheel-signals.jsonl'),
            ('spoke-projects.json', 'wheel-projects.json'),
            # GitHub
            ('github.com/mariov96/session-continuity-framework', 'github.com/wheelwright-ai/framework'),
        ]

        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        return result

    def update_md_content(self, content: str) -> str:
        """Update markdown content with new naming."""
        return self.transform_string(content)

    def get_registered_projects(self) -> List[Dict]:
        """Get list of projects from hub registry."""
        # Check all possible registry locations (old to new)
        registry_paths = [
            self.hub_path / '.WAI-registry' / 'wheel-projects.json',
            self.hub_path / '.wwai-registry' / 'wheel-projects.json',
            self.hub_path / '.wwai-registry' / 'spoke-projects.json',
            self.hub_path / '.scf-registry' / 'spoke-projects.json',
            self.hub_path / '.scf-registry' / 'wheel-projects.json',
        ]

        for reg_path in registry_paths:
            if reg_path.exists():
                try:
                    data = json.loads(reg_path.read_text())
                    return data.get('projects', [])
                except json.JSONDecodeError:
                    self.errors.append(f"Invalid JSON in {reg_path}")
                    continue

        return []


def find_scf_hub() -> Optional[Path]:
    """Find existing SCF hub location."""
    import os

    # Check environment variable
    env_hub = os.environ.get('SCF_HUB_PATH')
    if env_hub:
        env_path = Path(env_hub).expanduser()
        if env_path.exists():
            return env_path

    # Check common locations
    common_paths = [
        Path.home() / 'scf-hub',
        Path.home() / '.scf-hub',
        Path.home() / 'projects' / 'scf-hub',
        Path.home() / 'wheelwright-hub',
        Path.home() / '.wheelwright-hub',
    ]

    for path in common_paths:
        if (path / 'hub-profile.json').exists():
            return path
        if (path / '.scf-registry').exists():
            return path
        if (path / '.scf').exists():
            return path

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Migrate SCF/WWAI hub and projects to current Wheelwright (WAI) format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 migrate-scf-to-wheelwright.py
  python3 migrate-scf-to-wheelwright.py --dry-run
  python3 migrate-scf-to-wheelwright.py --hub-path ~/scf-hub

This script will:
  1. Rename .scf/ or .wwai/ directories → .WAI/
  2. Rename .scf-registry or .wwai-registry → .WAI-registry
  3. Rename BUILDSTATE.json or WWAI-State.json → WAI-State.json
  4. Rename BUILDSTATE.md or WWAI-State.md → WAI-State.md
  5. Rename SCF_README.md or WWAI-Guide.md → WAI-Guide.md
  6. Rename spoke-signals.jsonl → wheel-signals.jsonl
  7. Add token efficiency schema fields to WAI-State.json:
     - context.complexity_thresholds
     - context.capacity_management
     - ai_context.workflow_mode (ADAPTIVE)
     - ai_context.token_efficiency_protocols (v1.0)
  8. Update internal references from SCF/WWAI to WAI
  9. Migrate hub registry and all registered projects

Note: Platform templates (Cursor, VS Code, etc.) are new features and won't be migrated.
      Run 'WAI init' in each project after migration to generate them.
        '''
    )

    parser.add_argument(
        '--hub-path',
        type=Path,
        help='Path to SCF hub (auto-detected if not specified)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Find hub
    hub_path = args.hub_path
    if hub_path:
        hub_path = hub_path.expanduser().resolve()
    else:
        hub_path = find_scf_hub()
        if not hub_path:
            print("ERROR: Could not find SCF hub.")
            print("Please specify with --hub-path")
            return 1

    # Run migration
    migrator = SCFToWheelwrightMigrator(hub_path, dry_run=args.dry_run)
    success = migrator.migrate_all()

    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
