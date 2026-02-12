# src/cli/hub_manager.py
# Manages the WAI Hub connection, verification, and initiation.

import json
import os
import sys
from datetime import datetime # New import

# Assuming WAI-Spoke/WAI-State.json is at the project root relative to where CLI is run
# This needs to be resolved based on actual project structure
# For now, let's assume WAI-Spoke is one level up from cli/src (or where main.py is)
# or that the framework root is the current working directory.
WAI_STATE_PATH = "/home/mario/projects/wheelwright-ai/framework/WAI-Spoke/WAI-State.json" # Absolute path

def _get_wai_state():
    """Reads and returns the content of WAI-State.json."""
    if os.path.exists(WAI_STATE_PATH):
        try:
            with open(WAI_STATE_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON in {WAI_STATE_PATH}.")
            sys.exit(1)
    return {}

def _update_wai_state(state):
    """Writes the content back to WAI-State.json."""
    with open(WAI_STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def verify_hub_exists():
    """
    Verifies if a hub path is defined in WAI-State.json.
    Returns the hub path if found, otherwise None.
    """
    state = _get_wai_state()
    hub_path = state.get("wheel", {}).get("hub_path")
    if hub_path and os.path.isdir(hub_path):
        return hub_path
    return None

def prompt_for_hub_path():
    """Asks the user to provide the path to their WAI Hub."""
    print("\n--- WAI Hub Not Found ---")
    print("A WAI Hub is essential for context persistence and project management.")
    return input("Please enter the full path to your WAI Hub, or type 'init' to create one: ").strip()

def offer_to_initiate_hub():
    """Offers the user to create a new WAI Hub."""
    print("\n--- WAI Hub Creation ---")
    print("You can create a new WAI Hub. This will set up a new directory for your hub data.")
    confirm = input("Would you like to initiate a new WAI Hub? (yes/no): ").strip().lower()
    return confirm == 'yes'

def initiate_hub(path):
    """
    Creates a new WAI Hub at the given path.
    Persists the hub_path to WAI-State.json.
    """
    print(f"\n--- Initiating WAI Hub at: {path} (Placeholder) ---")
    # Simulate hub creation
    os.makedirs(path, exist_ok=True)
    
    # Define hub structure relative to path
    hub_dot_wai_path = os.path.join(path, ".WAI")
    hub_learnings_path = os.path.join(path, "learnings")
    hub_sessions_path = os.path.join(path, "sessions")
    
    # Create directories
    os.makedirs(hub_dot_wai_path, exist_ok=True)
    os.makedirs(hub_learnings_path, exist_ok=True)
    os.makedirs(hub_sessions_path, exist_ok=True)
    
    # Create placeholder files
    hub_profile_path = os.path.join(path, "hub-profile.json")
    hub_registry_path = os.path.join(path, "hub-registry.json")
    
    if not os.path.exists(hub_profile_path):
        with open(hub_profile_path, 'w') as f:
            json.dump({"hub_name": "My WAI Hub", "created_at": datetime.utcnow().isoformat(timespec='seconds') + 'Z'}, f, indent=2)
    
    if not os.path.exists(hub_registry_path):
        with open(hub_registry_path, 'w') as f:
            json.dump({"registered_spokes": []}, f, indent=2)

    # Persist the hub_path to WAI-State.json
    state = _get_wai_state()
    state.setdefault("wheel", {})["hub_path"] = path
    _update_wai_state(state)
    
    print(f"WAI Hub initiated successfully at {path} (Placeholder)")
    return True