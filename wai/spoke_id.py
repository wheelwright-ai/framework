"""
Spoke ID management - unique wheel identification for cross-project integrity.

Each spoke (wheel project) gets a unique 12-character hex ID generated from:
1. Project name + creation timestamp (deterministic for reproducibility)
2. Can detect when files belong to different spoke projects
3. Enables hub to validate file origins and warn on cross-project conflicts

Usage:
    from wai.spoke_id import generate_spoke_id, get_spoke_id, validate_spoke_id
    
    # Generate new spoke_id for a wheel
    spoke_id = generate_spoke_id("My Project", "2026-02-01T12:00:00Z")
    
    # Validate spoke_id format
    if validate_spoke_id("a1b2c3d4e5f6"):
        print("Valid spoke_id")
    
    # Get spoke_id from WAI-State.json
    spoke_id = get_spoke_id("/path/to/project")
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def generate_spoke_id(project_name: str, creation_timestamp: Optional[str] = None) -> str:
    """
    Generate a deterministic 12-character hex spoke_id.
    
    Args:
        project_name: Name of the project/wheel
        creation_timestamp: ISO format timestamp (optional, uses now if not provided)
    
    Returns:
        12-character hex string (first 12 chars of SHA256 hash)
    
    Example:
        >>> spoke_id = generate_spoke_id("Wheelwright Framework", "2026-02-01T00:00:00Z")
        >>> len(spoke_id)
        12
        >>> all(c in '0123456789abcdef' for c in spoke_id)
        True
    """
    if not creation_timestamp:
        creation_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Create deterministic input: project_name + timestamp
    input_str = f"{project_name}:{creation_timestamp}"
    
    # Generate SHA256 hash and take first 12 chars
    hash_obj = hashlib.sha256(input_str.encode("utf-8"))
    spoke_id = hash_obj.hexdigest()[:12]
    
    return spoke_id


def validate_spoke_id(spoke_id: str) -> bool:
    """
    Validate spoke_id format (12-character hex string).
    
    Args:
        spoke_id: String to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(spoke_id, str):
        return False
    if len(spoke_id) != 12:
        return False
    return all(c in "0123456789abcdef" for c in spoke_id)


def get_spoke_id(project_path: str) -> Optional[str]:
    """
    Get spoke_id from WAI-State.json in a project.
    
    Args:
        project_path: Path to project root (where WAI-Spoke/ is located)
    
    Returns:
        spoke_id string if found, None if not initialized
    """
    wai_state_path = Path(project_path) / "WAI-Spoke" / "WAI-State.json"
    
    if not wai_state_path.exists():
        return None
    
    try:
        with open(wai_state_path, "r") as f:
            state = json.load(f)
            return state.get("wheel", {}).get("spoke_id")
    except (json.JSONDecodeError, IOError):
        return None


def set_spoke_id(project_path: str, spoke_id: str) -> bool:
    """
    Set spoke_id in WAI-State.json.
    
    Args:
        project_path: Path to project root
        spoke_id: The spoke_id to set
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If spoke_id format is invalid
    """
    if not validate_spoke_id(spoke_id):
        raise ValueError(f"Invalid spoke_id format: {spoke_id}")
    
    wai_state_path = Path(project_path) / "WAI-Spoke" / "WAI-State.json"
    
    if not wai_state_path.exists():
        return False
    
    try:
        with open(wai_state_path, "r") as f:
            state = json.load(f)
        
        if "wheel" not in state:
            state["wheel"] = {}
        
        state["wheel"]["spoke_id"] = spoke_id
        state["_file_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        with open(wai_state_path, "w") as f:
            json.dump(state, f, indent=2)
        
        return True
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error setting spoke_id: {e}")
        return False


class SpokeRegistry:
    """
    Registry of known spoke_ids for hub-level cross-project detection.
    
    Tracks:
    - spoke_id -> project metadata mapping
    - Enables detection when files belong to different spokes
    - Supports hub learning ecosystem (warn on mismatched files)
    """
    
    def __init__(self, hub_path: Optional[str] = None):
        """
        Initialize spoke registry.
        
        Args:
            hub_path: Path to wheelwright hub (optional)
        """
        self.hub_path = Path(hub_path) if hub_path else None
        self.registry = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from hub if available."""
        if not self.hub_path:
            return
        
        registry_path = self.hub_path / ".WAI-registry" / "spokes.json"
        if registry_path.exists():
            try:
                with open(registry_path, "r") as f:
                    self.registry = json.load(f)
            except json.JSONDecodeError:
                self.registry = {}
    
    def register(self, spoke_id: str, project_name: str, project_path: str):
        """Register a spoke in the hub."""
        if not validate_spoke_id(spoke_id):
            raise ValueError(f"Invalid spoke_id: {spoke_id}")
        
        self.registry[spoke_id] = {
            "name": project_name,
            "path": str(project_path),
            "registered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        self._save_registry()
    
    def get_project(self, spoke_id: str) -> Optional[dict]:
        """Get project metadata by spoke_id."""
        return self.registry.get(spoke_id)
    
    def detect_mismatch(self, file_spoke_ids: list) -> Optional[str]:
        """
        Detect if multiple different spoke_ids found in file set.
        
        Args:
            file_spoke_ids: List of spoke_ids from files being processed
        
        Returns:
            Warning message if mismatch detected, None if all match
        """
        unique_ids = set(s for s in file_spoke_ids if s)
        
        if len(unique_ids) > 1:
            projects = [self.registry.get(sid, {}).get("name", f"Unknown ({sid})") 
                       for sid in unique_ids]
            return f"Cross-project file set detected: {', '.join(projects)}"
        
        return None
    
    def _save_registry(self):
        """Save registry to hub."""
        if not self.hub_path:
            return
        
        registry_dir = self.hub_path / ".WAI-registry"
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        registry_path = registry_dir / "spokes.json"
        with open(registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)


__all__ = [
    "generate_spoke_id",
    "validate_spoke_id",
    "get_spoke_id",
    "set_spoke_id",
    "SpokeRegistry",
]
