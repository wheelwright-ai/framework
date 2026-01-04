"""
Framework-First Initialization

Entry point for initializing Wheelwright: framework → hub → projects.
"""

import json
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from .hub import HubManager
from .projects import ProjectDiscovery
from .utils.paths import ensure_directory, normalize_path
from .utils.input import safe_confirm, print_info, print_success, print_warning, print_error
from .utils.exceptions import SpokeAlreadyExistsError, InvalidHubError


def framework_first_init(
    framework_path: Optional[Path] = None,
    verbose: bool = True
) -> None:
    """
    Framework-first initialization workflow.

    Steps:
    1. Initialize framework as spoke
    2. Discover or create hub (default: ../hub)
    3. Add other projects interactively

    Args:
        framework_path: Path to framework (default: current directory)
        verbose: Print status messages

    Examples:
        >>> framework_first_init(Path("/home/user/projects/framework"))

    Raises:
        SpokeAlreadyExistsError: If framework already initialized
        InvalidHubError: If hub setup fails
    """
    # Default to current directory
    if framework_path is None:
        framework_path = Path.cwd()

    framework_path = framework_path.resolve()

    if verbose:
        print_info("\n=== Wheelwright Framework Initialization ===\n")
        print_info(f"Framework path: {framework_path}\n")

    # Step 1: Initialize framework as spoke
    if verbose:
        print_info("Step 1: Initialize framework as spoke")

    init_spoke(framework_path, is_framework=True, verbose=verbose)

    if verbose:
        print_success("Framework initialized as spoke\n")

    # Step 2: Discover or create hub
    if verbose:
        print_info("Step 2: Discover or create hub")

    hub_manager = HubManager()
    hub_path = hub_manager.get_or_create_hub(
        current_path=framework_path,
        auto_discover=True,
        verbose=verbose
    )

    if verbose:
        print_success(f"Hub ready at {hub_path}\n")

    # Step 3: Add other projects
    if verbose:
        print_info("Step 3: Discover and add projects")

    # Ask user if they want to scan for projects
    scan = safe_confirm(
        "Scan for other projects to add to hub?",
        default=True
    )

    if scan:
        discovery = ProjectDiscovery()
        count = discovery.discover_and_add_projects(
            hub_path=hub_path,
            scan_paths=[framework_path.parent],  # Scan parent folder
            exclude_paths=[framework_path, hub_path]
        )

        if count > 0:
            print_success(f"\nAdded {count} project(s) to hub.")
    else:
        print_info("Skipped project discovery. You can add projects later with 'WAI projects add'.")

    # Final summary
    if verbose:
        print_success("\n=== Initialization Complete ===\n")
        print_info("Framework structure:")
        print_info(f"  Framework: {framework_path}")
        print_info(f"  Hub:       {hub_path}")
        print_info("\nNext steps:")
        print_info("  - Run 'WAI status' to see framework status")
        print_info("  - Run 'WAI group create <name>' to create project groups")
        print_info("  - Start working and let Wheelwright track your progress!")


