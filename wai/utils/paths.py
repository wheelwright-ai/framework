"""
Cross-Platform Path Utilities

Handles path normalization and validation across Linux, macOS, Windows, and WSL.
"""

import os
import platform
import re
from pathlib import Path, PureWindowsPath, PurePosixPath
from typing import Optional, Tuple, List

from .exceptions import PathNotFoundError, ValidationError


def normalize_path(path_str: str) -> Path:
    """
    Normalize path for current platform.

    Handles:
    - Windows paths on WSL: /mnt/c/... or C:\\...
    - WSL paths on Windows: \\\\wsl$\\Ubuntu\\...
    - Tilde expansion
    - Relative paths
    - Forward/backslash conversion
    
    Note: These conversions use [DEFER] operations

    Args:
        path_str: Path string to normalize

    Returns:
        Resolved absolute Path

    Examples:
        >>> normalize_path("~/projects")
        PosixPath('/home/user/projects')

        >>> normalize_path("C:\\Users\\mario")  # On WSL
        PosixPath('/mnt/c/Users/mario')
    """
    path_str = path_str.strip()

    if not path_str:
        raise ValidationError("Path cannot be empty")

    # Detect WSL environment
    is_wsl = _is_wsl()

    # Handle Windows drive letters in WSL
    if is_wsl and re.match(r'^[A-Za-z]:[/\\]', path_str):
        # C:\path or C:/path [DEFER] /mnt/c/path
        drive = path_str[0].lower()
        rest = path_str[2:].replace('\\', '/')
        path_str = f'/mnt/{drive}{rest}'

    # Handle WSL paths on Windows
    if platform.system() == 'Windows' and path_str.startswith('\\\\wsl'):
        # \\wsl$\Ubuntu\path [DEFER] keep as-is, Windows can handle
        pass

    # Expand user home and resolve
    try:
        path = Path(path_str).expanduser().resolve()
        return path
    except (OSError, RuntimeError) as e:
        raise ValidationError(f"Invalid path '{path_str}': {e}")


def _is_wsl() -> bool:
    """Detect if running in WSL environment."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False


def detect_wsl_windows_path(path: Path) -> Optional[str]:
    """
    Convert WSL path to Windows path if applicable.

    Args:
        path: WSL path

    Returns:
        Windows path string or None

    Examples:
        >>> detect_wsl_windows_path(Path("/mnt/c/Users/mario"))
        'C:\\Users\\mario'

        >>> detect_wsl_windows_path(Path("/home/mario"))
        '\\\\wsl$\\Ubuntu\\home\\mario'
    """
    if not _is_wsl():
        return None

    path_str = str(path)

    # Handle /mnt/c/... [DEFER] C:\...
    mnt_match = re.match(r'^/mnt/([a-z])(/.*)$', path_str)
    if mnt_match:
        drive = mnt_match.group(1).upper()
        rest = mnt_match.group(2).replace('/', '\\')
        return f'{drive}:{rest}'

    # Handle /home/... or other WSL paths [DEFER] \\wsl$\...
    # Detect WSL distro name
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('NAME='):
                    distro = line.split('=')[1].strip().strip('"')
                    if 'Ubuntu' in distro:
                        distro = 'Ubuntu'
                    elif 'Debian' in distro:
                        distro = 'Debian'
                    else:
                        distro = 'Ubuntu'  # Default
                    break
            else:
                distro = 'Ubuntu'
    except:
        distro = 'Ubuntu'

    windows_path = f'\\\\wsl$\\{distro}{path_str.replace("/", "\\")}'
    return windows_path


def is_valid_hub_location(path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate hub location with helpful error messages.

    Checks:
    - Path exists or parent exists (can create)
    - Not inside another hub
    - Not inside a spoke
    - Has write permissions

    Args:
        path: Proposed hub location

    Returns:
        Tuple of (valid: bool, error_message: Optional[str])
    """
    # Check if path exists
    if path.exists():
        if not path.is_dir():
            return False, f"Path exists but is not a directory: {path}"
    else:
        # Check if parent exists (we can create it)
        if not path.parent.exists():
            return False, f"Parent directory does not exist: {path.parent}"

        # Check write permissions on parent
        if not os.access(path.parent, os.W_OK):
            return False, f"No write permission on parent directory: {path.parent}"

    # Check if path is inside another hub
    current = path.parent
    while current != current.parent:  # Stop at root
        if (current / 'hub-profile.json').exists() and (current / 'registry').exists():
            return False, f"Cannot create hub inside another hub: {current}"
        current = current.parent

    # Check if path is inside a spoke
    current = path.parent
    while current != current.parent:
        if (current / 'WAI-Spoke').exists():
            return False, f"Cannot create hub inside a spoke: {current}"
        current = current.parent

    # Check write permissions if path exists
    if path.exists() and not os.access(path, os.W_OK):
        return False, f"No write permission on directory: {path}"

    return True, None


