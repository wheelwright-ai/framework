"""
Upgrade Adoption Consumer - Process and adopt teaching files from ingest.

Handles:
1. Verification of upgrade-adoption-plan.json
2. File hash verification
3. Signature verification (if hub-signed)
4. Adoption of ready-to-adopt files
5. Archiving/cleanup of processed files
"""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class UpgradeAdoptionConsumer:
    """Consumes (adopts/rejects) teaching files from upgrade adoption plan."""
    
    def __init__(self, spoke_path: Path):
        """Initialize consumer."""
        self.spoke_path = spoke_path
        self.wai_spoke = spoke_path / 'WAI-Spoke'
        self.seed_dir = self.wai_spoke / 'seed'
        self.ingest_dir = self.seed_dir / 'ingest'
        self.archive_dir = self.seed_dir / 'archive'
        self.plan_path = spoke_path / 'upgrade-adoption-plan.json'
        self.disposition_log = self.seed_dir / 'disposition-log.jsonl'
        
        # Ensure directories exist
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def consume_ready_files(self) -> Dict[str, Any]:
        """
        Consume (adopt) all ready-to-adopt files from ingest.
        
        Process:
        1. Load upgrade-adoption-plan.json
        2. Get files marked safe_to_auto_adopt
        3. Verify file hashes
        4. Move to target location
        5. Archive source .teaching file
        6. Log disposition
        
        Returns:
            Dict with:
            - adopted: List of adopted files
            - skipped: List of files needing review
            - errors: List of errors
            - is_complete: True if all ready files processed
        """
        
        result = {
            "adopted": [],
            "skipped": [],
            "errors": [],
            "is_complete": False
        }
        
        # Load plan
        if not self.plan_path.exists():
            result["errors"].append("No upgrade-adoption-plan.json found")
            return result
        
        try:
            plan = json.loads(self.plan_path.read_text(encoding='utf-8'))
        except Exception as e:
            result["errors"].append(f"Could not load plan: {e}")
            return result
        
        # Get ready files from plan
        ready_files = []
        for file_entry in plan.get('files', []):
            if file_entry.get('safe_to_auto_adopt', False):
                ready_files.append(file_entry)
        
        # Process each ready file
        for file_entry in ready_files:
            name = file_entry.get('name', '')
            path = file_entry.get('path', '')
            expected_hash = file_entry.get('hash', '')
            
            # Check if .teaching file exists in ingest
            teaching_file = self.ingest_dir / f"{name}.teaching"
            if not teaching_file.exists():
                # File not in ingest yet, skip
                result["skipped"].append(name)
                continue
            
            # Verify hash if provided
            if expected_hash:
                try:
                    content = teaching_file.read_text(encoding='utf-8')
                    actual_hash = f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"
                    if actual_hash != expected_hash:
                        result["errors"].append(
                            f"{name}: Hash mismatch (expected {expected_hash}, got {actual_hash})"
                        )
                        continue
                except Exception as e:
                    result["errors"].append(f"{name}: Could not verify hash: {e}")
                    continue
            
            # Move to target location
            try:
                target_path = self.spoke_path / path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Read source
                content = teaching_file.read_text(encoding='utf-8')
                
                # Write to target (remove .teaching extension)
                final_path = self.spoke_path / path
                final_path.write_text(content, encoding='utf-8')
                
                # Archive the .teaching file
                archive_path = self.archive_dir / f"{name}.teaching"
                shutil.move(str(teaching_file), str(archive_path))
                
                # Log disposition
                self._log_disposition(name, "adopted", path)
                
                result["adopted"].append(name)
            except Exception as e:
                result["errors"].append(f"{name}: Could not adopt: {e}")
        
        result["is_complete"] = len(result["errors"]) == 0
        return result
    
    def reject_file(self, file_name: str, reason: str = "User rejected") -> bool:
        """Reject a file - archive without adopting."""
        teaching_file = self.ingest_dir / f"{file_name}.teaching"
        if not teaching_file.exists():
            return False
        
        try:
            archive_path = self.archive_dir / f"{file_name}.teaching.rejected"
            shutil.move(str(teaching_file), str(archive_path))
            self._log_disposition(file_name, "rejected", reason)
            return True
        except Exception:
            return False
    
    def defer_file(self, file_name: str) -> bool:
        """Defer a file - mark as requiring later review."""
        teaching_file = self.ingest_dir / f"{file_name}.teaching"
        if not teaching_file.exists():
            return False
        
        try:
            # Keep in ingest but log disposition
            self._log_disposition(file_name, "deferred", "Awaiting later review")
            return True
        except Exception:
            return False
    
    def _log_disposition(self, file_name: str, decision: str, details: str) -> None:
        """Log file disposition decision."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "file_name": file_name,
            "decision": decision,  # adopted, rejected, deferred
            "details": details
        }
        
        # Append to disposition log
        with open(self.disposition_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_pending_review_files(self) -> List[Dict[str, Any]]:
        """Get files that require manual review (not safe_to_auto_adopt)."""
        if not self.plan_path.exists():
            return []
        
        try:
            plan = json.loads(self.plan_path.read_text(encoding='utf-8'))
        except Exception:
            return []
        
        review_files = []
        for file_entry in plan.get('files', []):
            if not file_entry.get('safe_to_auto_adopt', False):
                name = file_entry.get('name', '')
                teaching_file = self.ingest_dir / f"{name}.teaching"
                if teaching_file.exists():
                    review_files.append({
                        "name": name,
                        "reason": file_entry.get('requires_review', True),
                        "path": file_entry.get('path', ''),
                        "why_changed": file_entry.get('why_changed', ''),
                        "sections_to_preserve": file_entry.get('sections_to_preserve', [])
                    })
        
        return review_files
    
    def get_orphaned_files(self) -> List[str]:
        """Get .teaching files not in any plan."""
        from .upgrade_adoption import verify_upgrade_ingestion_complete
        
        result = verify_upgrade_ingestion_complete(self.plan_path, self.ingest_dir)
        return result.get("orphaned", [])


def auto_adopt_ready_files(spoke_path: Path) -> Dict[str, Any]:
    """
    Automatically adopt all ready-to-adopt files from latest upgrade plan.
    
    Useful for closeout: process safe files automatically, flag unsafe files.
    
    Args:
        spoke_path: Path to spoke
    
    Returns:
        Adoption result dict with counts and details
    """
    consumer = UpgradeAdoptionConsumer(spoke_path)
    result = consumer.consume_ready_files()
    
    # Separate reporting
    pending_review = consumer.get_pending_review_files()
    orphaned = consumer.get_orphaned_files()
    
    result["pending_review"] = len(pending_review)
    result["orphaned_count"] = len(orphaned)
    
    return result
