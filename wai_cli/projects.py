"""
Project Discovery and Selection

Enhanced project detection with interactive checklist for registration.
"""

from pathlib import Path
from typing import List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

from .utils.input import safe_input, print_info, print_success, print_error, single_key_input
from .utils.registry import add_project


@dataclass
class ProjectInfo:
    """Discovered project information."""

    path: Path
    name: str
    project_type: List[str]  # ["WAI-enabled", "Git", "Python", etc.]
    description: Optional[str] = None
    priority: int = 0  # Higher priority shown first

    def __post_init__(self):
        """Calculate priority based on project type."""
        # WAI-enabled projects get highest priority
        if "WAI-enabled" in self.project_type:
            self.priority = 100
        # Git repos are second priority
        elif "Git" in self.project_type:
            self.priority = 50
        else:
            self.priority = 10

    def format_types(self) -> str:
        """Format project types for display."""
        return ", ".join(self.project_type) if self.project_type else "Unknown"

    def __repr__(self):
        return f"ProjectInfo({self.name}, types={self.project_type})"


class ProjectDiscovery:
    """Project discovery and interactive selection."""

    def scan_for_projects(
        self,
        scan_paths: List[Path],
        exclude_paths: Optional[List[Path]] = None,
        max_depth: int = 2
    ) -> List[ProjectInfo]:
        """
        Enhanced project detection.

        Detection priority:
        1. WAI-Spoke/ folder (Wheelwright-enabled)
        2. .git (Git repository)
        3. Language-specific markers:
           - package.json (Node.js)
           - pyproject.toml, setup.py (Python)
           - Cargo.toml (Rust)
           - go.mod (Go)
           - pom.xml, build.gradle (Java)

        Args:
            scan_paths: Directories to scan
            exclude_paths: Paths to exclude from scan
            max_depth: Maximum directory depth to scan

        Returns:
            List of discovered projects, sorted by priority

        Examples:
            >>> discovery = ProjectDiscovery()
            >>> projects = discovery.scan_for_projects([Path("/home/user/projects")])
            [ProjectInfo(framework, types=['WAI-enabled', 'Git', 'Python']), ...]
        """
        exclude_paths = exclude_paths or []
        exclude_set = {p.resolve() for p in exclude_paths}

        discovered: List[ProjectInfo] = []
        seen_paths: Set[Path] = set()

        for scan_path in scan_paths:
            if not scan_path.exists() or not scan_path.is_dir():
                continue

            # Scan directory tree
            self._scan_directory(
                scan_path,
                discovered,
                seen_paths,
                exclude_set,
                current_depth=0,
                max_depth=max_depth
            )

        # Sort by priority (highest first), then by name
        discovered.sort(key=lambda p: (-p.priority, p.name.lower()))

        return discovered

    def _scan_directory(
        self,
        directory: Path,
        discovered: List[ProjectInfo],
        seen_paths: Set[Path],
        exclude_set: Set[Path],
        current_depth: int,
        max_depth: int
    ) -> None:
        """
        Recursively scan directory for projects.

        Args:
            directory: Directory to scan
            discovered: List to append discoveries to
            seen_paths: Set of already-seen paths (deduplication)
            exclude_set: Set of paths to exclude
            current_depth: Current recursion depth
            max_depth: Maximum depth to recurse
        """
        # Resolve path for comparison
        try:
            resolved = directory.resolve()
        except Exception:
            return  # Can't resolve path

        # Skip if excluded or already seen
        if resolved in exclude_set or resolved in seen_paths:
            return

        # Check if this directory is a project
        project_info = self._detect_project(directory)
        if project_info:
            discovered.append(project_info)
            seen_paths.add(resolved)
            # Don't recurse into detected projects
            return

        # Recurse into subdirectories if not at max depth
        if current_depth >= max_depth:
            return

        try:
            for item in directory.iterdir():
                if not item.is_dir():
                    continue

                # Skip hidden directories (except .git check)
                if item.name.startswith('.') and item.name != '.git':
                    continue

                # Skip common non-project directories
                if item.name in {'node_modules', 'venv', '__pycache__', 'dist', 'build', 'target'}:
                    continue

                self._scan_directory(
                    item,
                    discovered,
                    seen_paths,
                    exclude_set,
                    current_depth + 1,
                    max_depth
                )
        except PermissionError:
            pass  # Can't read directory

    def _detect_project(self, directory: Path) -> Optional[ProjectInfo]:
        """
        Detect if directory is a project.

        Detection logic:
        - WAI-Spoke/ → WAI-enabled project
        - .git → Git repository
        - Language markers → Specific project type

        Args:
            directory: Directory to check

        Returns:
            ProjectInfo if project detected, None otherwise
        """
        project_types: List[str] = []

        # Check for WAI-Spoke/
        if (directory / 'WAI-Spoke').exists():
            project_types.append("WAI-enabled")

        # Check for .git
        if (directory / '.git').exists():
            project_types.append("Git")

        # Check language-specific markers
        if (directory / 'package.json').exists():
            project_types.append("Node.js")

        if (directory / 'pyproject.toml').exists() or (directory / 'setup.py').exists():
            project_types.append("Python")

        if (directory / 'Cargo.toml').exists():
            project_types.append("Rust")

        if (directory / 'go.mod').exists():
            project_types.append("Go")

        if (directory / 'pom.xml').exists() or (directory / 'build.gradle').exists():
            project_types.append("Java")

        if (directory / 'Gemfile').exists():
            project_types.append("Ruby")

        if (directory / 'composer.json').exists():
            project_types.append("PHP")

        # If no markers found, not a project
        if not project_types:
            return None

        # Create ProjectInfo
        name = directory.name

        return ProjectInfo(
            path=directory.resolve(),
            name=name,
            project_type=project_types
        )

    def present_interactive_checklist(
        self,
        projects: List[ProjectInfo],
        hub_path: Path
    ) -> List[ProjectInfo]:
        """
        Interactive selection: y/n per project.

        Format:
        ```
        Found 12 projects:
        [1] ✓ framework (WAI-enabled, Git, Python)
            /home/user/projects/framework
        [2] my-app (Git, Node.js)
            /home/user/projects/my-app

        Add to hub? (y/n per project, 'all'/'none'/'quit')
        [1]: y
        [2]: n
        ...
        ```

        Args:
            projects: List of discovered projects
            hub_path: Path to hub (for registration)

        Returns:
            List of selected projects

        Examples:
            >>> selected = discovery.present_interactive_checklist(projects, hub_path)
        """
        if not projects:
            print_info("\nNo projects discovered.")
            return []

        # Display discovered projects
        print_info(f"\nFound {len(projects)} project(s):\n")

        for i, project in enumerate(projects, 1):
            marker = "✓" if "WAI-enabled" in project.project_type else " "
            types = project.format_types()
            print_info(f"[{i}]\t{marker} {project.name} ({types})")
            print_info(f"\t\t{project.path}")

        # Format options with colored action letters
        COLOR = '\033[36m'  # Cyan for action letters
        RESET = '\033[0m'

        print_info("\nAdd projects to hub?")
        print_info(f"  Options: {COLOR}Y{RESET}es  {COLOR}N{RESET}o  {COLOR}A{RESET}ll  {COLOR}C{RESET}ancel")
        print_info("")

        selected: List[ProjectInfo] = []

        for i, project in enumerate(projects, 1):
            # Prompt for this project (single-key input)
            prompt = f"[{i}] Add '{project.name}'?"

            response = single_key_input(prompt, ['y', 'n', 'a', 'c'])

            if response is None:
                # Ctrl+C or cancelled
                print_info("\nSelection cancelled.")
                break

            # Handle commands
            if response in ('cancel', 'c'):
                print_info("\nSelection cancelled.")
                break

            elif response == 'all' or response == 'a':
                # Add remaining projects
                selected.extend(projects[i-1:])
                print_info(f"\nAdded all remaining projects ({len(projects) - i + 1}).")
                break

            elif response in ('y', 'yes'):
                selected.append(project)
                print_success(f"  → Added '{project.name}'")

            elif response in ('n', 'no'):
                print_info(f"  → Skipped '{project.name}'")

            else:
                # Invalid input, treat as 'no' and continue
                print_info(f"  → Invalid input ('{response}'), skipping '{project.name}'")

        return selected

    def register_selected_projects(
        self,
        selected: List[ProjectInfo],
        hub_path: Path
    ) -> int:
        """
        Register selected projects to hub.

        Args:
            selected: List of selected projects
            hub_path: Path to hub

        Returns:
            Number of successfully registered projects

        Examples:
            >>> count = discovery.register_selected_projects(selected, hub_path)
            3
        """
        if not selected:
            return 0

        print_info(f"\nRegistering {len(selected)} project(s) to hub...")

        registered_count = 0

        for project in selected:
            try:
                # Generate description from project types
                description = f"{project.format_types()} project"

                add_project(
                    hub_path=hub_path,
                    project_path=project.path,
                    name=project.name,
                    description=description
                )

                print_success(f"Registered '{project.name}'")
                registered_count += 1

            except Exception as e:
                print_error(f"Failed to register '{project.name}': {e}")

        return registered_count

    def discover_and_add_projects(
        self,
        hub_path: Path,
        scan_paths: Optional[List[Path]] = None,
        exclude_paths: Optional[List[Path]] = None,
        auto_add: bool = False
    ) -> int:
        """
        Complete workflow: discover, select, and register projects.

        Args:
            hub_path: Path to hub
            scan_paths: Directories to scan (default: parent of hub)
            exclude_paths: Paths to exclude
            auto_add: Automatically add all without prompting

        Returns:
            Number of registered projects

        Examples:
            >>> discovery = ProjectDiscovery()
            >>> count = discovery.discover_and_add_projects(hub_path)
        """
        # Default scan paths: 2 levels above hub (grandparent)
        if scan_paths is None:
            scan_paths = [hub_path.parent.parent]

        # Add hub to exclude list
        if exclude_paths is None:
            exclude_paths = []
        exclude_paths.append(hub_path)

        # Scan for projects
        print_info("Scanning for projects...")
        discovered = self.scan_for_projects(scan_paths, exclude_paths, max_depth=2)

        if not discovered:
            print_info("No projects discovered.")
            return 0

        # Filter out already-registered projects
        from .utils.registry import load_registry
        try:
            registry = load_registry(hub_path)
            registered_paths = {Path(p['path']).resolve() for p in registry.get('projects', [])}

            # Filter discovered projects
            before_count = len(discovered)
            discovered = [p for p in discovered if p.path.resolve() not in registered_paths]
            filtered_count = before_count - len(discovered)

            if filtered_count > 0:
                print_info(f"Filtered {filtered_count} already-registered project(s).")

            if not discovered:
                print_info("All discovered projects are already registered.")
                return 0
        except Exception:
            pass  # If registry load fails, continue with full list

        # Select projects
        if auto_add:
            selected = discovered
            print_info(f"Auto-adding {len(selected)} project(s)...")
        else:
            selected = self.present_interactive_checklist(discovered, hub_path)

        if not selected:
            print_info("No projects selected.")
            return 0

        # Register projects
        return self.register_selected_projects(selected, hub_path)
