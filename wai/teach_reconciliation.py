from typing import Dict, Any, List
from pathlib import Path
import json
import shutil
from datetime import datetime, timezone
from wai.hub import HubManager # For Hub fingerprint verification
# from ..utils.input import print_info, print_success, print_error, print_warning # Implicitly used by print() in dummy functions

# Constants for ingest and processed directories - these should ideally be in a config file
TEACH_INGEST_DIR = "WAI-Spoke/seed/ingest"
TEACH_PROCESSED_DIR = "WAI-Spoke/seed/ingest/processed" # Teachings moved here after adoption


def scan_teach_ingest_dir(ingest_path: Path) -> List[Dict[str, Any]]:
    """
    Scans the specified ingest directory for .teaching files and their manifest.json.

    Args:
        ingest_path: The path to the directory containing .teaching files and manifest.json.

    Returns:
        A list of dictionaries, each representing a pending teaching with its metadata.
    """
    pending_teachings = []
    manifest_path = ingest_path / "manifest.json"

    if not ingest_path.is_dir():
        return pending_teachings

    manifest = {}
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {manifest_path}. Skipping manifest.")

    for teach_file in ingest_path.glob("*.teaching"):
        teaching_id = teach_file.stem
        # Check manifest for status
        manifest_entry = manifest.get(teaching_id, {})
        status = manifest_entry.get("status", "pending_adoption") # Default status

        if status == "pending_adoption":
            # Attempt to read the teaching file content if it's JSON
            content = None
            try:
                with open(teach_file, "r") as f:
                    content = f.read()
                    # Try to parse as JSON, otherwise treat as plain text
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        pass # Keep as string if not JSON
            except Exception as e:
                print(f"Warning: Could not read teaching file {teach_file}: {e}")
                continue

            pending_teachings.append({
                "id": teaching_id,
                "file_path": str(teach_file),
                "status": status,
                "metadata": manifest_entry, # Include any metadata from manifest
                "content_preview": str(content)[:200] + "..." if isinstance(content, str) and len(str(content)) > 200 else content
            })

    return pending_teachings


def brief_pending_teachings(pending_teachings: List[Dict[str, Any]]) -> str:
    """
    Formats a markdown string summarizing pending teachings for the briefing.

    Args:
        pending_teachings: A list of dictionaries, each representing a pending teaching.

    Returns:
        A markdown-formatted string.
    """
    if not pending_teachings:
        return ""

    lines = [
        "## 📚 Pending Teachings (Action Required)",
        ""
    ]
    lines.append("New knowledge and updates are available for adoption. Please review and decide.")
    lines.append("")

    for i, teaching in enumerate(pending_teachings, 1):
        lines.append(f"{i}. **{teaching.get('id', 'Unknown Teaching')}**")
        lines.append(f"   - Status: `{teaching.get('status', 'pending')}`")
        if teaching.get("metadata", {}).get("description"):
            lines.append(f"   - Description: {teaching['metadata']['description']}")
        lines.append(f"   - File: `{teaching['file_path']}`")
        lines.append(f"   - **Action**: To adopt, run: `wai teach adopt {teaching.get('id')}` (or refer to manifest for details)")
        lines.append("") # Ensure a blank line after each teaching for readability

    lines.append("---")
    lines.append("") # Ensure a blank line after separator
    return "\n".join(lines)


