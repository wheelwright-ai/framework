"""
Groups Management

CRUD operations for project groups in the hub registry.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from .utils.registry import (
    load_registry,
    create_group as registry_create_group,
    delete_group as registry_delete_group,
    add_spoke_to_group as registry_add_spoke,
    remove_spoke_from_group as registry_remove_spoke,
    list_groups as registry_list_groups,
    get_project
)
from .utils.input import safe_confirm, print_info, print_success, print_warning, print_error
from .utils.exceptions import RegistryError, ValidationError
from .utils.paths import normalize_path


class GroupsManager:
    """Groups CRUD operations."""

    def __init__(self, hub_path: Path):
        """
        Initialize groups manager.

        Args:
            hub_path: Path to hub directory
        """
        self.hub_path = hub_path

    def create_group(
        self,
        name: str,
        description: Optional[str] = None,
        verbose: bool = True
    ) -> bool:
        """
        Create a new group.

        Args:
            name: Group name
            description: Optional group description
            verbose: Print status messages

        Returns:
            True if created successfully, False otherwise

        Examples:
            >>> manager = GroupsManager(Path("/home/user/hub"))
            >>> manager.create_group("clients", "Client projects")
            True
        """
        try:
            registry_create_group(
                hub_path=self.hub_path,
                group_name=name,
                description=description
            )

            if verbose:
                print_success(f"Created group '{name}'")

            return True

        except RegistryError as e:
            if verbose:
                print_error(str(e))
            return False

        except Exception as e:
            if verbose:
                print_error(f"Failed to create group: {e}")
            return False

    def list_groups(self, verbose: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        List all groups.

        Args:
            verbose: Show detailed information

        Returns:
            Dictionary of groups

        Examples:
            >>> manager = GroupsManager(Path("/home/user/hub"))
            >>> groups = manager.list_groups()
            {'clients': {'name': 'clients', 'spokes': [...], ...}, ...}
        """
        try:
            groups = registry_list_groups(self.hub_path)

            if not groups:
                print_info("No groups defined.")
                return {}

            # Display groups
            print_info(f"\nGroups ({len(groups)}):\n")

            for group_name, group_data in groups.items():
                spokes_count = len(group_data.get('spokes', []))
                description = group_data.get('description', '')

                if verbose:
                    print_info(f"  {group_name} ({spokes_count} project(s))")
                    if description:
                        print_info(f"    Description: {description}")

                    # List spokes
                    if spokes_count > 0:
                        print_info(f"    Projects:")
                        for spoke_path in group_data.get('spokes', []):
                            # Try to get project name
                            project = get_project(self.hub_path, spoke_path)
                            if project:
                                print_info(f"      - {project['name']} ({spoke_path})")
                            else:
                                print_info(f"      - {spoke_path}")
                    print_info("")
                else:
                    desc_suffix = f" - {description}" if description else ""
                    print_info(f"  {group_name} ({spokes_count} project(s)){desc_suffix}")

            return groups

        except Exception as e:
            print_error(f"Failed to list groups: {e}")
            return {}

    def add_spoke_to_group(
        self,
        group_name: str,
        spoke_identifier: str,
        verbose: bool = True
    ) -> bool:
        """
        Add spoke to group.

        Args:
            group_name: Name of group
            spoke_identifier: Spoke name or path
            verbose: Print status messages

        Returns:
            True if added successfully, False otherwise

        Examples:
            >>> manager.add_spoke_to_group("clients", "my-client-app")
            True
        """
        try:
            # Resolve spoke path
            # First, try as project name
            project = get_project(self.hub_path, spoke_identifier)

            if project:
                spoke_path = Path(project['path'])
            else:
                # Try as path
                try:
                    spoke_path = normalize_path(spoke_identifier)
                except Exception:
                    if verbose:
                        print_error(f"Spoke not found: {spoke_identifier}")
                    return False

            # Add to group
            registry_add_spoke(
                hub_path=self.hub_path,
                group_name=group_name,
                spoke_path=spoke_path
            )

            if verbose:
                name = project['name'] if project else spoke_path.name
                print_success(f"Added '{name}' to group '{group_name}'")

            return True

        except RegistryError as e:
            if verbose:
                print_error(str(e))
            return False

        except Exception as e:
            if verbose:
                print_error(f"Failed to add spoke to group: {e}")
            return False

    def remove_spoke_from_group(
        self,
        group_name: str,
        spoke_identifier: str,
        verbose: bool = True
    ) -> bool:
        """
        Remove spoke from group.

        Args:
            group_name: Name of group
            spoke_identifier: Spoke name or path
            verbose: Print status messages

        Returns:
            True if removed successfully, False otherwise

        Examples:
            >>> manager.remove_spoke_from_group("clients", "my-client-app")
            True
        """
        try:
            # Resolve spoke path
            project = get_project(self.hub_path, spoke_identifier)

            if project:
                spoke_path = Path(project['path'])
            else:
                # Try as path
                try:
                    spoke_path = normalize_path(spoke_identifier)
                except Exception:
                    if verbose:
                        print_error(f"Spoke not found: {spoke_identifier}")
                    return False

            # Remove from group
            registry_remove_spoke(
                hub_path=self.hub_path,
                group_name=group_name,
                spoke_path=spoke_path
            )

            if verbose:
                name = project['name'] if project else spoke_path.name
                print_success(f"Removed '{name}' from group '{group_name}'")

            return True

        except RegistryError as e:
            if verbose:
                print_error(str(e))
            return False

        except Exception as e:
            if verbose:
                print_error(f"Failed to remove spoke from group: {e}")
            return False

    def delete_group(
        self,
        name: str,
        force: bool = False,
        verbose: bool = True
    ) -> bool:
        """
        Delete a group.

        Args:
            name: Group name
            force: Skip confirmation
            verbose: Print status messages

        Returns:
            True if deleted successfully, False otherwise

        Examples:
            >>> manager.delete_group("clients", force=True)
            True
        """
        try:
            # Load registry to check if group has spokes
            registry = load_registry(self.hub_path)
            group = registry.get('groups', {}).get(name)

            if not group:
                if verbose:
                    print_error(f"Group not found: {name}")
                return False

            # Check if group has spokes
            spokes_count = len(group.get('spokes', []))

            if spokes_count > 0 and not force:
                print_warning(f"Group '{name}' contains {spokes_count} project(s).")
                confirm = safe_confirm(
                    "Delete anyway? (projects will remain in registry)",
                    default=False
                )

                if not confirm:
                    print_info("Deletion cancelled.")
                    return False

            # Delete group
            registry_delete_group(
                hub_path=self.hub_path,
                group_name=name
            )

            if verbose:
                print_success(f"Deleted group '{name}'")

            return True

        except RegistryError as e:
            if verbose:
                print_error(str(e))
            return False

        except Exception as e:
            if verbose:
                print_error(f"Failed to delete group: {e}")
            return False

    def get_group_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed group information.

        Args:
            name: Group name

        Returns:
            Group dictionary or None if not found

        Examples:
            >>> info = manager.get_group_info("clients")
            {'name': 'clients', 'spokes': [...], ...}
        """
        try:
            groups = registry_list_groups(self.hub_path)
            return groups.get(name)
        except Exception:
            return None
