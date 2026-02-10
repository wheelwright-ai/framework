# src/cli/commands/spokes_commands.py
# Contains commands related to managing Spokes.

def confirm_action(action_description, artifacts_info=""):
    """Prompts user for confirmation before executing a state-changing action."""
    print(f"\n--- Confirmation Required ---")
    print(f"Action: {action_description}")
    if artifacts_info:
        print(f"This may affect: {artifacts_info}")
    confirm = input("Type 'yes' to confirm, or anything else to cancel: ").strip().lower()
    return confirm == "yes"

def add_spoke():
    action_desc = "Add a new Spoke to the project."
    artifacts_info = "Modifies project configuration (e.g., WAI-State.json)."
    if confirm_action(action_desc, artifacts_info):
        print(f"Executing: {action_desc} (Placeholder)")
        # Actual implementation will go here
        print("Spoke added successfully! (Placeholder)")
    else:
        print("Action cancelled.")

def select_spoke():
    action_desc = "Select an active Spoke for the current session."
    artifacts_info = "Modifies current session context in WAI-State.json."
    if confirm_action(action_desc, artifacts_info):
        print(f"Executing: {action_desc} (Placeholder)")
        # Actual implementation will go here
        print("Spoke selected successfully! (Placeholder)")
    else:
        print("Action cancelled.")

def list_spokes():
    action_desc = "List all registered Spokes."
    print(f"\nExecuting: {action_desc} (Placeholder)")
    # Actual implementation will go here
    print("Spoke 1: Project Alpha")
    print("Spoke 2: Project Beta")
    print("(Placeholder list of Spokes)")
