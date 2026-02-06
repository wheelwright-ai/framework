"""
Password hashing and verification utilities.
Uses bcrypt for secure password storage.
"""
import hashlib
import secrets
from typing import Tuple


class PasswordManager:
    """Manages password hashing and verification."""

    SALT_LENGTH = 32
    ITERATIONS = 100000

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using PBKDF2.
        Returns: salt$hash in hex format
        """
        salt = secrets.token_hex(PasswordManager.SALT_LENGTH // 2)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            PasswordManager.ITERATIONS
        )
        password_hash = hash_obj.hex()
        return f"{salt}${password_hash}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        """
        try:
            salt, stored_hash = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                PasswordManager.ITERATIONS
            )
            return hash_obj.hex() == stored_hash
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def generate_temp_password(length: int = 16) -> str:
        """Generate a temporary password."""
        return secrets.token_urlsafe(length)
