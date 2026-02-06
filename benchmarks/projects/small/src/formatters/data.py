"""
Data formatter for processing user input.
Converts raw data into structured format.
"""

class DataFormatter:
    """Formats user data into standardized structure."""

    def __init__(self, config=None):
        self.config = config or {}
        self.strict_mode = self.config.get('strict', False)

    def format(self, data):
        """
        Format raw data dictionary.

        Args:
            data: Dictionary of raw data

        Returns:
            Formatted data dictionary
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        formatted = {}

        # Format name field
        if 'name' in data:
            formatted['name'] = self._format_name(data['name'])

        # Format email field
        if 'email' in data:
            formatted['email'] = self._format_email(data['email'])

        # Format timestamp
        if 'timestamp' in data:
            formatted['timestamp'] = self._format_timestamp(data['timestamp'])

        return formatted

    def _format_name(self, name):
        """Format name field."""
        if not isinstance(name, str):
            return str(name)
        return name.strip().title()

    def _format_email(self, email):
        """Format email field."""
        if not isinstance(email, str):
            raise ValueError("Email must be string")
        email = email.strip().lower()
        if self.strict_mode and '@' not in email:
            raise ValueError("Invalid email format")
        return email

    def _format_timestamp(self, timestamp):
        """Format timestamp field."""
        return int(timestamp) if timestamp else None
