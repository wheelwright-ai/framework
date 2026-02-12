import sys
import os
from cli.menu.root_menu import display_root_menu, handle_root_menu_input
from cli.visualization.wheel_momentum import display_wheel_momentum
from cli import hub_manager
from cli.ui.header import display_header


# Menu stack to handle nested menus
MENU_STACK = []

def main():
    # --- Hub Verification/Initiation ---
    hub_path = hub_manager.verify_hub_exists() # Read from WAI-State.json
    if not (hub_path and os.path.isdir(hub_path)):
        user_response = hub_manager.prompt_for_hub_path()
        if user_response == "init":
            new_hub_path = input("Enter the full path for the new WAI Hub: ").strip()
            if new_hub_path and os.path.isdir(new_hub_path):
                if hub_manager.initiate_hub(new_hub_path):
                    hub_path = new_hub_path
                else: # failed to initiate
                    hub_path = None
            else: # invalid path
                hub_path = None
        else: # user provided a path
            if os.path.isdir(user_response):
                if hub_manager.initiate_hub(user_response):
                    hub_path = user_response
                else: # failed to initiate
                    hub_path = None
            else: # invalid path
                hub_path = None
    
    if not hub_path:
        print("Could not configure WAI Hub. Exiting.")
        sys.exit(1)


    # --- Proceed after hub is verified/initiated ---
    display_header() # Call dynamic header here
    display_wheel_momentum() # Call visualization here
    MENU_STACK.append({"display": display_root_menu, "handler": handle_root_menu_input}) # Start with root menu

    while True:
        try: # Added try-except for KeyboardInterrupt
            current_menu = MENU_STACK[-1] # Get current menu from top of stack
            current_menu["display"]() # Display current menu

            user_input = input("> ").strip().lower()

            if user_input in ["q", "exit"]: # Check for 'q' or 'exit'
                print("Exiting WAI CLI. Goodbye!")
                sys.exit(0)
            elif user_input in ["b", "back"]: # Check for 'b' or 'back'
                if len(MENU_STACK) > 1: # Cannot go back from root
                    MENU_STACK.pop()
                    continue # Redisplay new current menu
                else:
                    print("Already at the root menu. Cannot go back further.")
                    continue
            elif user_input in ["h", "home"]: # Check for 'h' or 'home'
                MENU_STACK.clear()
                MENU_STACK.append({"display": display_root_menu, "handler": handle_root_menu_input})
                continue # Redisplay root menu

            # Handle input for the current menu
            next_action = current_menu["handler"](user_input)

            if next_action == "invalid":
                # Invalid input handled by the handler, just redisplay current menu
                pass # Continue loop, redisplay current menu
            elif next_action and isinstance(next_action, dict): # Ensure it's a dict before checking "type"
                if next_action.get("type") == "menu":
                    MENU_STACK.append({"display": next_action["display_func"], "handler": next_action["handler_func"]})
                elif next_action.get("type") == "command":
                    print(f"Executing command: {next_action['command_func'].__name__}")
                    next_action["command_func"]()
                    # For now, stay in the current menu after command execution
                    pass
        except KeyboardInterrupt: # Handle Ctrl-C gracefully
            print("\nExiting WAI CLI. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
