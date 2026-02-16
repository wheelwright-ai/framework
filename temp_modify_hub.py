import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime

# Helper function to get correct indentation
def get_indent(line: str) -> str:
    return line[:len(line) - len(line.lstrip())]

def modify_hub_file_robustly(file_path: Path):
    original_lines = file_path.read_text().splitlines()
    modified_lines = []
    
    in_create_hub_structure = False
    in_extract_insight = False
    profile_data_modified = False # Flag to indicate hub-profile.json modification
    
    i = 0
    while i < len(original_lines):
        line = original_lines[i]
        
        # --- Modify _create_hub_structure ---
        if "def _create_hub_structure(self, hub_path: Path) -> None:" in line:
            in_create_hub_structure = True
            modified_lines.append(line)
            i += 1
            continue
        
        if in_create_hub_structure and "        # Copy hub-specific templates" in line and not profile_data_modified:
            # Found the start of the block to modify
            # Insert new hub-profile.json handling
            indent = get_indent(line)
            
            modified_lines.append(f"{indent}# Copy hub-specific templates (rearranged to handle hub-profile.json first)")
            modified_lines.append(f"{indent}# Handle hub-profile.json separately to add fingerprint")
            modified_lines.append(f"{indent}hub_profile_template = hub_templates / 'hub-profile.json'")
            modified_lines.append(f"{indent}hub_profile_path = hub_path / 'hub-profile.json'")
            modified_lines.append(f"{indent}if hub_profile_template.exists():")
            modified_lines.append(f"{indent}    shutil.copy2(hub_profile_template, hub_profile_path)")
            modified_lines.append(f"{indent}    try:")
            modified_lines.append(f"{indent}        profile_data = json.loads(hub_profile_path.read_text())")
            modified_lines.append(f"{indent}        if 'hub_config' not in profile_data:")
            modified_lines.append(f"{indent}            profile_data['hub_config'] = {}")
            modified_lines.append(f"{indent}        # Generate a unique fingerprint")
            modified_lines.append(f"{indent}        if not profile_data['hub_config'].get('fingerprint'):")
            modified_lines.append(f"{indent}            profile_data['hub_config']['fingerprint'] = str(uuid.uuid4())")
            modified_lines.append(f"{indent}        ")
            modified_lines.append(f"{indent}        profile_data['hub_config']['created_at'] = datetime.now().isoformat()")
            modified_lines.append(f"{indent}        profile_data['hub_config']['hub_path'] = str(hub_path)")
            modified_lines.append(f"")
            modified_lines.append(f"{indent}        hub_profile_path.write_text(json.dumps(profile_data, indent=2, ensure_ascii=False) + '\\n')")
            modified_lines.append(f"{indent}    except Exception as e:")
            modified_lines.append(f"{indent}        print_warning(f\"  Warning: Could not add fingerprint to hub-profile.json: {{e}}\")")
            modified_lines.append(f"")

            # Then re-insert the loop for other templates, skipping the original lines
            # I need to find the specific template names that follow this line, and copy them.
            # The current line is "        # Copy hub-specific templates"
            # The template names were in `for template_name in ['hub-registry.json', 'hub-security-policy.json', 'hub-learning-index.md']:`
            # This is complex with line-by-line. Easier to replace the whole block.
            
            # Skip past the original lines that were handled
            # Need to skip the whole original block for 'hub-registry.json' etc.
            # I will skip until "Create learning category files"
            while i < len(original_lines) and "        # Create learning category files" not in original_lines[i]:
                i += 1
            modified_lines.append(original_lines[i]) # Add the "Create learning category files" line back
            profile_data_modified = True
            i += 1
            continue

        # --- Add get_hub_fingerprint method ---
        if "def _extract_insight(self, content: str) -> Optional[str]:" in line:
            in_extract_insight = True
            modified_lines.append(line)
            i += 1
            continue
        
        if in_extract_insight and "        return None" in line:
            modified_lines.append(line) # Add the original 'return None' line
            # Insert the new method right after _extract_insight's return None
            class_indent = get_indent(original_lines[original_lines.index("class HubManager:")])

            fingerprint_method_lines = [
                "", # blank line before new method
                f"{class_indent}    def get_hub_fingerprint(self, hub_path: Path) -> Optional[str]:",
                f"{class_indent}        \"\"\"",
                f"{class_indent}        Retrieve the hub's fingerprint from hub-profile.json.",
                f"",
                f"{class_indent}        Args:",
                f"{class_indent}            hub_path: Path to the hub directory.",
                f"",
                f"{class_indent}        Returns:",
                f"{class_indent}            The hub fingerprint string, or None if not found.",
                f"{class_indent}        \"\"\"",
                f"{class_indent}        hub_profile_path = hub_path / 'hub-profile.json'",
                f"{class_indent}        if hub_profile_path.exists():",
                f"{class_indent}            try:",
                f"{class_indent}                profile_data = json.loads(hub_profile_path.read_text())",
                f"{class_indent}                return profile_data.get('hub_config', {}).get('fingerprint')",
                f"{class_indent}            except Exception:",
                f"{class_indent}                pass",
                f"{class_indent}        return None",
                "" # blank line after new method
            ]
            modified_lines.extend(fingerprint_method_lines)
            in_extract_insight = False
            i += 1
            continue # Continue to next line of original file

        modified_lines.append(line)
        i += 1

    file_path.write_text("\n".join(modified_lines))
    print("Successfully modified wai/hub.py")

# Execute the modification
hub_file = Path("wai/hub.py")
modify_hub_file_robustly(hub_file)
'