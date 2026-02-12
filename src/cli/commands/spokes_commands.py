import json # New import
import os # New import
from cli import hub_manager # Import hub_manager

def confirm_action(action_description, artifacts_info=""):
    """Prompts user for confirmation before executing a state-changing action."""
    print(f"\n--- Confirmation Required ---")
    print(f"Action: {action_description}")
    if artifacts_info:
        print(f"This may affect: {artifacts_info}")
    confirm = input("Type 'yes' to confirm, or anything else to cancel: ").strip().lower()
    return confirm in ["y", "yes"]

def add_spoke():
    action_desc = "Add a new Spoke to the project."
    hub_path = hub_manager.verify_hub_exists()
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    spoke_path = input("Enter the full path to the new Spoke project: ").strip()
    if not spoke_path or not os.path.isdir(spoke_path):
        print("Error: Invalid or non-existent Spoke path.")
        return

    # Extract info from spoke's WAI-Spoke/WAI-State.json
    spoke_name = os.path.basename(os.path.normpath(spoke_path)) # Default name
    spoke_version = "N/A"
    
    spoke_wai_state_path = os.path.join(spoke_path, "WAI-Spoke", "WAI-State.json")
    if os.path.exists(spoke_wai_state_path):
        try:
            with open(spoke_wai_state_path, 'r') as f:
                spoke_state = json.load(f)
                spoke_name_from_state = spoke_state.get("wheel", {}).get("name")
                spoke_version_from_state = spoke_state.get("wheel", {}).get("version")
                if spoke_name_from_state:
                    spoke_name = spoke_name_from_state
                if spoke_version_from_state:
                    spoke_version = spoke_version_from_state
        except json.JSONDecodeError:
            print(f"Warning: Malformed WAI-State.json in Spoke at {spoke_path}. Using default name/version.")
        except Exception as e:
            print(f"Warning: Error reading WAI-State.json in Spoke at {spoke_path}: {e}. Using default name/version.")

    hub_registry_path = os.path.join(hub_path, "hub-registry.json")
    try:
        hub_registry = {}
        if os.path.exists(hub_registry_path):
            with open(hub_registry_path, 'r') as f:
                hub_registry = json.load(f)
        
        registered_spokes = hub_registry.get("registered_spokes", [])
        
        # Check if spoke already registered
        for spoke in registered_spokes:
            if os.path.abspath(spoke.get('path')) == os.path.abspath(spoke_path):
                print(f"Spoke '{spoke_name}' at '{spoke_path}' is already registered.")
                return

        registered_spokes.append({"name": spoke_name, "path": spoke_path, "version": spoke_version})
        hub_registry["registered_spokes"] = registered_spokes

        with open(hub_registry_path, 'w') as f:
            json.dump(hub_registry, f, indent=2)

        print(f"Spoke '{spoke_name}' (v{spoke_version}) added successfully to the hub registry!")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in hub registry at {hub_registry_path}.")
    except Exception as e:
        print(f"An unexpected error occurred while adding spoke: {e}")

def select_spoke():
    action_desc = "Select an active Spoke for the current session."
    # artifacts_info = "Updates the active spoke in the current session (currently simulated)." # Removed confirmation
    # if confirm_action(action_desc, artifacts_info): # Removed confirmation
    hub_path = hub_manager.verify_hub_exists()
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    hub_registry_path = os.path.join(hub_path, "hub-registry.json")
    try:
        hub_registry = {}
        if os.path.exists(hub_registry_path):
            with open(hub_registry_path, 'r') as f:
                hub_registry = json.load(f)
        
        registered_spokes = hub_registry.get("registered_spokes", [])
        
        if not registered_spokes:
            print("No spokes currently registered to select.")
            return
        
        print("\nRegistered Spokes:")
        for i, spoke in enumerate(registered_spokes):
            print(f"{i+1}. Name: {spoke.get('name', 'N/A')}, Path: {spoke.get('path', 'N/A')}")
        
        selection = input("Enter the number or name of the Spoke to select: ").strip()
        
        selected_spoke = None
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(registered_spokes):
                selected_spoke = registered_spokes[idx]
        else:
            for spoke in registered_spokes:
                if spoke.get('name', '').lower() == selection.lower():
                    selected_spoke = spoke
                    break
        
                    if selected_spoke:
                        # Update WAI-Spoke/WAI-State.json with the active spoke path
                        try:
                            state = hub_manager._get_wai_state()
                            state.setdefault("wheel", {})["active_spoke_path"] = selected_spoke["path"]
                            hub_manager._update_wai_state(state)
                            print(f"Spoke '{selected_spoke['name']}' selected as active spoke for the current session.")
                        except Exception as e:
                            print(f"Error updating active spoke in WAI-State.json: {e}")
                    else:
                        print("Invalid selection. No spoke selected.")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in hub registry at {hub_registry_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    # else: # Removed confirmation
    #     print("Action cancelled.") # Removed confirmation


def list_spokes():
    action_desc = "List all registered Spokes."
    print(f"\nExecuting: {action_desc}")
    
    hub_path = hub_manager.verify_hub_exists()
    if not hub_path:
        print("Error: No hub path configured. Please configure a hub path first.")
        return

    hub_registry_path = os.path.join(hub_path, "hub-registry.json")
    if not os.path.exists(hub_registry_path):
        print(f"Error: Hub registry not found at {hub_registry_path}.")
        return

    try:
        with open(hub_registry_path, 'r') as f:
            hub_registry = json.load(f)
            registered_spokes = hub_registry.get("registered_spokes", [])
            
            if not registered_spokes:
                print("No spokes currently registered.")
                return
            
            print("\nRegistered Spokes:")
            for i, spoke in enumerate(registered_spokes):
                print(f"{i+1}. Name: {spoke.get('name', 'N/A')}, Path: {spoke.get('path', 'N/A')}")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in hub registry at {hub_registry_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
