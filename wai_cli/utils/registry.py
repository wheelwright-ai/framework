"""
Registry Manipulation Utilities

Safe loading, saving, and modification of hub registry (wheel-projects.json).
Includes atomic writes with backup to prevent corruption.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .exceptions import RegistryError, PathNotFoundError, ValidationError


def load_registry(hub_path: Path) -> Dict[str, Any]:
    """
    Load hub registry with validation.

    Args:
        hub_path: Path to hub directory

    Returns:
        Registry dictionary

    Raises:
        RegistryError: If registry is invalid or missing
        PathNotFoundError: If hub path doesn't exist

    Examples:
        >>> registry = load_registry(Path("/home/user/hub"))
        {'version': '2.0', 'projects': [...], 'groups': {...}}
    """
    if not hub_path.exists():
        raise PathNotFoundError(f"Hub path does not exist: {hub_path}")

    registry_file = hub_path / 'registry' / 'wheel-projects.json'

    if not registry_file.exists():
        raise RegistryError(f"Registry file not found: {registry_file}")

    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except json.JSONDecodeError as e:
        raise RegistryError(f"Invalid JSON in registry: {e}")
    except Exception as e:
        raise RegistryError(f"Failed to load registry: {e}")

    # Validate structure
    if not isinstance(registry, dict):
        raise RegistryError("Registry must be a JSON object")

    if 'projects' not in registry:
        raise RegistryError("Registry missing 'projects' field")

    if not isinstance(registry['projects'], list):
        raise RegistryError("Registry 'projects' must be an array")

    # Ensure groups field exists (backward compatibility)
    if 'groups' not in registry:
        registry['groups'] = {}

    return registry


def save_registry(
    hub_path: Path,
    registry: Dict[str, Any],
    backup: bool = True
) -> None:
    """
    Save registry with atomic write and optional backup.

    Args:
        hub_path: Path to hub directory
        registry: Registry dictionary to save
        backup: Create backup before saving

    Raises:
        RegistryError: If save fails
        ValidationError: If registry is invalid

    Implementation:
        1. Validate registry structure
        2. Create backup if requested
        3. Write to temporary file
        4. Atomic rename to target file
    """
    if not hub_path.exists():
        raise PathNotFoundError(f"Hub path does not exist: {hub_path}")

    registry_dir = hub_path / 'registry'
    if not registry_dir.exists():
        raise PathNotFoundError(f"Registry directory not found: {registry_dir}")

    registry_file = registry_dir / 'wheel-projects.json'

    # Validate registry structure
    _validate_registry(registry)

    # Create backup if requested and file exists
    if backup and registry_file.exists():
        backup_file = registry_dir / f'wheel-projects.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            shutil.copy2(registry_file, backup_file)
        except Exception as e:
            raise RegistryError(f"Failed to create backup: {e}")

    # Atomic write: write to temp, then rename
    temp_file = registry_dir / 'wheel-projects.json.tmp'

    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Trailing newline

        # Atomic rename
        temp_file.replace(registry_file)

    except Exception as e:
        # Clean up temp file on failure
        if temp_file.exists():
            temp_file.unlink()
        raise RegistryError(f"Failed to save registry: {e}")


def _validate_registry(registry: Dict[str, Any]) -> None:
    """
    Validate registry structure.

    Raises:
        ValidationError: If registry is invalid
    """
    if not isinstance(registry, dict):
        raise ValidationError("Registry must be a dictionary")

    if 'projects' not in registry:
        raise ValidationError("Registry missing 'projects' field")

    if not isinstance(registry['projects'], list):
        raise ValidationError("'projects' must be a list")

    # Validate each project
    for i, project in enumerate(registry['projects']):
        if not isinstance(project, dict):
            raise ValidationError(f"Project {i} must be a dictionary")

        required_fields = ['path', 'name']
        for field in required_fields:
            if field not in project:
                raise ValidationError(f"Project {i} missing required field: {field}")

    # Validate groups if present
    if 'groups' in registry:
        if not isinstance(registry['groups'], dict):
            raise ValidationError("'groups' must be a dictionary")

        for group_name, group_data in registry['groups'].items():
            if not isinstance(group_data, dict):
                raise ValidationError(f"Group '{group_name}' must be a dictionary")

            if 'spokes' not in group_data:
                raise ValidationError(f"Group '{group_name}' missing 'spokes' field")

            if not isinstance(group_data['spokes'], list):
                raise ValidationError(f"Group '{group_name}' 'spokes' must be a list")


def add_project(
    hub_path: Path,
    project_path: Path,
    name: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add project to registry.

    Args:
        hub_path: Path to hub directory
        project_path: Path to project (spoke)
        name: Project name
        description: Optional project description

    Returns:
        Updated registry

    Raises:
        RegistryError: If project already exists or add fails
        ValidationError: If inputs are invalid

    Examples:
        >>> add_project(
        ...     Path("/home/user/hub"),
        ...     Path("/home/user/projects/myapp"),
        ...     "myapp",
        ...     "My application"
        ... )
    """
    # Validate inputs
    if not name or not name.strip():
        raise ValidationError("Project name cannot be empty")

    if not project_path.exists():
        raise PathNotFoundError(f"Project path does not exist: {project_path}")

    # Load registry
    registry = load_registry(hub_path)

    # Check if project already exists
    project_path_str = str(project_path.resolve())
    for project in registry['projects']:
        if project['path'] == project_path_str:
            raise RegistryError(f"Project already registered: {project_path}")

        if project['name'] == name:
            raise RegistryError(f"Project with name '{name}' already exists")

    # Add project
    new_project = {
        'path': project_path_str,
        'name': name.strip(),
        'added_at': datetime.now().isoformat()
    }

    if description:
        new_project['description'] = description.strip()

    registry['projects'].append(new_project)

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def remove_project(
    hub_path: Path,
    project_identifier: str
) -> Dict[str, Any]:
    """
    Remove project from registry by name or path.

    Args:
        hub_path: Path to hub directory
        project_identifier: Project name or path

    Returns:
        Updated registry

    Raises:
        RegistryError: If project not found

    Examples:
        >>> remove_project(Path("/home/user/hub"), "myapp")
        >>> remove_project(Path("/home/user/hub"), "/home/user/projects/myapp")
    """
    # Load registry
    registry = load_registry(hub_path)

    # Find project by name or path
    project_index = None
    for i, project in enumerate(registry['projects']):
        if project['name'] == project_identifier or project['path'] == project_identifier:
            project_index = i
            break

    if project_index is None:
        raise RegistryError(f"Project not found: {project_identifier}")

    # Remove project
    removed_project = registry['projects'].pop(project_index)

    # Remove from all groups
    removed_path = removed_project['path']
    for group_name, group_data in registry.get('groups', {}).items():
        if removed_path in group_data.get('spokes', []):
            group_data['spokes'].remove(removed_path)

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def update_project(
    hub_path: Path,
    project_identifier: str,
    **updates: Any
) -> Dict[str, Any]:
    """
    Update project metadata.

    Args:
        hub_path: Path to hub directory
        project_identifier: Project name or path
        **updates: Fields to update (name, description, etc.)

    Returns:
        Updated registry

    Raises:
        RegistryError: If project not found

    Examples:
        >>> update_project(
        ...     Path("/home/user/hub"),
        ...     "myapp",
        ...     description="Updated description"
        ... )
    """
    # Load registry
    registry = load_registry(hub_path)

    # Find project
    project = None
    for p in registry['projects']:
        if p['name'] == project_identifier or p['path'] == project_identifier:
            project = p
            break

    if project is None:
        raise RegistryError(f"Project not found: {project_identifier}")

    # Apply updates
    for key, value in updates.items():
        if key == 'path':
            # Validate path exists if updating
            path = Path(value)
            if not path.exists():
                raise PathNotFoundError(f"Updated path does not exist: {value}")
            project[key] = str(path.resolve())
        else:
            project[key] = value

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def get_project(
    hub_path: Path,
    project_identifier: str
) -> Optional[Dict[str, Any]]:
    """
    Get project by name or path.

    Args:
        hub_path: Path to hub directory
        project_identifier: Project name or path

    Returns:
        Project dictionary or None if not found

    Examples:
        >>> project = get_project(Path("/home/user/hub"), "myapp")
        {'path': '/home/user/projects/myapp', 'name': 'myapp', ...}
    """
    registry = load_registry(hub_path)

    for project in registry['projects']:
        if project['name'] == project_identifier or project['path'] == project_identifier:
            return project

    return None


