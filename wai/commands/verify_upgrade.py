"""
Verify Upgrade Command - Spoke-side verification of upgrade adoption plans.

Process:
1. Load upgrade-adoption-plan.json from spoke root
2. Verify hub signature using HMAC-SHA256
3. Verify file hashes for integrity
4. Show adoption guidance with context
5. Prompt for adoption decisions
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from ..upgrade_adoption import (
    load_upgrade_plan,
    verify_hub_signature,
    verify_file_hash,
    get_adoptable_files
)
from ..utils.input import (
    print_info, print_success, print_error, print_warning
)
from ..reference_manager import TeachingManager


def _load_plan_file(spoke_path: Path) -> Optional[Dict[str, Any]]:
    """Load upgrade-adoption-plan.json from spoke."""
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    return load_upgrade_plan(plan_path)


def _verify_plan_integrity(plan: Dict[str, Any], teach_manager: TeachingManager) -> Tuple[bool, List[str]]:
    """
    Verify all file hashes in plan against actual files in ingest directory.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check all spoke files
    for file_entry in plan.get('files', []):
        ingest_file = teach_manager.ingest_dir / f"{file_entry['name']}.teaching"
        
        if not ingest_file.exists():
            errors.append(f"Missing file: {file_entry['name']} (not in /seed/ingest/)")
            continue
        
        try:
            content = ingest_file.read_text(encoding='utf-8')
            if not verify_file_hash(content, file_entry['hash']):
                errors.append(f"Hash mismatch: {file_entry['name']} (content corrupted or modified)")
        except Exception as e:
            errors.append(f"Cannot verify {file_entry['name']}: {e}")
    
    # Check all hub files (even if spoke, plan includes them)
    for file_entry in plan.get('hub_files', []):
        ingest_file = teach_manager.ingest_dir / f"{file_entry['name']}.teaching"
        
        if not ingest_file.exists():
            errors.append(f"Missing hub file: {file_entry['name']} (not in /seed/ingest/)")
            continue
        
        try:
            content = ingest_file.read_text(encoding='utf-8')
            if not verify_file_hash(content, file_entry['hash']):
                errors.append(f"Hash mismatch: {file_entry['name']} (content corrupted or modified)")
        except Exception as e:
            errors.append(f"Cannot verify {file_entry['name']}: {e}")
    
    return len(errors) == 0, errors


def _show_adoption_summary(plan: Dict[str, Any]) -> None:
    """Display upgrade plan summary to agent."""
    metadata = plan.get('metadata', {})
    
    print_info("\n  ════════════════════════════════════════════════════")
    print_info(f"  UPGRADE ADOPTION PLAN v{metadata.get('framework_version', 'unknown')}")
    print_info("  ════════════════════════════════════════════════════")
    
    # Framework and version info
    print_info(f"\n  Framework Version: {metadata.get('framework_version')}")
    print_info(f"  Created: {metadata.get('created_at')}")
    print_info(f"  Source: {metadata.get('source')}")
    
    # Verification status
    verification = plan.get('verification', {})
    print_info(f"\n  Security:")
    if verification.get('hub_fingerprint'):
        print_success(f"    ✓ Signed by {verification.get('signed_by')}")
    else:
        print_warning(f"    ⚠ No hub signature (unsigned plan)")
    
    # Files summary
    files = plan.get('files', [])
    hub_files = plan.get('hub_files', [])
    
    ready_to_adopt = [f for f in files if f.get('safe_to_auto_adopt')]
    needs_review = [f for f in files if not f.get('safe_to_auto_adopt')]
    
    print_info(f"\n  Files:")
    print_info(f"    Spoke files: {len(files)}")
    if ready_to_adopt:
        print_success(f"      - Ready to adopt: {len(ready_to_adopt)}")
    if needs_review:
        print_warning(f"      - Need review: {len(needs_review)}")
    
    if hub_files:
        print_info(f"    Hub files: {len(hub_files)}")


def _show_adoption_guidance(plan: Dict[str, Any]) -> None:
    """Show detailed adoption guidance for each file."""
    files = plan.get('files', [])
    
    print_info(f"\n  ADOPTION GUIDANCE")
    print_info("  " + "─" * 48)
    
    # Show ready-to-adopt files
    ready = [f for f in files if f.get('safe_to_auto_adopt')]
    if ready:
        print_info("\n  Ready to Adopt Immediately:")
        for f in ready:
            print_success(f"    ✓ {f['name']}")
            print_info(f"      Changed from: {f.get('changed_from')} → {f.get('version')}")
            print_info(f"      Why: {f.get('why_changed', 'N/A')}")
            if f.get('mentions'):
                print_info(f"      Affects: {', '.join(f['mentions'])}")
    
    # Show files needing review
    review = [f for f in files if not f.get('safe_to_auto_adopt')]
    if review:
        print_info("\n  Requires Review:")
        for f in review:
            print_warning(f"    ⚠ {f['name']}")
            print_info(f"      Changed from: {f.get('changed_from')} → {f.get('version')}")
            print_info(f"      Why: {f.get('why_changed', 'N/A')}")
            print_info(f"      Action: {f.get('action', 'review').upper()}")
            
            # Show merge strategy if present
            if f.get('merge_strategy'):
                print_info(f"      Merge strategy: {f['merge_strategy']}")
                if f.get('sections_to_preserve'):
                    print_info(f"        Preserve: {', '.join(f['sections_to_preserve'])}")
                if f.get('sections_to_update'):
                    print_info(f"        Update: {', '.join(f['sections_to_update'])}")


