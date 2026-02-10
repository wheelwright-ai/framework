# src/cli/menu/hub_menu.py
# Defines the structure and behavior of the Hub menu.

from cli.commands import hub_commands

def display_hub_menu():
    print("\n--- Hub Menu ---")
    print("1. Initialize")
    print("2. Teach")
    print("3. Learn")
    print("4. Version")
    print("\nEnter 'back', 'home', or 'exit'.")
    print("----------------")

def handle_hub_menu_input(user_input):
    if user_input == "1" or user_input == "initialize":
        return {"type": "command", "command_func": hub_commands.initialize_hub}
    elif user_input == "2" or user_input == "teach":
        return {"type": "command", "command_func": hub_commands.teach_hub}
    elif user_input == "3" or user_input == "learn":
        return {"type": "command", "command_func": hub_commands.learn_hub}
    elif user_input == "4" or user_input == "version":
        return {"type": "command", "command_func": hub_commands.get_hub_version}
    else:
        print("Error: Invalid input. Please try again.")
        return "invalid"
