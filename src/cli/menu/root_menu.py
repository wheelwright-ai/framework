# src/cli/menu/root_menu.py
# Defines the structure and behavior of the main root menu.

import sys
# Import handlers and display functions from specific menu modules
from cli.menu.hub_menu import display_hub_menu, handle_hub_menu_input
from cli.menu.spokes_menu import display_spokes_menu, handle_spokes_menu_input
from cli.menu.more_menu import display_more_menu, handle_more_menu_input

# --- Root Menu Definition ---
ROOT_MENU_OPTIONS = {
    "1": {"name": "Hub", "alias": ["hub"], "display_func": display_hub_menu, "handler_func": handle_hub_menu_input},
    "2": {"name": "Spokes", "alias": ["spokes"], "display_func": display_spokes_menu, "handler_func": handle_spokes_menu_input},
    "3": {"name": "More", "alias": ["more"], "display_func": display_more_menu, "handler_func": handle_more_menu_input},
}

def display_root_menu():
    print("\n--- WAI CLI Root Menu ---")
    for key, option in ROOT_MENU_OPTIONS.items():
        print(f"{key}. {option['name']}")
    print("\nEnter 'back', 'home', or 'exit'.")
    print("------------------------")

def handle_root_menu_input(user_input):
    selected_option = None
    # Check numeric input
    if user_input in ROOT_MENU_OPTIONS:
        selected_option = ROOT_MENU_OPTIONS[user_input]
    else:
        # Check text aliases
        for key, option in ROOT_MENU_OPTIONS.items():
            if user_input in option["alias"]:
                selected_option = option
                break

    if selected_option:
        return {"type": "menu", "display_func": selected_option["display_func"], "handler_func": selected_option["handler_func"]}
    else:
        print("Error: Invalid input. Please try again.")
        return "invalid"