def perform_teaching_adoption(spoke_path: Path, teaching: Dict[str, Any]) -> bool:
    """
    Performs the adoption of a single teaching file.

    Args:
        spoke_path: The root path of the spoke project.
        teaching: A dictionary containing teaching details (id, file_path, metadata).

    Returns:
        True if adoption was successful or completed with warnings, False if failed.
    """
    warnings: List[str] = [] # Initialize warnings list only once at the beginning
    
    try: # Wrap the entire function logic in a try-except block for comprehensive error handling
        teach_file_path = Path(teaching['file_path'])
        manifest_path = teach_file_path.parent / "manifest.json" # Manifest is in the same folder as .teaching files

        # --- Fingerprint Verification Logic ---
        spoke_root_path = spoke_path # Alias for clarity
        
        spoke_wai_state_path = spoke_root_path / "WAI-Spoke" / "WAI-State.json"
        spoke_config_hub_fingerprint = None

        if spoke_wai_state_path.exists():
            try:
                spoke_state_data = json.loads(spoke_wai_state_path.read_text())
                # Assuming the Hub path is stored in _hub_profile within WAI-State.json
                spoke_hub_path_str = spoke_state_data.get('_hub_profile', {}).get('hub_config', {}).get('hub_path')
                if spoke_hub_path_str:
                    spoke_hub_path = Path(spoke_hub_path_str)
                    # HubManager needs to be available in the scope (assumed to be imported at top level)
                    hub_manager = HubManager() 
                    spoke_config_hub_fingerprint = hub_manager.get_hub_fingerprint(spoke_hub_path)
            except Exception as e:
                warnings.append(f"  [WARNING] Could not retrieve configured hub fingerprint from Spoke's WAI-State.json: {e}")
                
    # Extract fingerprint from the teaching plan if it's an upgrade plan
    plan_hub_fingerprint = teaching['metadata'].get('verification', {}).get('hub_fingerprint')
    
    # Perform verification
    if spoke_config_hub_fingerprint: # Spoke is configured to verify
        if plan_hub_fingerprint: # Plan is signed
            if spoke_config_hub_fingerprint != plan_hub_fingerprint:
                warnings.append(f"  [ERROR] Teaching plan fingerprint mismatch. Configured Hub: '{spoke_config_hub_fingerprint}', Plan signed by: '{plan_hub_fingerprint}'. Refusing adoption.")
                return False # Refuse adoption due to critical error
        else: # Spoke configured, but plan is NOT signed
            warnings.append(f"  [ERROR] Spoke configured with Hub fingerprint '{spoke_config_hub_fingerprint}', but teaching plan is not signed. Refusing adoption.")
            return False # Refuse adoption due to critical error
    elif plan_hub_fingerprint: # Spoke NOT configured, but plan IS signed
        warnings.append(f"  [WARNING] Spoke is not configured with a Hub fingerprint, but teaching plan is signed by '{plan_hub_fingerprint}'. Proceeding with caution.")
    # --- End Fingerprint Verification Logic ---
    
    # Determine target path
    target_rel_path = teaching['metadata'].get('path') # Use path from manifest if provided
    if not target_rel_path:
        # Default to placing in spoke_path / teaching_filename without .teaching extension
        target_name = teach_file_path.name.replace(".teaching", "")
        # Heuristic: if name matches a known core WAI file, place it in WAI-Spoke/
        # Otherwise, place it in reference/auto/
        if target_name in ["WAI-AI-ONBOARDING.md", "WAI-Guide.md", "WAI-State.md", "WAI-State.json", "WAI-Lugs.jsonl"]:
            target_path = spoke_path / "WAI-Spoke" / target_name
        else:
            target_path = spoke_path / "WAI-Spoke" / "reference" / "auto" / target_name
    else:
        target_path = spoke_path / target_rel_path
        
    target_path.parent.mkdir(parents=True, exist_ok=True) # Ensure target directory exists

    safe_to_auto_adopt = teaching['metadata'].get('safe_to_auto_adopt', False)
    merge_strategy = teaching['metadata'].get('merge_strategy', 'overwrite')
    
    try: # Wrap the entire function logic in a try-except block for comprehensive error handling
        if safe_to_auto_adopt:
            if merge_strategy == 'overwrite':
                shutil.copy2(teach_file_path, target_path)
            elif merge_strategy == 'merge_sections':
                if target_path.exists():
                    try:
                        current_content = json.loads(target_path.read_text())
                        new_content = json.loads(teach_file_path.read_text())
                        
                        sections_to_preserve = teaching['metadata'].get('sections_to_preserve', [])
                        sections_to_update = teaching['metadata'].get('sections_to_update', [])
                        
                        working_content = current_content.copy()

                        for key, value in new_content.items():
                            if key not in sections_to_preserve:
                                working_content[key] = value
                        
                        for section in sections_to_update:
                            if section not in new_content and section in working_content:
                                del working_content[section]

                        target_path.write_text(json.dumps(working_content, indent=2) + "\n")

                    except json.JSONDecodeError as jde:
                        warnings.append(f"  [ERROR] JSON decode error during merge for {teach_file_path.name} -> {target_path.name}: {jde}. Refusing adoption.")
                        return False # Fatal error during merge, refuse adoption
                    except Exception as exc:
                        warnings.append(f"  [ERROR] Unexpected error during merge_sections for {teach_file_path.name}: {exc}. Refusing adoption.\nDetails: {exc}")
                        return False # Fatal error during merge, refuse adoption
                else: # Target doesn't exist, just copy
                    shutil.copy2(teach_file_path, target_path)
            else: # Default or unknown merge strategy
                shutil.copy2(teach_file_path, target_path)
            
            teach_file_path.unlink() # Delete the teaching file after adoption

            if manifest_path.exists():
                with open(manifest_path, "r+") as f:
                    manifest = json.load(f)
                    manifest_entry = manifest.get(teaching['id'], {})
                    manifest_entry['status'] = 'adopted'
                    manifest_entry['adopted_at'] = datetime.now(timezone.utc).isoformat()
                    manifest[teaching['id']] = manifest_entry # Ensure updated entry is stored back
                    f.seek(0)
                    json.dump(manifest, f, indent=2)
                    f.truncate()
            
            # After auto-adoption, check for any [ERROR] in warnings
            if any("[ERROR]" in w for w in warnings):
                return False
            return True

        else: # requires review (safe_to_auto_adopt is False)
            warnings.append(f"  [INFO] Teaching '{teaching['id']}' requires manual review. Not auto-adopting.")
            warnings.append(f"  Please review '{teach_file_path.relative_to(spoke_path)}' and merge manually into '{target_path.relative_to(spoke_path)}'.")
            return False # Always return False if requires review
            
    except Exception as e:
        warnings.append(f"  [ERROR] Unhandled exception during teaching adoption for '{teaching.get('id', 'unknown')}': {e}")
        return False # Any unhandled exception makes adoption fail


