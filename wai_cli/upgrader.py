"""
Spoke Structure Upgrader

Handles detection and automatic upgrading of spoke structures from v1.0 to v2.0.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class SpokeUpgrader:
    """Handles detection and upgrading of spoke structures."""

    @staticmethod
    def detect_version(spoke_path: Path) -> str:
        """
        Detect spoke structure version.

        Returns:
            "1.0" - Old .WAI structure
            "2.0" - New WAI-Spoke structure with file index
            "unknown" - No valid structure found
        """
        old_dir = spoke_path / '.WAI'
        new_dir = spoke_path / 'WAI-Spoke'

        if new_dir.exists():
            index_file = new_dir / 'WAI-File-Index.json'
            if index_file.exists():
                try:
                    index_data = json.loads(index_file.read_text())
                    return index_data.get('version', '2.0')
                except:
                    return '2.0'
            return '2.0'  # Has WAI-Spoke but no index yet
        elif old_dir.exists():
            return '1.0'

        return 'unknown'

    @staticmethod
    def upgrade_spoke(spoke_path: Path, from_version: str, verbose: bool = True) -> bool:
        """
        Upgrade spoke structure to current version.

        Args:
            spoke_path: Path to spoke project
            from_version: Current version
            verbose: Print progress messages

        Returns:
            True if upgrade successful, False otherwise
        """
        if from_version == '1.0':
            return SpokeUpgrader._upgrade_from_v1(spoke_path, verbose=verbose)
        return False

    @staticmethod
    def _upgrade_from_v1(spoke_path: Path, verbose: bool = True) -> bool:
        """
        Upgrade from v1.0 (.WAI) to v2.0 (WAI-Spoke).

        Changes:
        - Rename .WAI/ → WAI-Spoke/
        - Rename files: wheel-signals.jsonl → WAI-Signals.jsonl, etc.
        - Create WAI-File-Index.json
        - Log upgrade decision to WAI-State.json

        Args:
            spoke_path: Path to spoke project
            verbose: Print progress messages

        Returns:
            True if successful
        """
        try:
            old_dir = spoke_path / '.WAI'
            new_dir = spoke_path / 'WAI-Spoke'

            if verbose:
                print(f"   Upgrading spoke structure: .WAI → WAI-Spoke")

            # Rename directory
            if old_dir.exists() and not new_dir.exists():
                old_dir.rename(new_dir)
            elif not new_dir.exists():
                if verbose:
                    print(f"   ✗ No .WAI directory found")
                return False

            # Rename files with old naming
            renames = [
                ('wheel-signals.jsonl', 'WAI-Signals.jsonl'),
                ('kb-sync.json', 'WAI-KB-Sync.json'),
                ('session-conversation.jsonl', 'WAI-Session-Log.jsonl'),
            ]

            for old_name, new_name in renames:
                old_file = new_dir / old_name
                new_file = new_dir / new_name
                if old_file.exists() and not new_file.exists():
                    old_file.rename(new_file)
                    if verbose:
                        print(f"   ✓ Renamed: {old_name} → {new_name}")

            # Create WAI-File-Index.json if it doesn't exist
            index_file = new_dir / 'WAI-File-Index.json'
            if not index_file.exists():
                SpokeUpgrader._create_file_index(spoke_path, new_dir)
                if verbose:
                    print(f"   ✓ Created WAI-File-Index.json")

            # Log upgrade to WAI-State.json
            SpokeUpgrader._log_upgrade(new_dir, '1.0', '2.0')
            if verbose:
                print(f"   ✓ Logged upgrade decision")

            if verbose:
                print(f"   ✓ Upgrade complete!")

            return True

        except Exception as e:
            if verbose:
                print(f"   ✗ Upgrade failed: {e}")
            return False

    @staticmethod
    def _create_file_index(spoke_path: Path, wai_dir: Path):
        """
        Create WAI-File-Index.json for a spoke.

        Args:
            spoke_path: Path to project root
            wai_dir: Path to WAI-Spoke directory
        """
        project_name = spoke_path.name

        index = {
            "version": "2.0",
            "metadata": {
                "spoke_path": str(wai_dir),
                "project_root": str(spoke_path),
                "project_name": project_name,
                "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated_by": "WAI Auto-Upgrade"
            },
            "core_files": {
                "WAI-State.json": {
                    "purpose": "Project state, decisions, session tracking",
                    "required": True,
                    "auto_managed": True
                },
                "WAI-Guide.md": {
                    "purpose": "AI behavioral instructions and protocols",
                    "required": True,
                    "auto_managed": False
                },
                "WAI-State.md": {
                    "purpose": "Strategic vision and evolution narrative",
                    "required": True,
                    "auto_managed": False
                },
                "WAI-File-Index.json": {
                    "purpose": "Manifest of all managed files and bidirectional attribution",
                    "required": True,
                    "auto_managed": True
                }
            },
            "operational_files": {
                "WAI-KB-Sync.json": {
                    "purpose": "Hub knowledge base sync metadata",
                    "required": False,
                    "auto_managed": True,
                    "cleanup": "safe_to_delete_if_stale"
                },
                "WAI-Signals.jsonl": {
                    "purpose": "Learning signals for hub ingestion",
                    "required": False,
                    "auto_managed": True,
                    "cleanup": "archive_after_hub_sync"
                },
                "WAI-Session-Log.jsonl": {
                    "purpose": "Conversation log for current session",
                    "required": False,
                    "auto_managed": True,
                    "cleanup": "delete_on_closeout"
                }
            },
            "project_files": {},
            "legacy_files": {}
        }

        index_file = wai_dir / 'WAI-File-Index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write('\n')

    @staticmethod
    def _log_upgrade(wai_dir: Path, from_version: str, to_version: str):
        """
        Log upgrade decision to WAI-State.json.

        Args:
            wai_dir: Path to WAI-Spoke directory
            from_version: Version upgraded from
            to_version: Version upgraded to
        """
        state_file = wai_dir / 'WAI-State.json'

        if not state_file.exists():
            return

        try:
            with open(state_file, encoding='utf-8') as f:
                state = json.load(f)

            # Add to decisions array
            decision = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "decision": f"Auto-upgraded spoke structure from v{from_version} to v{to_version}",
                "rationale": f"Framework auto-upgrade during sync. Migrated .WAI → WAI-Spoke, renamed files with WAI-* prefix, created file index.",
                "impact": 7,
                "by": "WAI Auto-Upgrade"
            }

            if 'decisions' not in state:
                state['decisions'] = []

            state['decisions'].append(decision)

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            print(f"   Warning: Could not log upgrade to WAI-State.json: {e}")

    @staticmethod
    def auto_upgrade_if_needed(spoke_path: Path, verbose: bool = True) -> bool:
        """
        Detect and automatically upgrade spoke if needed.

        Convenience method for use in sync operations.

        Args:
            spoke_path: Path to spoke project
            verbose: Print progress messages

        Returns:
            True if upgrade performed or not needed, False if upgrade failed
        """
        version = SpokeUpgrader.detect_version(spoke_path)

        if version == 'unknown':
            if verbose:
                print(f"   No spoke structure detected at {spoke_path}")
            return False

        if version == '1.0':
            if verbose:
                print(f"   Detected v1.0 spoke structure, upgrading...")
            return SpokeUpgrader.upgrade_spoke(spoke_path, '1.0', verbose=verbose)

        # Already v2.0 or newer
        return True
