import pytest
from unittest.mock import patch
import sys
from io import StringIO

# Assuming cli.main can be imported, which will be the case when run via pytest
from cli.main import main as cli_main

# Helper to simulate user input and capture output
def run_cli_with_input(monkeypatch, capsys, inputs):
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_generator))
    
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_main()
    
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0 # Expect clean exit
    
    captured = capsys.readouterr()
    return captured.out

# Test: Root menu displays correctly on startup.
def test_root_menu_displays_on_startup(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["exit"])
    assert "--- WAI CLI Root Menu ---" in output
    assert "1. Hub" in output
    assert "2. Spokes" in output
    assert "3. More" in output

# Test: Numeric selection '1' navigates to Hub menu.
def test_numeric_selection_navigates_to_hub(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["1", "exit"])
    assert "--- Hub Menu ---" in output

# Test: Text alias 'hub' navigates to Hub menu.
def test_text_alias_navigates_to_hub(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["hub", "exit"])
    assert "--- Hub Menu ---" in output

# Test: Invalid numeric input does not exit CLI and reprints menu.
def test_invalid_input_reprints_menu(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["abc", "exit"])
    assert "Error: Invalid input. Please try again." in output
    # Ensure root menu is reprinted after error
    assert output.count("--- WAI CLI Root Menu ---") >= 2

# Test: 'back' command from a submenu returns to parent menu.
def test_back_from_submenu_returns_to_parent(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["1", "back", "exit"])
    assert "--- Hub Menu ---" in output # Entered Hub
    assert output.count("--- WAI CLI Root Menu ---") >= 2 # Returned to root

# Test: 'home' command from a submenu returns to root menu.
def test_home_from_submenu_returns_to_root(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["1", "home", "exit"]) # Hub -> home -> exit
    assert "--- Hub Menu ---" in output # Entered Hub
    assert output.count("--- WAI CLI Root Menu ---") >= 2 # Returned to root

# Test: 'exit' command terminates gracefully.
def test_exit_command_terminates_gracefully(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["exit"])
    assert "Exiting WAI CLI. Goodbye!" in output

# Test: Leaf command execution (e.g., 'hub initialize') prompts for confirmation for state changes.
def test_state_changing_command_prompts_confirmation(monkeypatch, capsys):
    output = run_cli_with_input(monkeypatch, capsys, ["1", "1", "no", "exit"]) # Hub -> Initialize -> no
    assert "--- Confirmation Required ---" in output
    assert "Action cancelled." in output
    
