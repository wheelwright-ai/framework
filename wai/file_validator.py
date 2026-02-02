"""
File validator - detect cross-project file conflicts via spoke_id.

When operating on files in a spoke-project, validates that all files belong to
the same spoke_id. Warns or rejects operations involving mixed-spoke files.

This protects hub ecosystem integrity - prevents accidental merging or syncing
files from different projects.
"""

import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class FileValidator:
    """Validate files belong to same spoke_id."""
    
    def __init__(self, primary_spoke_id: Optional[str] = None):
        """
        Initialize validator.
        
        Args:
            primary_spoke_id: The expected spoke_id for this session's project
        """
        self.primary_spoke_id = primary_spoke_id
        self.detected_spoke_ids = {}  # path -> spoke_id mapping
    
    def extract_spoke_id_from_file(self, file_path: Path) -> Optional[str]:
        """
        Extract spoke_id from file content if present.
        
        Looks for spoke_id in:
        1. JSON files: .wheel.spoke_id
        2. Markdown files: spoke_id metadata comment
        3. JSONL files: spoke_id in first valid entry
        
        Args:
            file_path: Path to file to check
        
        Returns:
            spoke_id if found, None otherwise
        """
        if not file_path.exists():
            return None
        
        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                    return data.get("wheel", {}).get("spoke_id")
            
            elif file_path.suffix == ".jsonl":
                with open(file_path, "r") as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if "spoke_id" in entry:
                                return entry["spoke_id"]
                return None
            
            elif file_path.suffix in [".md", ".markdown"]:
                # Look for comment: <!-- spoke_id: xxxxx -->
                with open(file_path, "r") as f:
                    content = f.read()
                    match = re.search(r"<!--\s*spoke_id:\s*([0-9a-f]{12})\s*-->", content)
                    if match:
                        return match.group(1)
                return None
        
        except (json.JSONDecodeError, IOError):
            return None
    
    def validate_file_set(self, file_paths: List[Path], 
                         strict: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate that all files belong to same spoke_id.
        
        Args:
            file_paths: List of files to validate
            strict: If True, raise error on mismatch; if False, warn
        
        Returns:
            (is_valid, warning_message)
        """
        spoke_ids = {}
        
        for file_path in file_paths:
            spoke_id = self.extract_spoke_id_from_file(file_path)
            if spoke_id:
                spoke_ids[str(file_path)] = spoke_id
        
        # Check for multiple spoke_ids
        unique_ids = set(spoke_ids.values())
        
        if len(unique_ids) > 1:
            message = f"Cross-project file set detected:\n"
            for path, sid in spoke_ids.items():
                message += f"  {Path(path).name}: {sid}\n"
            
            if strict:
                raise ValueError(message)
            return False, message
        
        # Check if any spoke_id doesn't match primary
        if self.primary_spoke_id and unique_ids:
            mismatched = [s for s in unique_ids if s != self.primary_spoke_id]
            if mismatched:
                message = (f"File set contains different spoke_id: "
                          f"expected {self.primary_spoke_id}, "
                          f"found {mismatched[0]}")
                return False, message
        
        return True, None
    
    def inject_spoke_id(self, file_path: Path, spoke_id: str) -> bool:
        """
        Inject spoke_id into file (for template/generation).
        
        Args:
            file_path: Path to file
            spoke_id: spoke_id to inject
        
        Returns:
            True if successful
        """
        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                if "wheel" not in data:
                    data["wheel"] = {}
                data["wheel"]["spoke_id"] = spoke_id
                
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                return True
            
            elif file_path.suffix in [".md", ".markdown"]:
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Add if not present
                if "spoke_id:" not in content:
                    header = f"<!-- spoke_id: {spoke_id} -->\n\n"
                    content = header + content
                    with open(file_path, "w") as f:
                        f.write(content)
                return True
        
        except IOError:
            return False
        
        return False


def detect_cross_project_files(wai_state_path: Path, 
                              file_paths: List[Path]) -> Optional[str]:
    """
    Standalone function to detect cross-project files.
    
    Args:
        wai_state_path: Path to WAI-State.json in primary project
        file_paths: List of files to check
    
    Returns:
        Warning message if cross-project detected, None if all match
    """
    # Get primary spoke_id
    try:
        with open(wai_state_path, "r") as f:
            state = json.load(f)
            primary_spoke_id = state.get("wheel", {}).get("spoke_id")
    except (json.JSONDecodeError, IOError):
        return None
    
    if not primary_spoke_id:
        return None
    
    # Validate
    validator = FileValidator(primary_spoke_id)
    is_valid, message = validator.validate_file_set(file_paths, strict=False)
    
    return message if not is_valid else None


__all__ = [
    "FileValidator",
    "detect_cross_project_files",
]
