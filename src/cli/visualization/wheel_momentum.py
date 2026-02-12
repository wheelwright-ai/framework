import json
import os
from cli import hub_manager # Import hub_manager to access WAI-State.json and WAI-Lugs.jsonl

def display_wheel_momentum(): # Restored signature
    """
    Displays the "Wheel Momentum" visualization.
    This is a situational awareness snapshot, not a metrics dashboard.
    It shows approximate wheel size, recent spoke activity, LUG interaction,
    and signs of stall or runaway behavior using ASCII art.
    """
    state = hub_manager._get_wai_state()
    
    # --- Gather Data ---
    # Hub Information
    hub_path = hub_manager.verify_hub_exists() # Get the current hub path
    hub_name = "Not Configured"
    hub_version = "N/A"
    if hub_path:
        hub_profile_path = os.path.join(hub_path, "hub-profile.json")
        if os.path.exists(hub_profile_path):
            try:
                with open(hub_profile_path, 'r') as f:
                    hub_profile = json.load(f)
                    hub_name = hub_profile.get("hub_name", "Unknown Hub")
                    hub_version = hub_profile.get("version", "1.0.0") # Assuming hub-profile.json can have a version
            except json.JSONDecodeError:
                hub_name = "Error reading hub profile."
        else:
            hub_name = "Hub profile not found."
    
    # Framework Information
    framework_version = state.get("wheel", {}).get("version", "N/A")
    framework_path = os.getcwd() # Current working directory is the framework path

    # Approximate wheel size (number of spokes)
    spoke_count = 0
    spoke_display = "No spokes configured."

    if hub_path: # Only read from hub_registry if hub_path exists
        hub_registry_path = os.path.join(hub_path, "hub-registry.json")
        if os.path.exists(hub_registry_path):
            try:
                with open(hub_registry_path, 'r') as f:
                    hub_registry = json.load(f)
                    registered_spokes = hub_registry.get("registered_spokes", [])
                    spoke_count = len(registered_spokes)
                    if spoke_count == 0:
                        spoke_display = "No spokes configured."
                    elif spoke_count == 1:
                        spoke_display = "1 spoke active."
                    else:
                        spoke_display = f"{spoke_count} spokes."
            except json.JSONDecodeError:
                spoke_display = "Error reading hub registry."
            except Exception as e:
                spoke_display = f"Error: {e}"
        else:
            spoke_display = "Hub registry not found."
    else:
        spoke_display = "Hub not configured."
        
    # LUG interaction over last N learn cycles
    lug_count = 0
    lug_activity = "fading ░░░░" # Default to very low
    
    # Try to read WAI-Lugs.jsonl and count lugs
    try:
        if os.path.exists("WAI-Spoke/WAI-Lugs.jsonl"):
            with open("WAI-Spoke/WAI-Lugs.jsonl", 'r') as f:
                for line in f:
                    try:
                        lug_count += 1
                    except json.JSONDecodeError:
                        pass # Ignore malformed lines
        
        if lug_count > 10:
            lug_activity = "strong ▓▓▓▓"
        elif lug_count > 5:
            lug_activity = "steady ▓▓▒░"
        elif lug_count > 0:
            lug_activity = "low ▓▒░░"

    except Exception as e:
        print(f"Error reading lugs for visualization: {e}")
        lug_activity = "unknown ▒▒▒▒" # Indicate error


    # Momentum and stall behavior (Placeholder for now, requires more complex logic)
    momentum_display = "↗ steady" # Placeholder
    
    print("\n        .--.")
    print("       / /\\\\")
    print("      | | ||")
    print("      \\ \\//")
    print("       '--'\n")

    print(f"Hub: {hub_name} ({hub_path}) v{hub_version}")
    print(f"Framework: v{framework_version} at {framework_path}")
    print(f"Spokes: {spoke_display}")
    print(f"Momentum: {momentum_display}")
    print(f"LUGs (total): {lug_count} ({lug_activity})")
    print("\n(Dynamic Wheel Momentum Visualization)\n")