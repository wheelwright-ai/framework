import sys
from cli.menu.root_menu import display_root_menu, handle_root_menu_input
from cli.visualization.wheel_momentum import display_wheel_momentum # New import


# Menu stack to handle nested menus
MENU_STACK = []

def main():
    display_wheel_momentum() # Call visualization here
    MENU_STACK.append({"display": display_root_menu, "handler": handle_root_menu_input}) # Start with root menu

    while True:
        current_menu = MENU_STACK[-1] # Get current menu from top of stack
        current_menu["display"]() # Display current menu

        user_input = input("> ").strip().lower()

        if user_input == "exit":
            print("Exiting WAI CLI. Goodbye!")
            sys.exit(0)
        elif user_input == "back":
            if len(MENU_STACK) > 1: # Cannot go back from root
                MENU_STACK.pop()
                continue # Redisplay new current menu
            else:
                print("Already at the root menu. Cannot go back further.")
                continue
        elif user_input == "home":
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
                print(f"Executing command: {next_action['command_func'].__name__} (Placeholder)")
                next_action["command_func"]()
                # For now, stay in the current menu after command execution
                pass


if __name__ == "__main__":
    main()