def suggest_hub_locations(framework_path: Optional[Path] = None) -> List[Path]:
    """
    Suggest hub locations based on platform and framework location.

    Args:
        framework_path: Path to framework (for relative ../hub suggestion)

    Returns:
        List of suggested paths (existing ones first, then non-existing)

    Examples:
        >>> suggest_hub_locations(Path("/home/mario/projects/framework"))
        [Path("/home/mario/projects/hub"), Path("/home/mario/wheelwright-hub")]
    """
    suggestions = []

    # Priority 1: ../hub relative to framework
    if framework_path:
        parent_hub = (framework_path.parent / 'hub').resolve()
        suggestions.append(parent_hub)

    # Priority 2: Environment variable
    env_hub = os.environ.get('WHEELWRIGHT_HUB_PATH')
    if env_hub:
        try:
            suggestions.append(normalize_path(env_hub))
        except:
            pass

    # Priority 3: Platform-specific locations
    home = Path.home()

    if platform.system() == 'Windows':
        suggestions.extend([
            home / 'wheelwright-hub',
            home / 'Documents' / 'hub',
            Path('C:/wheelwright-hub') if Path('C:/').exists() else None
        ])
    elif _is_wsl():
        suggestions.extend([
            home / 'wheelwright-hub',
            Path('/mnt/c/Users') / os.environ.get('USER', 'user') / 'wheelwright-hub'
        ])
    else:  # Linux/macOS
        suggestions.extend([
            home / 'wheelwright-hub',
            home / 'projects' / 'hub',
            Path('/opt/wheelwright-hub') if Path('/opt').exists() else None
        ])

    # Filter out None and duplicates
    suggestions = [s for s in suggestions if s is not None]
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)

    # Sort: existing first, then by priority
    existing = [s for s in unique_suggestions if s.exists()]
    non_existing = [s for s in unique_suggestions if not s.exists()]

    return existing + non_existing


def is_same_path(path1: Path, path2: Path) -> bool:
    """
    Check if two paths refer to the same location.

    Handles:
    - Symlinks
    - Case sensitivity on Windows
    - Relative vs absolute paths

    Args:
        path1: First path
        path2: Second path

    Returns:
        True if paths refer to same location
    """
    try:
        return path1.resolve() == path2.resolve()
    except:
        return False


def ensure_directory(path: Path, parents: bool = True, exist_ok: bool = True) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path
        parents: Create parent directories
        exist_ok: Don't raise error if exists

    Returns:
        Path to directory

    Raises:
        PathNotFoundError: If cannot create directory
    """
    try:
        path.mkdir(parents=parents, exist_ok=exist_ok)
        return path
    except PermissionError:
        raise PathNotFoundError(f"Permission denied creating directory: {path}")
    except OSError as e:
        raise PathNotFoundError(f"Cannot create directory {path}: {e}")
