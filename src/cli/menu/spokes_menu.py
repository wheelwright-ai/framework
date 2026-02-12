# src/cli/menu/spokes_menu.py
# Defines the structure and behavior of the Spokes menu.

from cli.commands import spokes_commands

def display_spokes_menu():
    print("\n--- Spokes Menu ---")
    print("1. Add")
    print("2. Select")
    print("3. List")
    print("\nEnter 'back', 'home', or 'exit'.")
    print("-------------------")

def handle_spokes_menu_input(user_input):
    if user_input == "1" or user_input == "add":
        return {"type": "command", "command_func": spokes_commands.add_spoke}
    elif user_input == "2" or user_input == "select":
        return {"type": "command", "command_func": spokes_commands.select_spoke}
    elif user_input == "3" or user_input == "list":
        return {"type": "command", "command_func": spokes_commands.list_spokes}
    else:
        print("Error: Invalid input. Please try again.")
        return "invalid"