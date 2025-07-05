"""
Shared utility functions for the Network Journal application.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from pathlib import Path


def generate_id() -> str:
    """Generate a unique ID for database entities."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get the current timestamp."""
    return datetime.utcnow()


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Set up logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    return dictionary.get(key, default)


def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string for database storage."""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = text.strip()
    
    # Truncate if max_length is specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def format_date_for_display(date: datetime) -> str:
    """Format a date for display in the UI."""
    return date.strftime("%B %d, %Y")


def format_datetime_for_display(dt: datetime) -> str:
    """Format a datetime for display in the UI."""
    return dt.strftime("%B %d, %Y at %I:%M %p")


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (
        today.month == birth_date.month and today.day < birth_date.day
    ):
        age -= 1
    return age


def days_since_last_contact(last_contact_date: datetime) -> int:
    """Calculate days since last contact."""
    if not last_contact_date:
        return float('inf')
    
    today = datetime.now()
    delta = today - last_contact_date
    return delta.days


def normalize_company_name(name: str) -> str:
    """Normalize company name for consistent storage."""
    if not name:
        return ""
    
    # Convert to title case and remove extra whitespace
    normalized = " ".join(name.split()).title()
    
    # Handle common abbreviations
    abbreviations = {
        "Inc": "Inc.",
        "Corp": "Corp.",
        "Ltd": "Ltd.",
        "LLC": "LLC",
        "LLP": "LLP"
    }
    
    for abbr, replacement in abbreviations.items():
        normalized = normalized.replace(f" {abbr} ", f" {replacement} ")
        if normalized.endswith(f" {abbr}"):
            normalized = normalized[:-len(abbr)] + replacement
    
    return normalized


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from a URL."""
    if not url:
        return None
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with dict2 taking precedence."""
    result = dict1.copy()
    result.update(dict2)
    return result 