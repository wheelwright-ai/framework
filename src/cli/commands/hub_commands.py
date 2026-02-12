# src/cli/commands/hub_commands.py
# Contains commands related to the WAI Hub.

import os # New import
import json # New import
from cli import hub_manager # Import hub_manager

def confirm_action(action_description, artifacts_info=""):
    """Prompts user for confirmation before executing a state-changing action."""
    print(f"\n--- Confirmation Required ---")
    print(f"Action: {action_description}")
    if artifacts_info:
        print(f"This may affect: {artifacts_info}")
    confirm = input("Type 'yes' to confirm, or anything else to cancel: ").strip().lower()
    return confirm in ["y", "yes"]

def initialize_hub():
    action_desc = "Initialize a new WAI Hub."
    # artifacts_info = "Creates a new hub directory structure and configuration files." # Removed as confirmation removed
    # if confirm_action(action_desc, artifacts_info): # Removed confirmation
    hub_path = hub_manager.verify_hub_exists() # Get the current hub path
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    print(f"Executing: {action_desc}")
    
    # Define hub structure relative to hub_path
    hub_dot_wai_path = os.path.join(hub_path, ".WAI")
    hub_learnings_path = os.path.join(hub_path, "learnings")
    hub_sessions_path = os.path.join(hub_path, "sessions")
    
    # Create directories
    os.makedirs(hub_dot_wai_path, exist_ok=True)
    os.makedirs(hub_learnings_path, exist_ok=True)
    os.makedirs(hub_sessions_path, exist_ok=True)
    
    # Create placeholder files (simplified for now)
    hub_profile_path = os.path.join(hub_path, "hub-profile.json")
    hub_registry_path = os.path.join(hub_path, "hub-registry.json")
    
    if not os.path.exists(hub_profile_path):
        hub_name = input("Enter a name for your new WAI Hub (e.g., 'My Personal Hub'): ").strip()
        if not hub_name:
            hub_name = "My WAI Hub" # Default name
        with open(hub_profile_path, 'w') as f:
            json.dump({"hub_name": hub_name, "created_at": hub_manager.datetime.utcnow().isoformat(timespec='seconds') + 'Z'}, f, indent=2)
    
    if not os.path.exists(hub_registry_path):
        with open(hub_registry_path, 'w') as f:
            json.dump({"registered_spokes": []}, f, indent=2)

    print(f"Hub initialized successfully at {hub_path}!")
    # else: # Removed confirmation
    #     print("Action cancelled.") # Removed confirmation

def teach_hub():
    action_desc = "First, runs Learn to analyze spokes, then processes generated Lugs for teaching."
    
    print(f"\nExecuting: {action_desc}")
    
    # Step 1: Run Learn to analyze spokes and generate Lugs
    print("\n--- Running Learn as part of Teach process ---")
    learn_hub() # Call learn_hub to generate Lugs

    hub_path = hub_manager.verify_hub_exists()
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return
    
    learnings_dir = os.path.join(hub_path, "learnings")

    if not os.path.exists(learnings_dir) or not os.listdir(learnings_dir):
        print("No learning records (Lugs) found after running Learn. Nothing to Teach.")
        return

    # Step 2: Simulate processing the generated Lugs (for Teaching)
    processed_lugs_count = 0
    print("\n--- Processing Lugs for Teaching ---")
    
    learning_files = [f for f in os.listdir(learnings_dir) if f.startswith("lug_") and f.endswith(".json")]

    for lug_filename in learning_files:
        lug_path = os.path.join(learnings_dir, lug_filename)
        try:
            with open(lug_path, 'r') as f:
                lug_content = json.load(f)
            
            # Simulate teaching process (e.g., feeding to another AI, updating a knowledge graph)
            print(f" - Taught system about Lug: '{lug_content.get('t', 'Untitled Lug')}' (ID: {lug_content.get('i', 'N/A')})")
            processed_lugs_count += 1
            
            # Optionally, move processed lugs to a 'taught' sub-directory or mark as processed
            # For now, we'll just leave them, or delete them if they should be transient.
            # os.remove(lug_path) # If lugs should be consumed and deleted
            
        except Exception as e:
            print(f"Error processing Lug '{lug_filename}': {e}")
            
    print(f"\nCompleted teaching process. Processed {processed_lugs_count} Lugs.")
