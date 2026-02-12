# src/cli/ui/header.py
# Implements the dynamic header for the WAI CLI.

from cli import hub_manager

def display_header():
    state = hub_manager._get_wai_state()
    project_name = state.get("wheel", {}).get("name", "Wheelwright AI")
    framework_version = state.get("wheel", {}).get("version", "N/A")

    header_text = f"\n--- {project_name} CLI (v{framework_version}) ---"
    print(header_text)
