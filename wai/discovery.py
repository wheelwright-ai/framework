"""
Spoke auto-discovery scanner - find all wheel projects in a hub.

Scans directory tree for WAI-Spoke/ directories, extracts project metadata,
assigns spoke_ids if missing, and builds hub registry.

Usage:
    from wai.discovery import SpokeDiscovery
    
    discovery = SpokeDiscovery("/path/to/hub")
    spokes = discovery.scan()
    registry = discovery.build_registry()
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

from .spoke_id import generate_spoke_id, validate_spoke_id, set_spoke_id


class SpokeDiscovery:
    """Discover and catalog spoke projects in a hub."""
    
    def __init__(self, hub_path: str, verbose: bool = True):
        """
        Initialize discovery scanner.
        
        Args:
            hub_path: Path to wheelwright hub
            verbose: Print status messages
        """
        self.hub_path = Path(hub_path).resolve()
        self.verbose = verbose
        self.discovered_spokes = {}  # spoke_id -> metadata
        self.spokes_missing_id = []  # Projects missing spoke_id
        self.orphaned_spokes = []  # WAI-Spoke without hub entry
    
    def log(self, message: str, level: str = "info"):
        """Log discovery action."""
        if self.verbose:
            prefix = "→" if level == "info" else f"[{level.upper()}]"
            print(f"{prefix} {message}")
    
    def scan(self, max_depth: int = 10) -> Dict[str, dict]:
        """
        Recursively scan hub for WAI-Spoke/ directories.
        
        Args:
            max_depth: Maximum directory depth to scan
        
        Returns:
            Dictionary of {project_path: metadata}
        """
        self.log(f"Scanning hub: {self.hub_path}")
        
        found_projects = {}
        
        for root, dirs, files in os.walk(self.hub_path, topdown=True):
            # Limit depth
            depth = len(Path(root).relative_to(self.hub_path).parts)
            if depth > max_depth:
                dirs.clear()
                continue
            
            # Skip .git, .WAI-registry, etc.
            dirs[:] = [d for d in dirs if not d.startswith(('.git', '.', '__pycache__'))]
            
            # Check if this directory has WAI-Spoke
            project_path = Path(root)
            wai_spoke = project_path / "WAI-Spoke"
            
            if wai_spoke.is_dir():
                # Found a spoke project
                project_name = project_path.name
                metadata = self._extract_metadata(project_path, wai_spoke)
                found_projects[str(project_path)] = metadata
                
                self.log(f"Found project: {project_name}")
        
        self.log(f"Discovered {len(found_projects)} project(s)")
        return found_projects
    
    def _extract_metadata(self, project_path: Path, wai_spoke_path: Path) -> dict:
        """Extract metadata from a spoke project."""
        wai_state = wai_spoke_path / "WAI-State.json"
        
        metadata = {
            "path": str(project_path),
            "name": project_path.name,
            "spoke_id": None,
            "version": None,
            "status": "unknown",
            "has_state": False,
        }
        
        if wai_state.exists():
            try:
                with open(wai_state, "r") as f:
                    state = json.load(f)
                
                metadata["has_state"] = True
                metadata["spoke_id"] = state.get("wheel", {}).get("spoke_id")
                metadata["version"] = state.get("wheel", {}).get("version")
                metadata["status"] = state.get("wheel", {}).get("status", "unknown")
                metadata["wheel_name"] = state.get("wheel", {}).get("name")
                
                if not metadata["spoke_id"]:
                    self.spokes_missing_id.append(metadata)
            
            except json.JSONDecodeError as e:
                self.log(f"Error reading {wai_state}: {e}", level="warning")
        
        return metadata
    
    def assign_missing_ids(self) -> Tuple[int, List[str]]:
        """
        Assign spoke_ids to projects that are missing them.
        
        Uses deterministic generation based on project name and current time.
        
        Returns:
            (count_assigned, list_of_assigned_ids)
        """
        if not self.spokes_missing_id:
            self.log("All projects have spoke_ids")
            return 0, []
        
        assigned = []
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        for metadata in self.spokes_missing_id:
            project_path = Path(metadata["path"])
            project_name = metadata["name"]
            
            # Generate deterministic spoke_id
            spoke_id = generate_spoke_id(project_name, timestamp)
            
            # Assign to WAI-State.json
            success = set_spoke_id(str(project_path), spoke_id)
            
            if success:
                self.log(f"Assigned spoke_id to {project_name}: {spoke_id}")
                metadata["spoke_id"] = spoke_id
                assigned.append(spoke_id)
            else:
                self.log(f"Failed to assign spoke_id to {project_name}", level="warning")
        
        self.spokes_missing_id = []
        return len(assigned), assigned
    
    def build_registry(self) -> Dict[str, dict]:
        """
        Build spoke registry from discovered projects.
        
        Returns:
            Registry of {spoke_id: project_metadata}
        """
        registry = {}
        
        for project_path, metadata in self.discovered_spokes.items():
            spoke_id = metadata.get("spoke_id")
            
            if spoke_id:
                if validate_spoke_id(spoke_id):
                    registry[spoke_id] = {
                        "name": metadata.get("name"),
                        "path": metadata.get("path"),
                        "version": metadata.get("version"),
                        "status": metadata.get("status"),
                        "discovered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    }
                else:
                    self.log(f"Invalid spoke_id for {metadata.get('name')}: {spoke_id}", 
                            level="warning")
        
        self.log(f"Built registry with {len(registry)} spoke(s)")
        return registry
    
    def save_registry(self, registry: Dict[str, dict]) -> bool:
        """
        Save registry to hub's .WAI-registry/spokes.json.
        
        Args:
            registry: Registry to save
        
        Returns:
            True if successful
        """
        registry_dir = self.hub_path / ".WAI-registry"
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        registry_path = registry_dir / "spokes.json"
        
        try:
            with open(registry_path, "w") as f:
                json.dump(registry, f, indent=2)
            
            self.log(f"Saved registry to {registry_path}")
            return True
        except IOError as e:
            self.log(f"Failed to save registry: {e}", level="error")
            return False
    
    def discover_and_register(self) -> Tuple[int, int, int]:
        """
        Complete discovery workflow: scan, assign IDs, build & save registry.
        
        Returns:
            (total_found, assigned_ids, registry_entries)
        """
        # Step 1: Scan
        self.discovered_spokes = self.scan()
        total = len(self.discovered_spokes)
        
        # Step 2: Assign missing IDs
        assigned, _ = self.assign_missing_ids()
        
        # Step 3: Build registry
        registry = self.build_registry()
        
        # Step 4: Save registry
        self.save_registry(registry)
        
        return total, assigned, len(registry)
    
    def get_report(self) -> str:
        """Generate discovery report."""
        lines = [
            "\n=== Spoke Discovery Report ===\n",
            f"Hub path: {self.hub_path}",
            f"Spokes discovered: {len(self.discovered_spokes)}",
            f"Missing spoke_ids: {len(self.spokes_missing_id)}",
            f"Orphaned spokes: {len(self.orphaned_spokes)}",
        ]
        
        if self.discovered_spokes:
            lines.append("\nDiscovered projects:")
            for path, metadata in self.discovered_spokes.items():
                spoke_id = metadata.get("spoke_id", "MISSING")
                status = metadata.get("status", "unknown")
                lines.append(f"  • {metadata['name']} ({spoke_id}) [{status}]")
                lines.append(f"    Path: {path}")
        
        return "\n".join(lines)


def discover_hub_spokes(hub_path: str, verbose: bool = True) -> Tuple[int, Dict[str, dict]]:
    """
    Standalone function to discover and register all spokes in a hub.
    
    Args:
        hub_path: Path to hub
        verbose: Print status
    
    Returns:
        (total_spokes, registry)
    """
    discovery = SpokeDiscovery(hub_path, verbose=verbose)
    total, assigned, registry_count = discovery.discover_and_register()
    
    if assigned > 0:
        print(f"✓ Assigned {assigned} spoke_id(s)")
    
    registry = discovery.build_registry()
    return total, registry


__all__ = [
    "SpokeDiscovery",
    "discover_hub_spokes",
]