def init_spoke(
    spoke_path: Path,
    is_framework: bool = False,
    verbose: bool = True
) -> None:
    """
    Initialize a spoke (project) with WAI-Spoke/ structure.

    Creates:
    - WAI-Spoke/
    - WAI-Spoke/WAI-Guide.md (from template)
    - WAI-Spoke/WAI-State.json (from template)
    - WAI-Spoke/WAI-State.md (from template)
    - WAI-Spoke/WAI-KB-Sync.json (from template)
    - WAI-Spoke/WAI-Signals.jsonl (empty)
    - WAI-Spoke/WAI-File-Index.json (manifest)

    Args:
        spoke_path: Path to project
        is_framework: True if initializing framework itself
        verbose: Print status messages

    Raises:
        SpokeAlreadyExistsError: If WAI-Spoke/ already exists
    """
    spoke_dir = spoke_path / 'WAI-Spoke'

    # Check if already initialized
    if spoke_dir.exists():
        raise SpokeAlreadyExistsError(f"WAI-Spoke already exists at {spoke_path}")

    # Create WAI-Spoke directory
    ensure_directory(spoke_dir)

    # Get templates directory
    # Assuming wai_cli is in framework/wai_cli/
    framework_root = Path(__file__).parent.parent  # framework/
    templates_dir = framework_root / 'templates' / 'WAI'

    if not templates_dir.exists():
        # Fallback: try relative to current working directory
        templates_dir = Path.cwd() / 'templates' / 'WAI'

    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")

    # Copy template files
    template_files = [
        'WAI-Guide.md',
        'WAI-State.json',
        'WAI-State.md',
        'WAI-KB-Sync.json',
        'WAI-File-Index.json'
    ]

    for template_file in template_files:
        src = templates_dir / template_file
        dst = spoke_dir / template_file

        if src.exists():
            # Read template and substitute variables
            content = src.read_text(encoding='utf-8')

            # Basic variable substitution
            project_name = spoke_path.name
            content = content.replace('{{PROJECT_NAME}}', project_name)
            content = content.replace('{{PROJECT_PATH}}', str(spoke_path))
            content = content.replace('{{SPOKE_PATH}}', str(spoke_dir))
            content = content.replace('{{TIMESTAMP}}', datetime.now().isoformat())

            # Write to destination
            dst.write_text(content, encoding='utf-8')

            if verbose:
                print_info(f"  Created {template_file}")
        else:
            if verbose:
                print_warning(f"  Template not found: {template_file}")

    # Create empty WAI-Signals.jsonl
    signals_file = spoke_dir / 'WAI-Signals.jsonl'
    signals_file.touch()

    if verbose:
        print_info(f"  Created WAI-Signals.jsonl")

    # Create seed and reference folders
    seed_dir = spoke_dir / 'seed'
    ingest_dir = seed_dir / 'ingest'
    reference_dir = seed_dir / 'reference'
    archive_dir = spoke_dir / 'reference'
    ensure_directory(ingest_dir)
    ensure_directory(reference_dir)
    ensure_directory(archive_dir)

    readme = seed_dir / 'README.md'
    if not readme.exists():
        readme.write_text(
            "# Seed Folders\n\n"
            "Use these folders to bootstrap WAI-Spoke with existing context.\n\n"
            "- seed/ingest: drop background docs to be fully subsumed into WAI files.\n"
            "- seed/reference: drop reference docs to be indexed and archived in reference/.\n\n"
            "After running Update, seed/ingest and seed/reference should be empty.\n"
        )
        if verbose:
            print_info("  Created seed/README.md")

    # Create WAI-Workspace.cmd in WAI-Spoke
    workspace_template = templates_dir / 'WAI-Workspace.cmd'
    workspace_target = spoke_dir / 'WAI-Workspace.cmd'
    if workspace_template.exists() and not workspace_target.exists():
        try:
            workspace_target.write_text(workspace_template.read_text(encoding='utf-8'), encoding='utf-8')
            if verbose:
                print_info("  Created WAI-Workspace.cmd")
        except Exception as e:
            if verbose:
                print_warning(f"  Failed to create WAI-Workspace.cmd: {e}")

    # Capture initial project discovery snapshot
    try:
        from .spoke_update import SpokeUpdateProcessor

        updater = SpokeUpdateProcessor(spoke_path)
        review = updater.review_project()

        state_md = spoke_dir / 'WAI-State.md'
        if state_md.exists():
            snapshot = [
                "## Project Discovery Snapshot",
                "",
                f"Project: {review.get('name', spoke_path.name)}",
                f"Path: {review.get('path', str(spoke_path))}",
                "",
                "Key files found:"
            ]
            key_files = review.get('key_files', [])
            if key_files:
                snapshot.extend([f"- {item}" for item in key_files])
            else:
                snapshot.append("- None detected")

            readme_preview = review.get('readme_preview', '').strip()
            if readme_preview:
                snapshot.extend(["", "README preview:", "```", readme_preview, "```"])

            state_md.write_text(state_md.read_text().rstrip() + "\n\n" + "\n".join(snapshot) + "\n")
            if verbose:
                print_info("  Added project discovery snapshot")
    except Exception as exc:
        if verbose:
            print_warning(f"  Discovery snapshot skipped: {exc}")

    # Update WAI-File-Index.json with metadata
    index_file = spoke_dir / 'WAI-File-Index.json'
    if index_file.exists():
        try:
            index_data = json.loads(index_file.read_text())

            # Update metadata
            if 'metadata' not in index_data:
                index_data['metadata'] = {}

            index_data['metadata']['spoke_path'] = str(spoke_dir)
            index_data['metadata']['project_root'] = str(spoke_path)
            index_data['metadata']['project_name'] = spoke_path.name
            index_data['metadata']['last_updated'] = datetime.now().isoformat()
            index_data['metadata']['updated_by'] = 'WAI CLI (init)'

            # Write back
            index_file.write_text(
                json.dumps(index_data, indent=2, ensure_ascii=False) + '\n',
                encoding='utf-8'
            )

            if verbose:
                print_info(f"  Updated WAI-File-Index.json metadata")

        except Exception as e:
            if verbose:
                print_warning(f"  Failed to update WAI-File-Index.json: {e}")

    if verbose:
        print_success(f"Spoke initialized at {spoke_dir}")


def check_spoke_initialized(spoke_path: Path) -> bool:
    """
    Check if spoke is already initialized.

    Args:
        spoke_path: Path to check

    Returns:
        True if WAI-Spoke/ exists

    Examples:
        >>> check_spoke_initialized(Path("/home/user/project"))
        True
    """
    return (spoke_path / 'WAI-Spoke').exists()


def init_spoke_interactive(verbose: bool = True) -> None:
    """
    Interactive spoke initialization.

    Prompts user for:
    - Spoke path (default: current directory)
    - Confirmation

    Args:
        verbose: Print status messages

    Examples:
        >>> init_spoke_interactive()
    """
    from .utils.input import safe_input

    print_info("\n=== Initialize Spoke ===\n")

    # Get spoke path
    current_dir = Path.cwd()
    path_str = safe_input(
        "Spoke path",
        default=str(current_dir),
        max_length=500
    )

    if path_str is None:
        print_info("Initialization cancelled.")
        return

    try:
        spoke_path = normalize_path(path_str)
    except Exception as e:
        print_error(f"Invalid path: {e}")
        return

    # Check if already initialized
    if check_spoke_initialized(spoke_path):
        print_warning(f"Spoke already initialized at {spoke_path}")
        return

    # Confirm
    confirm = safe_confirm(
        f"Initialize spoke at {spoke_path}?",
        default=True
    )

    if not confirm:
        print_info("Initialization cancelled.")
        return

    # Initialize
    try:
        init_spoke(spoke_path, is_framework=False, verbose=verbose)
        print_success(f"\nSpoke initialized at {spoke_path}")
    except Exception as e:
        print_error(f"Initialization failed: {e}")
