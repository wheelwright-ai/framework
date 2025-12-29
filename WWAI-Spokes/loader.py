"""
Spoke Loader

Discovers and loads available spokes.
"""

from pathlib import Path
from typing import Dict, Type, Optional, List
from .base import BaseSpoke


# Registry of available spokes
SPOKE_REGISTRY: Dict[str, Type[BaseSpoke]] = {}


def register_spoke(spoke_class: Type[BaseSpoke]) -> Type[BaseSpoke]:
    """
    Decorator to register a spoke class.

    Usage:
        @register_spoke
        class MySpoke(BaseSpoke):
            ...
    """
    # Create a temporary instance to get the name
    # This is a bit hacky but works for registration
    try:
        name = spoke_class.__dict__.get('name', None)
        if name is None:
            # Try to instantiate briefly
            temp = object.__new__(spoke_class)
            name = temp.name if hasattr(temp, 'name') else spoke_class.__name__.lower()
    except:
        name = spoke_class.__name__.lower().replace('spoke', '')

    SPOKE_REGISTRY[name] = spoke_class
    return spoke_class


def load_builtin_spokes() -> None:
    """Load all built-in spokes."""
    from .meta_consultation import MetaConsultationSpoke
    from .document_analysis import DocumentAnalysisSpoke
    from .code_review import CodeReviewSpoke

    SPOKE_REGISTRY['meta-consultation'] = MetaConsultationSpoke
    SPOKE_REGISTRY['document-analysis'] = DocumentAnalysisSpoke
    SPOKE_REGISTRY['code-review'] = CodeReviewSpoke


def get_spoke(name: str) -> Optional[Type[BaseSpoke]]:
    """
    Get a spoke class by name.

    Args:
        name: The spoke name

    Returns:
        The spoke class or None if not found
    """
    if not SPOKE_REGISTRY:
        load_builtin_spokes()
    return SPOKE_REGISTRY.get(name)


def list_spokes() -> List[Dict[str, str]]:
    """
    List all available spokes.

    Returns:
        List of dicts with name and description
    """
    if not SPOKE_REGISTRY:
        load_builtin_spokes()

    result = []
    for name, spoke_class in SPOKE_REGISTRY.items():
        try:
            # Get description from class
            desc = getattr(spoke_class, 'description', 'No description')
            if callable(desc):
                temp = object.__new__(spoke_class)
                desc = temp.description
            result.append({
                'name': name,
                'description': desc
            })
        except:
            result.append({
                'name': name,
                'description': 'No description'
            })

    return result


def instantiate_spoke(name: str, wheel_path: Path, config: Optional[dict] = None) -> Optional[BaseSpoke]:
    """
    Create a spoke instance.

    Args:
        name: The spoke name
        wheel_path: Path to the wheel's .wwai directory
        config: Optional spoke configuration

    Returns:
        Spoke instance or None if not found
    """
    spoke_class = get_spoke(name)
    if spoke_class:
        return spoke_class(wheel_path, config)
    return None
