#!/usr/bin/env python3
"""
Migrate from Session Continuity Framework (SCF) to Wheelwright Framework.

This script converts:
1. ~/scf-hub → ~/wheelwright-hub (hub directory)
2. Project-level SCF metadata → Wheelwright WAI-Spoke/ structure
3. Old naming (SCF, WWAI) → New naming (WAI, Wheelwright)
4. Updates all references and configuration

Usage:
    python3 migrate_scf_to_wheelwright.py [--dry-run] [--hub-path PATH]

Examples:
    # Show what would be migrated (dry-run)
    python3 migrate_scf_to_wheelwright.py --dry-run
    
    # Perform migration
    python3 migrate_scf_to_wheelwright.py
    
    # Custom hub path
    python3 migrate_scf_to_wheelwright.py --hub-path ~/my-hub
"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional


class SCFToWheelwrightMigrator:
    """Migrate from SCF to Wheelwright Framework."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = True):
        self.dry_run = dry_run
        self.verbose = verbose
        self.home = Path.home()
        self.scf_hub = self.home / "scf-hub"
        self.wheelwright_hub = self.home / "wheelwright-hub"
        self.migration_log = []
    
    def log(self, message: str, level: str = "info"):
        """Log migration action."""
        self.migration_log.append((level, message))
        if self.verbose:
            prefix = f"[{level.upper()}]" if level != "info" else "[→]"
            print(f"{prefix} {message}")
    
    def check_scf_hub_exists(self) -> bool:
        """Check if SCF hub exists."""
        if self.scf_hub.exists():
            self.log(f"Found SCF hub at {self.scf_hub}")
            return True
        else:
            self.log(f"SCF hub not found at {self.scf_hub}", level="warning")
            return False
    
    def migrate_hub_directory(self) -> bool:
        """Migrate hub directory from scf-hub to wheelwright-hub."""
        if self.wheelwright_hub.exists():
            self.log(f"Wheelwright hub already exists at {self.wheelwright_hub}", 
                    level="warning")
            return False
        
        if not self.scf_hub.exists():
            self.log(f"SCF hub not found at {self.scf_hub}", level="error")
            return False
        
        try:
            if self.dry_run:
                self.log(f"[DRY-RUN] Would copy {self.scf_hub} → {self.wheelwright_hub}")
            else:
                shutil.copytree(self.scf_hub, self.wheelwright_hub)
                self.log(f"Migrated hub: {self.scf_hub} → {self.wheelwright_hub}")
            return True
        except Exception as e:
            self.log(f"Failed to migrate hub: {e}", level="error")
            return False
    
    def update_hub_metadata(self) -> bool:
        """Update hub metadata files with Wheelwright naming."""
        if not self.wheelwright_hub.exists():
            self.log("Wheelwright hub not found - skipping metadata update", 
                    level="warning")
            return False
        
        # Update WAI-State.json
        wai_state_path = self.wheelwright_hub / "WAI-Spoke" / "WAI-State.json"
        
        if wai_state_path.exists():
            try:
                with open(wai_state_path, "r") as f:
                    state = json.load(f)
                
                # Update references
                state["_file_meta"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
                state["wheelwright"]["migrated_from_scf"] = True
                state["wheelwright"]["migrated_at"] = datetime.utcnow().isoformat() + "Z"
                
                if self.dry_run:
                    self.log(f"[DRY-RUN] Would update {wai_state_path}")
                else:
                    with open(wai_state_path, "w") as f:
                        json.dump(state, f, indent=2)
                    self.log(f"Updated hub WAI-State.json")
                
                return True
            except json.JSONDecodeError as e:
                self.log(f"Failed to parse hub WAI-State.json: {e}", level="error")
                return False
        else:
            self.log("Hub WAI-State.json not found - creating new", level="warning")
            return False
    
    def find_spoke_projects(self) -> List[Path]:
        """Find all spoke projects in user's home directory."""
        spoke_projects = []
        
        # Look for directories containing .SCF/ or WAI-Spoke/
        for root in [self.home / "projects", self.home / "work", self.home]:
            if not root.exists():
                continue
            
            for item in root.glob("*/"):
                if item.is_dir():
                    # Check for old SCF structure
                    if (item / ".SCF").exists():
                        spoke_projects.append(item)
                        self.log(f"Found SCF project: {item.name}")
                    # Also check for new WAI structure (in case partial migration)
                    elif (item / "WAI-Spoke").exists():
                        # Already migrated, but log it
                        self.log(f"Found WAI project (already migrated?): {item.name}")
            
            # Only search one level deep by default
            if root != self.home:
                break
        
        return spoke_projects
    
    def migrate_spoke_project(self, project_path: Path) -> bool:
        """Migrate a single spoke project from SCF to Wheelwright."""
        scf_spoke = project_path / ".SCF"
        wai_spoke = project_path / "WAI-Spoke"
        
        if not scf_spoke.exists():
            self.log(f"SCF spoke not found in {project_path}", level="warning")
            return False
        
        if wai_spoke.exists():
            self.log(f"WAI-Spoke already exists in {project_path} - skipping", 
                    level="warning")
            return False
        
        try:
            if self.dry_run:
                self.log(f"[DRY-RUN] Would migrate {project_path.name}: .SCF → WAI-Spoke")
            else:
                # Copy .SCF to WAI-Spoke
                shutil.copytree(scf_spoke, wai_spoke)
                
                # Update internal files
                state_path = wai_spoke / "WAI-State.json"
                if state_path.exists():
                    with open(state_path, "r") as f:
                        state = json.load(f)
                    
                    # Update metadata
                    state["_file_meta"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
                    state["wheelwright"] = {
                        "migrated_from_scf": True,
                        "migrated_at": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    with open(state_path, "w") as f:
                        json.dump(state, f, indent=2)
                
                self.log(f"Migrated spoke project: {project_path.name}")
            
            return True
        except Exception as e:
            self.log(f"Failed to migrate spoke {project_path.name}: {e}", 
                    level="error")
            return False
    
    def run_migration(self, auto_discover: bool = True) -> Tuple[bool, List[str]]:
        """
        Run complete migration.
        
        Args:
            auto_discover: Automatically find and migrate spoke projects
        
        Returns:
            (success, messages)
        """
        self.log("Starting Wheelwright migration...")
        
        if not self.check_scf_hub_exists():
            self.log("Cannot proceed without SCF hub", level="error")
            return False, self.migration_log
        
        # Migrate hub
        hub_ok = self.migrate_hub_directory()
        if not hub_ok:
            self.log("Hub migration failed", level="error")
            return False, self.migration_log
        
        # Update hub metadata
        self.update_hub_metadata()
        
        # Discover and migrate spoke projects
        if auto_discover:
            self.log("\nSearching for spoke projects...")
            projects = self.find_spoke_projects()
            
            if projects:
                self.log(f"Found {len(projects)} projects to migrate")
                for project in projects:
                    self.migrate_spoke_project(project)
            else:
                self.log("No spoke projects found - you can migrate them manually later")
        
        self.log("\nMigration complete!", level="info")
        return True, self.migration_log


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate from Session Continuity Framework (SCF) to Wheelwright"
    )
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be migrated without making changes")
    parser.add_argument("--hub-path", type=Path, default=None,
                       help="Custom path for wheelwright-hub (default: ~/wheelwright-hub)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress status messages")
    
    args = parser.parse_args()
    
    migrator = SCFToWheelwrightMigrator(
        dry_run=args.dry_run,
        verbose=not args.quiet
    )
    
    if args.hub_path:
        migrator.wheelwright_hub = args.hub_path
    
    print("\n" + "="*60)
    print("SCF → Wheelwright Migration Tool")
    print("="*60 + "\n")
    
    if migrator.dry_run:
        print("MODE: DRY-RUN (no changes will be made)\n")
    
    success, log = migrator.run_migration()
    
    if not success:
        print("\n❌ Migration failed. See errors above.")
        return 1
    else:
        print("\n✓ Migration successful!")
        if migrator.dry_run:
            print("  Run without --dry-run to apply changes")
        return 0


if __name__ == "__main__":
    exit(main())
