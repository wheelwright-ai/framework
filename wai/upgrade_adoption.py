"""
Upgrade Adoption Plan - Verified knowledge distribution

Creates signed, versioned upgrade-adoption-plan.json with:
- Hub fingerprint (security)
- File hashes (integrity)
- Context fields (AI-friendly)
- Version info (relevance)
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class UpgradeAdoptionPlanBuilder:
    """Builder for upgrade-adoption-plan.json."""

    def __init__(
        self,
        framework_version: str,
        spoke_structure_version: str,
        source: str = "framework"
    ):
        """Initialize upgrade plan builder."""
        self.framework_version = framework_version
        self.spoke_structure_version = spoke_structure_version
        self.source = source
        self.files: List[Dict[str, Any]] = []
        self.hub_files: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow().replace(tzinfo=None).isoformat() + "Z"

    def add_file(
        self,
        name: str,
        path: str,
        source_path: str,
        version: str = "3.0.0",
        changed_from: str = "2.0.0",
        why_changed: str = "",
        breaking_changes: bool = False,
        safe_to_auto_adopt: bool = True,
        requires_review: bool = False,
        merge_strategy: Optional[str] = None,
        sections_to_preserve: Optional[List[str]] = None,
        sections_to_update: Optional[List[str]] = None,
        mentions: Optional[List[str]] = None,
        applies_to: Optional[List[str]] = None
    ) -> None:
        """Add spoke template file to upgrade plan."""
        
        # Read file and compute hash
        source = Path(source_path)
        if not source.exists():
            return
        
        content = source.read_text(encoding='utf-8')
        file_hash = self._compute_hash(content)
        file_size = len(content.encode('utf-8'))
        
        # Build file entry
        file_entry = {
            "name": name,
            "path": path,
            "size": file_size,
            "hash": file_hash,
            "source_path": str(source_path),
            "version": version,
            "changed_from": changed_from,
            "why_changed": why_changed,
            "breaking_changes": breaking_changes,
            "safe_to_auto_adopt": safe_to_auto_adopt,
            "requires_review": requires_review,
            "mentions": mentions or [],
            "applies_to": applies_to or ["spoke"],
            "status": "ready" if safe_to_auto_adopt else "review_needed",
            "action": "adopt" if safe_to_auto_adopt else "review"
        }
        
        # Add merge strategy if provided
        if merge_strategy:
            file_entry["merge_strategy"] = merge_strategy
        if sections_to_preserve:
            file_entry["sections_to_preserve"] = sections_to_preserve
        if sections_to_update:
            file_entry["sections_to_update"] = sections_to_update
        
        self.files.append(file_entry)

    def add_hub_file(
        self,
        name: str,
        path: str,
        source_path: str,
        version: str = "3.0.0",
        changed_from: str = "2.0.0",
        why_changed: str = "",
        breaking_changes: bool = False,
        safe_to_auto_adopt: bool = True,
        requires_review: bool = False,
        mentions: Optional[List[str]] = None
    ) -> None:
        """Add hub-specific template file to upgrade plan."""
        
        # Read file and compute hash
        source = Path(source_path)
        if not source.exists():
            return
        
        content = source.read_text(encoding='utf-8')
        file_hash = self._compute_hash(content)
        file_size = len(content.encode('utf-8'))
        
        # Build hub file entry
        file_entry = {
            "name": name,
            "path": path,
            "size": file_size,
            "hash": file_hash,
            "source_path": str(source_path),
            "version": version,
            "changed_from": changed_from,
            "why_changed": why_changed,
            "breaking_changes": breaking_changes,
            "safe_to_auto_adopt": safe_to_auto_adopt,
            "requires_review": requires_review,
            "mentions": mentions or [],
            "applies_to": ["hub"],
            "status": "ready" if safe_to_auto_adopt else "review_needed",
            "action": "adopt" if safe_to_auto_adopt else "review"
        }
        
        self.hub_files.append(file_entry)

    def build(self, hub_fingerprint: Optional[str] = None) -> Dict[str, Any]:
        """Build the upgrade adoption plan."""
        
        plan = {
            "metadata": {
                "version": self.framework_version,
                "framework_version": self.framework_version,
                "spoke_structure_version": self.spoke_structure_version,
                "created_at": self.created_at,
                "source": self.source,
                "target_type": "universal",
                "description": "Framework templates for universal distribution to hubs and spokes"
            },
            "verification": {
                "hub_fingerprint": hub_fingerprint,
                "spoke_signature": None,
                "hash_algorithm": "sha256-hmac",
                "signed_by": f"wheelwright-framework-{self.framework_version}",
                "verification_required": True
            },
            "files": self.files,
            "hub_files": self.hub_files if self.hub_files else [],
            "checksums": {
                "all_files_hash": self._compute_manifest_hash(),
                "verification_required": True
            }
        }
        
        # Add adoption guidance
        plan["adoption_guidance"] = self._build_adoption_guidance()
        
        return plan

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        return f"sha256:{hash_obj.hexdigest()}"

    def _compute_manifest_hash(self) -> str:
        """Compute hash of entire file manifest."""
        manifest_json = json.dumps(
            {"files": self.files, "hub_files": self.hub_files},
            sort_keys=True
        )
        hash_obj = hashlib.sha256(manifest_json.encode('utf-8'))
        return f"sha256:{hash_obj.hexdigest()}"

    def _build_adoption_guidance(self) -> Dict[str, Any]:
        """Build adoption guidance for spoke and hub."""
        
        spoke_files = [f for f in self.files if "spoke" in f["applies_to"]]
        hub_files = [f for f in self.hub_files if "hub" in f["applies_to"]]
        
        guidance = {
            "for_spoke": {
                "recommended_order": [],
                "post_adoption": "Run: WAI sync to process updated structure"
            }
        }
        
        # Build recommended adoption order for spoke
        for file in spoke_files:
            if file["safe_to_auto_adopt"]:
                guidance["for_spoke"]["recommended_order"].append(
                    f"{file['name']} (adopt immediately - {file['why_changed']})"
                )
        
        for file in spoke_files:
            if not file["safe_to_auto_adopt"]:
                guidance["for_spoke"]["recommended_order"].append(
                    f"{file['name']} (review merge strategy)"
                )
        
        # Hub guidance
        if hub_files:
            guidance["for_hub"] = {
                "recommended_order": [],
                "post_adoption": "Run: WAI hub status to verify"
            }
            
            for file in hub_files:
                if file["safe_to_auto_adopt"]:
                    guidance["for_hub"]["recommended_order"].append(
                        f"{file['name']} (adopt immediately)"
                    )
        
        return guidance


def sign_upgrade_plan(
    plan: Dict[str, Any],
    hub_key: str
) -> Dict[str, Any]:
    """Sign upgrade plan with hub fingerprint."""
    
    # Create signature of plan content
    plan_json = json.dumps(plan["files"] + plan.get("hub_files", []), sort_keys=True)
    signature = hmac.new(
        hub_key.encode('utf-8'),
        plan_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Update plan with signature
    plan["verification"]["hub_fingerprint"] = signature
    plan["verification"]["signed_by"] = f"wheelwright-framework-{plan['metadata']['framework_version']}"
    
    return plan


def verify_file_hash(content: str, expected_hash: str) -> bool:
    """Verify file content matches expected hash."""
    
    actual_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    expected_value = expected_hash.replace("sha256:", "")
    
    return actual_hash == expected_value


def verify_hub_signature(
    plan: Dict[str, Any],
    hub_key: str
) -> bool:
    """Verify hub signature on upgrade plan."""
    
    if not plan["verification"].get("hub_fingerprint"):
        return False
    
    # Reconstruct signature
    plan_json = json.dumps(plan["files"] + plan.get("hub_files", []), sort_keys=True)
    expected_sig = hmac.new(
        hub_key.encode('utf-8'),
        plan_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare with stored signature
    stored_sig = plan["verification"]["hub_fingerprint"]
    return hmac.compare_digest(expected_sig, stored_sig)


def load_upgrade_plan(plan_path: Path) -> Optional[Dict[str, Any]]:
    """Load upgrade adoption plan from file."""
    
    if not plan_path.exists():
        return None
    
    try:
        return json.loads(plan_path.read_text(encoding='utf-8'))
    except Exception:
        return None


def save_upgrade_plan(
    plan: Dict[str, Any],
    plan_path: Path
) -> bool:
    """Save upgrade adoption plan to file."""
    
    try:
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
            encoding='utf-8'
        )
        return True
    except Exception:
        return False


def get_adoptable_files(
    plan: Dict[str, Any],
    target_type: str = "spoke"
) -> Tuple[List[Dict], List[Dict]]:
    """
    Get files to adopt for target type.
    
    Returns:
        Tuple of (ready_to_adopt, needs_review)
    """
    
    # Select files based on target type
    if target_type == "hub":
        files = plan.get("hub_files", [])
    else:
        files = plan.get("files", [])
    
    # Filter by applies_to
    applicable = [
        f for f in files 
        if target_type in f.get("applies_to", [])
    ]
    
    # Split into ready and review
    ready = [f for f in applicable if f.get("safe_to_auto_adopt", False)]
    review = [f for f in applicable if not f.get("safe_to_auto_adopt", False)]
    
    return ready, review