def _generate_lug_id(title, timestamp):
    import hashlib
    return hashlib.sha256(f"{title}-{timestamp}".encode()).hexdigest()[:12]

def learn_hub():
    action_desc = "Analyze registered Spokes and generate high-impact learning Lugs."
    
    hub_path = hub_manager.verify_hub_exists()
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    print(f"\nExecuting: {action_desc}")

    hub_registry_path = os.path.join(hub_path, "hub-registry.json")
    if not os.path.exists(hub_registry_path):
        print(f"Error: Hub registry not found at {hub_registry_path}. No spokes to learn from.")
        return

    learnings_dir = os.path.join(hub_path, "learnings")
    os.makedirs(learnings_dir, exist_ok=True) # Ensure learnings directory exists

    try:
        with open(hub_registry_path, 'r') as f:
            hub_registry = json.load(f)
        registered_spokes = hub_registry.get("registered_spokes", [])
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in hub registry at {hub_registry_path}.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading hub registry: {e}")
        return

    if not registered_spokes:
        print("No spokes currently registered to learn from.")
        return

    generated_lugs_count = 0
    print("\n--- Learning from Spokes ---")
    for spoke in registered_spokes:
        spoke_name = spoke.get('name', 'Unknown')
        spoke_path = spoke.get('path')
        spoke_version = spoke.get('version', 'N/A')

        if not spoke_path or not os.path.isdir(spoke_path):
            print(f"Skipping '{spoke_name}': Invalid or non-existent path: {spoke_path}")
            continue

        print(f"\nAnalyzing Spoke: '{spoke_name}' (v{spoke_version}) at {spoke_path}")

        # Common project indicators
        has_git = os.path.isdir(os.path.join(spoke_path, ".git"))
        has_package_json = os.path.exists(os.path.join(spoke_path, "package.json"))
        has_requirements_txt = os.path.exists(os.path.join(spoke_path, "requirements.txt"))
        has_terraform = os.path.isdir(os.path.join(spoke_path, ".terraform")) or \
                        any(f.endswith(".tf") for f in os.listdir(spoke_path) if os.path.isfile(os.path.join(spoke_path, f)))
        has_wai_spoke = os.path.exists(os.path.join(spoke_path, "WAI-Spoke", "WAI-State.json"))

        timestamp = hub_manager.datetime.utcnow().isoformat(timespec='seconds') + 'Z'

        # Generate Lugs based on findings
        # Lug: Project Discovered
        lug_title = f"Discovered Project: {spoke_name}"
        lug_desc = f"CLI discovered and analyzed project '{spoke_name}' at '{spoke_path}'."
        lug_content = {
            "i": _generate_lug_id(lug_title, timestamp),
            "t": lug_title,
            "ty": "signal",
            "s": "open",
            "status": "open",
            "description": lug_desc,
            "priority": "medium",
            "impact": 8,
            "value": 7,
            "scope": "project",
            "tags": ["discovery", "project"],
            "created_at": timestamp,
            "blocks": [], "blocked_by": []
        }
        lug_filename = f"lug_{lug_content['i']}.json"
        with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
            json.dump(lug_content, f, indent=2)
        print(f" - Generated Lug: '{lug_title}' (Impact: 8)")
        generated_lugs_count += 1

        if has_wai_spoke:
            lug_title = f"Discovered WAI-Spoke structure in: {spoke_name}"
            lug_desc = f"Project '{spoke_name}' contains a WAI-Spoke structure, indicating it's a Wheelwright-managed project."
            lug_content = {
                "i": _generate_lug_id(lug_title, timestamp),
                "t": lug_title,
                "ty": "signal",
                "s": "open",
                "status": "open",
                "description": lug_desc,
                "priority": "high",
                "impact": 9,
                "value": 9,
                "scope": "project",
                "tags": ["discovery", "wai-spoke", "architecture"],
                "created_at": timestamp,
                "blocks": [], "blocked_by": []
            }
            lug_filename = f"lug_{lug_content['i']}.json"
            with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
                json.dump(lug_content, f, indent=2)
            print(f" - Generated Lug: '{lug_title}' (Impact: 9)")
            generated_lugs_count += 1
        
        if has_git:
            lug_title = f"Discovered Git Repository in: {spoke_name}"
            lug_desc = f"Project '{spoke_name}' is a Git repository."
            lug_content = {
                "i": _generate_lug_id(lug_title, timestamp),
                "t": lug_title,
                "ty": "signal",
                "s": "open",
                "status": "open",
                "description": lug_desc,
                "priority": "medium",
                "impact": 8,
                "value": 5,
                "scope": "project",
                "tags": ["discovery", "git"],
                "created_at": timestamp,
                "blocks": [], "blocked_by": []
            }
            lug_filename = f"lug_{lug_content['i']}.json"
            with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
                json.dump(lug_content, f, indent=2)
            print(f" - Generated Lug: '{lug_title}' (Impact: 8)")
            generated_lugs_count += 1

        if has_terraform:
            lug_title = f"Discovered Terraform Project in: {spoke_name}"
            lug_desc = f"Project '{spoke_name}' contains Terraform configurations."
            lug_content = {
                "i": _generate_lug_id(lug_title, timestamp),
                "t": lug_title,
                "ty": "signal",
                "s": "open",
                "status": "open",
                "description": lug_desc,
                "priority": "high",
                "impact": 9,
                "value": 8,
                "scope": "project",
                "tags": ["discovery", "terraform", "iac"],
                "created_at": timestamp,
                "blocks": [], "blocked_by": []
            }
            lug_filename = f"lug_{lug_content['i']}.json"
            with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
                json.dump(lug_content, f, indent=2)
            print(f" - Generated Lug: '{lug_title}' (Impact: 9)")
            generated_lugs_count += 1
        
        if has_package_json:
            lug_title = f"Discovered Node.js Project in: {spoke_name}"
            lug_desc = f"Project '{spoke_name}' contains a package.json, indicating a Node.js project."
            lug_content = {
                "i": _generate_lug_id(lug_title, timestamp),
                "t": lug_title,
                "ty": "signal",
                "s": "open",
                "status": "open",
                "description": lug_desc,
                "priority": "medium",
                "impact": 7,
                "value": 6,
                "scope": "project",
                "tags": ["discovery", "nodejs", "javascript"],
                "created_at": timestamp,
                "blocks": [], "blocked_by": []
            }
            lug_filename = f"lug_{lug_content['i']}.json"
            with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
                json.dump(lug_content, f, indent=2)
            print(f" - Generated Lug: '{lug_title}' (Impact: 7)")
            generated_lugs_count += 1

        if has_requirements_txt:
            lug_title = f"Discovered Python Project in: {spoke_name}"
            lug_desc = f"Project '{spoke_name}' contains a requirements.txt, indicating a Python project."
            lug_content = {
                "i": _generate_lug_id(lug_title, timestamp),
                "t": lug_title,
                "ty": "signal",
                "s": "open",
                "status": "open",
                "description": lug_desc,
                "priority": "medium",
                "impact": 7,
                "value": 6,
                "scope": "project",
                "tags": ["discovery", "python"],
                "created_at": timestamp,
                "blocks": [], "blocked_by": []
            }
            lug_filename = f"lug_{lug_content['i']}.json"
            with open(os.path.join(learnings_dir, lug_filename), 'w') as f:
                json.dump(lug_content, f, indent=2)
            print(f" - Generated Lug: '{lug_title}' (Impact: 7)")
            generated_lugs_count += 1
            
    print(f"\nCompleted learning from spokes. Generated {generated_lugs_count} new Lugs.")

def get_hub_version():
    action_desc = "Display the version of the connected WAI Hub."
    hub_path = hub_manager.verify_hub_exists() # Get the current hub path
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    print(f"\nExecuting: {action_desc}")
    
    hub_profile_path = os.path.join(hub_path, "hub-profile.json")
    if not os.path.exists(hub_profile_path):
        print(f"Error: Hub profile not found at {hub_profile_path}.")
        return

    try:
        with open(hub_profile_path, 'r') as f:
            hub_profile = json.load(f)
            hub_version = hub_profile.get("version", "1.0.0") # Default to 1.0.0 if not in profile
            print(f"WAI Hub Version: {hub_version}")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in hub profile at {hub_profile_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")