"""
String manipulation utilities.
"""
import uuid
import random
import string


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}_{unique}"
    return unique


def generate_slug(text: str) -> str:
    """Generate URL-safe slug from text."""
    slug = text.lower().strip()
    slug = slug.replace(" ", "-")
    slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)
    slug = "-".join(slug.split("-"))  # Remove multiple dashes
    return slug


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def pluralize(word: str, count: int) -> str:
    """Simple pluralization."""
    if count == 1:
        return word
    # Very basic - doesn't handle irregular plurals
    if word.endswith("y"):
        return word[:-1] + "ies"
    return word + "s"


def capitalize_words(text: str) -> str:
    """Capitalize first letter of each word."""
    return " ".join(word.capitalize() for word in text.split())


def random_string(length: int = 10) -> str:
    """Generate random alphanumeric string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def is_empty_or_whitespace(text: str) -> bool:
    """Check if string is empty or only whitespace."""
    return not text or not text.strip()
