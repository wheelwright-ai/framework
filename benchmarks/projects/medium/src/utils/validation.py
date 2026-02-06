"""
Data validation utilities for common patterns.
"""
import re
from typing import List, Dict, Any


class Validator:
    """Utility class for common validations."""

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?1?\d{9,15}$')
    SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        if not email or len(email) > 254:
            return False
        return bool(Validator.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        return bool(Validator.PHONE_PATTERN.match(phone))

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate URL slug format."""
        if not slug or len(slug) > 100:
            return False
        return bool(Validator.SLUG_PATTERN.match(slug))

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength.
        Returns: {is_strong: bool, messages: List[str]}
        """
        messages = []
        is_strong = True

        if len(password) < 8:
            messages.append("Password must be at least 8 characters")
            is_strong = False

        if not re.search(r'[A-Z]', password):
            messages.append("Password must contain uppercase letter")
            is_strong = False

        if not re.search(r'[a-z]', password):
            messages.append("Password must contain lowercase letter")
            is_strong = False

        if not re.search(r'\d', password):
            messages.append("Password must contain digit")
            is_strong = False

        if not re.search(r'[!@#$%^&*]', password):
            messages.append("Password must contain special character")
            is_strong = False

        return {"is_strong": is_strong, "messages": messages}

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        """
        Validate that required fields are present and non-empty.
        Returns: {valid: bool, errors: Dict[str, str]}
        """
        errors = {}
        for field in required:
            if field not in data or not data[field]:
                errors[field] = f"{field} is required"

        return {"valid": len(errors) == 0, "errors": errors}