def verify_upgrade_command(spoke_path: Path, hub_key: Optional[str] = None) -> bool:
    """
    Verify upgrade adoption plan on spoke.
    
    Args:
        spoke_path: Path to project (spoke root)
        hub_key: Optional hub key for signature verification
    
    Returns:
        True if plan verified successfully
    """
    teach_manager = TeachingManager(spoke_path)
    
    # 1. Load plan
    print_info("\n  Loading upgrade plan...")
    plan = _load_plan_file(spoke_path)
    
    if not plan:
        print_error("  No upgrade-adoption-plan.json found in spoke root")
        return False
    
    print_success("  ✓ Plan loaded")
    
    # 2. Verify hub signature if key provided
    verification_ok = True
    if hub_key:
        print_info("  Verifying hub signature...")
        if verify_hub_signature(plan, hub_key):
            print_success("  ✓ Hub signature valid")
        else:
            print_error("  ✗ Hub signature INVALID (plan may be tampered)")
            verification_ok = False
    else:
        print_warning("  ⚠ No hub key provided (signature verification skipped)")
        print_info("    Plan will be adopted but without cryptographic verification")
    
    # 3. Verify file hashes
    print_info("  Verifying file integrity...")
    hashes_ok, hash_errors = _verify_plan_integrity(plan, teach_manager)
    
    if hashes_ok:
        print_success(f"  ✓ All file hashes verified")
    else:
        print_error(f"  ✗ Hash verification failed:")
        for error in hash_errors:
            print_error(f"      {error}")
        verification_ok = False
    
    # 4. Show summary and guidance
    _show_adoption_summary(plan)
    _show_adoption_guidance(plan)
    
    # 5. Report overall status
    print_info(f"\n  ════════════════════════════════════════════════════")
    if verification_ok:
        print_success("  ✓ PLAN VERIFIED - Ready for adoption")
    else:
        print_warning("  ⚠ VERIFICATION ISSUES - Review before adoption")
    
    print_info(f"  ════════════════════════════════════════════════════\n")
    
    return verification_ok


def get_adoption_decisions(plan: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Get adoption decisions from agent.
    
    Returns:
        Dict with 'adopt', 'review', 'defer' keys and file names
    """
    decisions = {
        'adopt': [],
        'review': [],
        'defer': []
    }
    
    files = plan.get('files', [])
    
    for file_entry in files:
        file_name = file_entry['name']
        
        if file_entry.get('safe_to_auto_adopt'):
            # Auto-adopt safe files
            decisions['adopt'].append(file_name)
        elif file_entry.get('requires_review'):
            # Files needing review (AI should decide)
            decisions['review'].append(file_name)
        else:
            # Defer others
            decisions['defer'].append(file_name)
    
    return decisions


def execute_adoptions(
    spoke_path: Path,
    plan: Dict[str, Any],
    decisions: Dict[str, List[str]]
) -> bool:
    """
    Execute file adoptions based on decisions.
    
    Args:
        spoke_path: Path to spoke root
        plan: Upgrade adoption plan
        decisions: Adoption decisions from agent
    
    Returns:
        True if all adoptions completed
    """
    teach_manager = TeachingManager(spoke_path)
    success_count = 0
    error_count = 0
    
    print_info("\n  EXECUTING ADOPTIONS")
    print_info("  " + "─" * 48)
    
    # Get file entries for reference
    file_map = {f['name']: f for f in plan.get('files', [])}
    file_map.update({f['name']: f for f in plan.get('hub_files', [])})
    
    # Execute adopt decisions
    for file_name in decisions.get('adopt', []):
        file_entry = file_map.get(file_name)
        if not file_entry:
            continue
        
        try:
            # Read from ingest
            ingest_file = teach_manager.ingest_dir / f"{file_name}.teaching"
            if not ingest_file.exists():
                print_warning(f"  Skipping {file_name}: not in ingest")
                error_count += 1
                continue
            
            content = ingest_file.read_text(encoding='utf-8')
            
            # Determine target path with traversal protection
            target_path = spoke_path / file_entry.get('path', file_name)
            try:
                target_path.resolve().relative_to(spoke_path.resolve())
            except ValueError:
                print_error(f"  ✗ Path traversal detected: {file_entry.get('path', file_name)}")
                error_count += 1
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to final location
            target_path.write_text(content, encoding='utf-8')
            
            print_success(f"  ✓ Adopted {file_name}")
            success_count += 1
            
        except Exception as e:
            print_error(f"  ✗ Failed to adopt {file_name}: {e}")
            error_count += 1
    
    # Handle review files (for now, just show they were deferred)
    for file_name in decisions.get('review', []):
        print_warning(f"  ⟳ Deferred review of {file_name}")
    
    # Handle deferred files
    for file_name in decisions.get('defer', []):
        print_info(f"  ○ Skipped {file_name}")
    
    print_info(f"\n  Adoptions: {success_count} completed, {error_count} failed")
    
    return error_count == 0
