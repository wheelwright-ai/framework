"""
Teach Command - Distribute updated template files to spokes.

Process:
1. Copy latest template files to spoke's /reference/ingest/
2. Include version info and implementation instructions
3. Create manifest of taught files
4. Agent reviews and adopts during closeout
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..reference_manager import TeachingManager
from ..utils.input import print_info, print_success, print_error, print_warning


def teach_command(spoke_path: Path, hub_path: Optional[Path], framework_path: Path) -> bool:
    """
    Teach a spoke with updated templates from framework.
    
    Args:
        spoke_path: Path to project to teach
        hub_path: Path to hub (optional, for knowledge distribution)
        framework_path: Path to framework (source of templates)
    
    Returns:
        True if teaching completed
    """
    teach_manager = TeachingManager(spoke_path)
    templates_dir = framework_path / 'templates' / 'WAI'
    
    if not templates_dir.exists():
        print_error(f"  Framework templates not found at {templates_dir}")
        return False
    
    print_info("  Teaching Spoke with Latest Framework Templates...")
    
    # Template files to teach
    template_files = [
        'WAI-Guide.md',
        'WAI-State.json',
        'WAI-State.md',
        'WAI-Point.json',
        'WAI-KB-Sync.json',
    ]
    
    files_taught = []
    
    for template_name in template_files:
        src = templates_dir / template_name
        if not src.exists():
            continue
        
        # Read template
        try:
            content = src.read_text(encoding='utf-8')
        except Exception as e:
            print_warning(f"  Failed to read {template_name}: {e}")
            continue
        
        # Extract version info and implementation instructions
        version_info = _extract_version_info(content)
        impl_instructions = _extract_implementation_instructions(content)
        deferred_lugs = _extract_deferred_lugs(content)
        
        # WAI-Point.json goes in root (entry point)
        # Other files go in seed/ingest/
        if template_name == 'WAI-Point.json':
            dst = spoke_path / f"{template_name}.teaching"
            location = 'root'
        else:
            dst = teach_manager.ingest_dir / f"{template_name}.teaching"
            location = 'ingest'
        
        try:
            dst.write_text(content, encoding='utf-8', errors='replace')
            print_success(f"  [OK] {template_name} (v{version_info.get('commit_hash', 'unknown')[:8]}) -> {location}")
            
            files_taught.append({
                'name': template_name,
                'size': len(content),
                'version': version_info,
                'status': version_info.get('status', 'stable'),
                'blocks': [],
                'blocked_by': [],
                'requirements': [],
                'deferred_lugs': deferred_lugs,
                'implementation_instructions': bool(impl_instructions),
                'has_changes': True,
                'location': location  # 'root' or 'ingest'
            })
        except Exception as e:
            print_error(f"  Failed to teach {template_name}: {e}")
    
    if not files_taught:
        print_warning("  No templates to teach")
        return False
    
    # Create manifest with hub fingerprint for security
    try:
        # Get hub fingerprint if hub exists
        hub_fingerprint = None
        if hub_path and (hub_path / 'hub-profile.json').exists():
            try:
                import json
                profile = json.loads((hub_path / 'hub-profile.json').read_text())
                hub_fingerprint = profile.get('fingerprint')  # Trust marker
            except Exception:
                pass
        
        teach_manager.create_manifest(files_taught, datetime.now().isoformat(), hub_fingerprint)
        print_success(f"\n  [OK] Taught {len(files_taught)} file(s)")
        print_info(f"    Agent will review in /seed/ingest/ on next session")
        if hub_fingerprint:
            print_info(f"    [OK] Signed with hub fingerprint (trusted)")
        return True
    except Exception as e:
        print_error(f"  Failed to create manifest: {e}")
        return False


def _extract_version_info(content: str) -> Dict[str, Any]:
    """Extract version info from file header."""
    lines = content.split('\n')
    version_info = {
        'commit_hash': 'unknown',
        'status': 'stable'
    }
    
    for line in lines[:20]:  # Check first 20 lines
        if '**Version:**' in line or 'version:' in line.lower():
            # Extract hash (first meaningful part after colon)
            parts = line.split('`')
            if len(parts) >= 2:
                version_info['commit_hash'] = parts[1].strip()
        elif '**Status:**' in line or 'status:' in line.lower():
            # Extract status (stable, beta, dev)
            for status in ['stable', 'beta', 'development', 'dev']:
                if status in line.lower():
                    version_info['status'] = status
                    break
    
    return version_info


def _extract_implementation_instructions(content: str) -> str:
    """Extract implementation instructions section."""
    lines = content.split('\n')
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
    
    return ''


def _extract_deferred_lugs(content: str) -> List[Dict[str, Any]]:
    """Extract deferred work (lug IDs) from implementation instructions."""
    impl = _extract_implementation_instructions(content)
    lugs = []
    
    # Look for lug references like: - [ ] Task A → lug-id-xxx
    lines = impl.split('\n')
    for line in lines:
        if '[DEFER]' in line or '->' in line:
            # Extract lug ID (should be after arrow or in parens)
            parts = line.split('[DEFER]') if '[DEFER]' in line else line.split('->')
            if len(parts) > 1:
                lug_id = parts[1].strip().split()[0]
                task_name = parts[0].split('-')[-1].strip() if '-' in parts[0] else 'Unknown'
                lugs.append({
                    'id': lug_id,
                    'task': task_name
                })
    
    return lugs
