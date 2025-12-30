"""
WAI CLI Exception Hierarchy

Custom exceptions for Wheelwright Framework CLI operations.
"""


class WAIError(Exception):
    """Base exception for all WAI errors."""
    pass


class PathNotFoundError(WAIError):
    """Path does not exist or is not accessible."""
    pass


class InvalidHubError(WAIError):
    """Invalid hub structure or configuration."""
    pass


class SpokeAlreadyExistsError(WAIError):
    """Spoke already initialized at this location."""
    pass


class RegistryError(WAIError):
    """Registry manipulation error."""
    pass


class GroupError(WAIError):
    """Group operation error."""
    pass


class ValidationError(WAIError):
    """Input validation error."""
    pass


class UpgradeError(WAIError):
    """Spoke structure upgrade error."""
    pass