def list_projects(
    hub_path: Path,
    group_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all projects, optionally filtered by group.

    Args:
        hub_path: Path to hub directory
        group_filter: Optional group name to filter by

    Returns:
        List of project dictionaries

    Examples:
        >>> projects = list_projects(Path("/home/user/hub"))
        >>> client_projects = list_projects(Path("/home/user/hub"), group_filter="clients")
    """
    registry = load_registry(hub_path)

    if group_filter is None:
        return registry['projects']

    # Filter by group
    group = registry.get('groups', {}).get(group_filter)
    if group is None:
        raise RegistryError(f"Group not found: {group_filter}")

    group_paths = set(group.get('spokes', []))
    return [p for p in registry['projects'] if p['path'] in group_paths]


def create_group(
    hub_path: Path,
    group_name: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new group.

    Args:
        hub_path: Path to hub directory
        group_name: Name of group to create
        description: Optional group description

    Returns:
        Updated registry

    Raises:
        RegistryError: If group already exists

    Examples:
        >>> create_group(
        ...     Path("/home/user/hub"),
        ...     "clients",
        ...     "Client projects"
        ... )
    """
    if not group_name or not group_name.strip():
        raise ValidationError("Group name cannot be empty")

    # Load registry
    registry = load_registry(hub_path)

    # Ensure groups dict exists
    if 'groups' not in registry:
        registry['groups'] = {}

    # Check if group exists
    if group_name in registry['groups']:
        raise RegistryError(f"Group already exists: {group_name}")

    # Create group
    registry['groups'][group_name] = {
        'name': group_name.strip(),
        'spokes': [],
        'created_at': datetime.now().isoformat()
    }

    if description:
        registry['groups'][group_name]['description'] = description.strip()

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def delete_group(
    hub_path: Path,
    group_name: str
) -> Dict[str, Any]:
    """
    Delete a group (projects remain in registry).

    Args:
        hub_path: Path to hub directory
        group_name: Name of group to delete

    Returns:
        Updated registry

    Raises:
        RegistryError: If group not found
    """
    # Load registry
    registry = load_registry(hub_path)

    if 'groups' not in registry or group_name not in registry['groups']:
        raise RegistryError(f"Group not found: {group_name}")

    # Delete group
    del registry['groups'][group_name]

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def add_spoke_to_group(
    hub_path: Path,
    group_name: str,
    spoke_path: Path
) -> Dict[str, Any]:
    """
    Add spoke to group.

    Args:
        hub_path: Path to hub directory
        group_name: Name of group
        spoke_path: Path to spoke project

    Returns:
        Updated registry

    Raises:
        RegistryError: If group not found or spoke not registered
    """
    # Load registry
    registry = load_registry(hub_path)

    # Verify group exists
    if 'groups' not in registry or group_name not in registry['groups']:
        raise RegistryError(f"Group not found: {group_name}")

    # Verify spoke is registered
    spoke_path_str = str(spoke_path.resolve())
    spoke_exists = any(p['path'] == spoke_path_str for p in registry['projects'])

    if not spoke_exists:
        raise RegistryError(f"Spoke not registered: {spoke_path}")

    # Add spoke to group if not already present
    group = registry['groups'][group_name]
    if spoke_path_str not in group['spokes']:
        group['spokes'].append(spoke_path_str)

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def remove_spoke_from_group(
    hub_path: Path,
    group_name: str,
    spoke_path: Path
) -> Dict[str, Any]:
    """
    Remove spoke from group.

    Args:
        hub_path: Path to hub directory
        group_name: Name of group
        spoke_path: Path to spoke project

    Returns:
        Updated registry

    Raises:
        RegistryError: If group not found
    """
    # Load registry
    registry = load_registry(hub_path)

    # Verify group exists
    if 'groups' not in registry or group_name not in registry['groups']:
        raise RegistryError(f"Group not found: {group_name}")

    # Remove spoke from group
    spoke_path_str = str(spoke_path.resolve())
    group = registry['groups'][group_name]

    if spoke_path_str in group['spokes']:
        group['spokes'].remove(spoke_path_str)

    # Save registry
    save_registry(hub_path, registry, backup=True)

    return registry


def list_groups(hub_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    List all groups.

    Args:
        hub_path: Path to hub directory

    Returns:
        Dictionary of groups

    Examples:
        >>> groups = list_groups(Path("/home/user/hub"))
        {'clients': {'name': 'clients', 'spokes': [...], ...}, ...}
    """
    registry = load_registry(hub_path)
    return registry.get('groups', {})