def cleanup_ingest_directory(ingest_path: Path) -> List[str]:
    """
    Cleans up adopted .teaching files from the ingest directory.
    This also updates the manifest.json to remove adopted entries or mark them as cleaned.

    Args:
        ingest_path: The path to the WAI-Spoke/seed/ingest directory.

    Returns:
        A list of filenames that were cleaned up.
    """
    cleaned_files = []
    manifest_path = ingest_path / "manifest.json"

    if not ingest_path.is_dir():
        return cleaned_files

    # This check ensures that the manifest.json is handled only if it exists
    # and if there are other files in the directory that might correspond to teachings.
    # Otherwise, an empty or manifest-only directory is considered clean enough.
    if manifest_path.is_file():
        # Optimization: if the directory is empty or only contains manifest.json, nothing to clean up.
        if not any(ingest_path.iterdir()):
            return cleaned_files
        if len(list(ingest_path.iterdir())) == 1 and manifest_path.exists():
            return cleaned_files
    else:
        # If manifest.json does not exist, but there are .teaching files, we should still clean them up.
        # But for now, we only process based on manifest.
        pass


    manifest = {}
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {manifest_path}. Skipping manifest cleanup.")

    for teach_file in ingest_path.glob("*.teaching"):
        teaching_id = teach_file.stem
        manifest_entry = manifest.get(teaching_id, {})
        
        # If adopted, remove the file
        if manifest_entry.get("status") == "adopted" or manifest_entry.get("status") == "cleaned":
            try:
                teach_file.unlink()
                cleaned_files.append(teach_file.name)
                # Update manifest entry
                manifest[teaching_id]["status"] = "cleaned"
                manifest[teaching_id]["cleaned_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            except Exception as e:
                print(f"Warning: Could not delete adopted teaching file {teach_file.name}: {e}")
        # If it's a teaching file but not in manifest, or status is pending, leave it for now
        # Manual review files should also stay until explicitly handled.

    # Update manifest.json
    if manifest_path.is_file():
        try:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not update manifest.json during cleanup: {e}")

    return cleaned_files


if __name__ == '__main__':
    # Example usage for testing purposes
    # Create a dummy ingest directory and a .teaching file
    test_spoke_path = Path("./test_spoke")
    test_spoke_path.mkdir(exist_ok=True)
    (test_spoke_path / "WAI-Spoke").mkdir(exist_ok=True)
    ingest_dir = test_spoke_path / "WAI-Spoke" / "seed" / "ingest"
    ingest_dir.mkdir(parents=True, exist_ok=True)

    # Dummy manifest.json
    dummy_manifest_content = {
        "wai-ai-onboarding": {
            "path": "WAI-Spoke/WAI-AI-ONBOARDING.md",
            "safe_to_auto_adopt": True,
            "description": "Consolidated AI onboarding guide."
        },
        "wai-state-update": {
            "path": "WAI-Spoke/WAI-State.json",
            "safe_to_auto_adopt": True, # Changed to true for testing merge
            "merge_strategy": "merge_sections",
            "sections_to_preserve": ["_session_state", "_project_foundation", "decisions", "analytics"],
            "sections_to_update": ["wheelwright.structure_version", "wheelwright.version", "_file_meta"],
            "description": "Updates to WAI-State.json schema."
        },
        "manual-review": {
            "path": "WAI-Spoke/some-config.json",
            "safe_to_auto_adopt": False,
            "description": "A teaching that requires manual review."
        }
    }
    (ingest_dir / "manifest.json").write_text(json.dumps(dummy_manifest_content, indent=2))

    # Dummy .teaching file 1 (auto-adopt)
    (ingest_dir / "wai-ai-onboarding.teaching").write_text("# WAI AI Onboarding Guide (Updated)")

    # Dummy .teaching file 2 (auto-adopt, JSON merge)
    (ingest_dir / "wai-state-update.teaching").write_text(json.dumps({
        "wheelwright": {"version": "4.0.0", "structure_version": "4.0", "_file_meta": {"new_key": "value"}},
        "_session_state": {"some_session_data": "to_be_overwritten"}
    }, indent=2))
    # Create a dummy WAI-State.json to merge into
    (test_spoke_path / "WAI-Spoke" / "WAI-State.json").write_text(json.dumps({
        "wheelwright": {"version": "3.1.0", "structure_version": "3.1", "_file_meta": {"old_key": "value"}},
        "_session_state": {"some_session_data": "preserved_value"},
        "decisions": ["old_decision"]
    }, indent=2))

    # Dummy .teaching file 3 (manual review)
    (ingest_dir / "manual-review.teaching").write_text("{'config_key': 'new_value'}")

    print("--- Scanning pending teachings ---")
    teachings = scan_teach_ingest_dir(ingest_dir)
    if teachings:
        print(brief_pending_teachings(teachings))
        print("\n--- Performing adoption ---")
        for teaching in teachings:
            result = perform_teaching_adoption(test_spoke_path, teaching)
            if result is True:
                print(f"  Adopted '{teaching['id']}' successfully.")
            elif result is False:
                print(f"  Failed to adopt '{teaching['id']}'.")
            else: # Warnings
                print(f"  Adopted '{teaching['id']}' with warnings/manual review needed: {result}")
    else:
        print("No pending teachings found.")

    # Clean up dummy files
    shutil.rmtree(test_spoke_path)
    print("\n--- Cleaned up test_spoke directory ---")