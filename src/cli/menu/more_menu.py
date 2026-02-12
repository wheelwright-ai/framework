# src/cli/menu/more_menu.py
# Defines the structure and behavior of the More menu.

from cli.commands import more_commands

def display_more_menu():
    print("\n--- More Menu ---")
    print("1. Framework Info")
    print("2. CLI Info")
    print("3. List Skills")
    print("\nEnter 'back', 'home', or 'exit'.")
    print("-----------------")

def handle_more_menu_input(user_input):
    if user_input == "1" or user_input == "framework":
        return {"type": "command", "command_func": more_commands.display_framework_info}
    elif user_input == "2" or user_input == "cli":
        return {"type": "command", "command_func": more_commands.display_cli_info}
    elif user_input == "3" or user_input == "skills":
        return {"type": "command", "command_func": more_commands.list_skills}
    else:
        print("Error: Invalid input. Please try again.")
        return "invalid"