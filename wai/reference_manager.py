"""
Reference Manager - Handles teaching, tracking, and adoption of versioned files.

Manages the teaching workflow:
1. teach command populates /reference/ingest/ with new template versions
2. WAI-Point detects files and creates pending upgrade actions
3. Agent reviews, decides to adopt/update/reject
4. Closeout processes decisions and archives files
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class FileTeaching:
    """Represents a file being taught (in /reference/ingest/ or root)."""
    
    def __init__(self, file_path: Path, manifest_entry: Dict[str, Any]):
        self.file_path = file_path
        self.manifest_entry = manifest_entry  # Keep full entry for location
        self.name = manifest_entry.get('name')
        self.version = manifest_entry.get('version', {})
        self.commit_hash = self.version.get('commit_hash')
        self.status = self.version.get('status', 'stable')
        self.blocks = manifest_entry.get('blocks', [])
        self.blocked_by = manifest_entry.get('blocked_by', [])
        self.requirements = manifest_entry.get('requirements', [])
        self.deferred_lugs = manifest_entry.get('deferred_lugs', [])
        self.implementation_instructions = manifest_entry.get('implementation_instructions', '')
        self.location = manifest_entry.get('location', 'ingest')  # 'root' or 'ingest'
        
    @property
    def requires_action(self) -> bool:
        """Whether this file needs agent action (not fully available locally yet)."""
        return True  # All files in ingest need review
    
    @property
    def blocking_items(self) -> List[str]:
        """Items that must be adopted before this one."""
        return self.blocked_by
    
    @property
    def blocked_items(self) -> List[str]:
        """Items that can't be adopted until this one is."""
        return self.blocks


class TeachingManager:
    """Manages seed/ingest teaching/adoption workflow with hub signature verification."""
    
    def __init__(self, spoke_dir: Path):
        self.spoke_dir = spoke_dir
        self.wai_spoke = spoke_dir / 'WAI-Spoke'
        self.seed_dir = self.wai_spoke / 'seed'
        self.ingest_dir = self.seed_dir / 'ingest'
        self.archive_dir = self.seed_dir / 'archive'
        self.manifest_file = self.ingest_dir / 'manifest.json'
        self.manifest_sig_file = self.ingest_dir / 'manifest.json.sig'
        self.disposition_log = self.seed_dir / 'disposition-log.jsonl'
        
        # Ensure directories exist
        self.ingest_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def get_pending_teachings(self) -> List[FileTeaching]:
        """Get all files waiting to be reviewed in /reference/ingest/ or root."""
        teachings = []
        
        if not self.manifest_file.exists():
            return teachings
        
        try:
            manifest = json.loads(self.manifest_file.read_text(encoding='utf-8'))
            
            for entry in manifest.get('files_taught', []):
                # WAI-Point.json.teaching is in root, others in ingest
                location = entry.get('location', 'ingest')
                if location == 'root':
                    file_path = self.spoke_dir / f"{entry.get('name')}.teaching"
                else:
                    file_path = self.ingest_dir / f"{entry.get('name')}.teaching"
                
                teaching = FileTeaching(file_path, entry)
                teachings.append(teaching)
            
            # Sort by dependencies (blocked_by first)
            teachings.sort(key=lambda t: (len(t.blocked_by), t.name))
            
            return teachings
        except Exception:
            return teachings
    
    def create_manifest(self, files: List[Dict[str, Any]], teach_timestamp: str, hub_fingerprint: Optional[str] = None):
        """Create manifest for taught files with hub signature."""
        manifest = {
            'version': '1.0',
            'taught_at': teach_timestamp,
            'hub_fingerprint': hub_fingerprint or 'unknown',  # Trust marker
            'files_taught': files,
            'status': 'pending_review',
            'signature_required': bool(hub_fingerprint)
        }
        
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'
        self.manifest_file.write_text(manifest_json, encoding='utf-8')
        
        # If hub fingerprint provided, create signature
        if hub_fingerprint:
            sig = self._create_signature(manifest_json, hub_fingerprint)
            self.manifest_sig_file.write_text(sig, encoding='utf-8')
    
    def verify_manifest(self) -> bool:
        """Verify manifest signature matches hub fingerprint."""
        if not self.manifest_file.exists():
            return False
        
        try:
            manifest = json.loads(self.manifest_file.read_text())
            hub_fp = manifest.get('hub_fingerprint')
            requires_sig = manifest.get('signature_required', False)
            
            if not requires_sig:
                return True  # No signature required
            
            if not self.manifest_sig_file.exists():
                return False  # Signature required but missing
            
            manifest_json = self.manifest_file.read_text()
            sig_content = self.manifest_sig_file.read_text()
            
            # Verify signature matches
            expected_sig = self._create_signature(manifest_json, hub_fp)
            return sig_content == expected_sig
        except Exception:
            return False
    
    @staticmethod
    def _create_signature(content: str, hub_fingerprint: str) -> str:
        """Create HMAC signature of content using hub fingerprint as key."""
        sig = hmac.new(
            hub_fingerprint.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        return sig
    
    def record_disposition(self, file_name: str, decision: str, notes: str = ''):
        """Record what agent did with a taught file."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'file': file_name,
            'decision': decision,  # 'adopted', 'adapted', 'rejected', 'deferred'
            'notes': notes
        }
        
        with open(self.disposition_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def archive_file(self, file_name: str, decision: str, location: str = 'ingest'):
        """Move processed file to archive."""
        if location == 'root':
            src = self.spoke_dir / f"{file_name}.teaching"
        else:
            src = self.ingest_dir / f"{file_name}.teaching"
        
        dst = self.archive_dir / f"{file_name}.{decision}"
        
        if src.exists():
            src.rename(dst)
    
    def get_pending_count(self) -> int:
        """Count files awaiting adoption."""
        return len(self.get_pending_teachings())
    
    def clear_ingest(self):
        """Clear all pending teachings (after closeout processing)."""
        if self.manifest_file.exists():
            self.manifest_file.unlink()
        
        # Archive any remaining files
        for file_path in self.ingest_dir.glob('*'):
            if file_path.name != 'manifest.json' and file_path.name != 'manifest.json.sig':
                file_path.rename(self.archive_dir / f"{file_path.name}.unprocessed")


def extract_implementation_instructions(file_content: str) -> Optional[str]:
    """Extract the implementation instructions section from a file."""
    lines = file_content.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if '## Implementation Instructions' in line:
            start_idx = i
        elif start_idx is not None and line.startswith('## ') and 'Implementation Instructions' not in line:
            end_idx = i
            break
    
    if start_idx is not None:
        end_idx = end_idx or len(lines)
        return '\n'.join(lines[start_idx:end_idx])
    
    return None


def strip_implementation_instructions(file_content: str) -> str:
    """Remove implementation instructions section from file."""
    lines = file_content.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if '## Implementation Instructions' in line:
            start_idx = i
        elif start_idx is not None and line.startswith('## ') and 'Implementation Instructions' not in line:
            end_idx = i
            break
    
    if start_idx is not None:
        end_idx = end_idx or len(lines)
        result = lines[:start_idx] + lines[end_idx:]
        return '\n'.join(result).rstrip() + '\n'
    
    return file_content
