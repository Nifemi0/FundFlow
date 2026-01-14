"""
Utility helper functions for FundFlow.
"""
import re
from typing import Optional


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        Slugified string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    
    return text


def format_number(num: Optional[float], decimals: int = 1) -> str:
    """
    Format number for display (e.g., 1.5M, 10K).
    
    Args:
        num: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if num is None:
        return "N/A"
    
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{decimals}f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def extract_twitter_handle(url_or_handle: str) -> Optional[str]:
    """
    Extract Twitter handle from URL or @ username.
    
    Args:
        url_or_handle: Twitter URL or @username
        
    Returns:
        Clean username without @
    """
    if not url_or_handle:
        return None
    
    # Remove @ if present
    handle = url_or_handle.replace("@", "")
    
    # Extract from URL
    if "twitter.com/" in handle or "x.com/" in handle:
        parts = handle.split("/")
        if parts:
            handle = parts[-1]
    
    # Clean
    handle = handle.strip().lower()
    
    return handle if handle else None


def parse_filter_string(filter_str: str) -> dict:
    """
    Parse filter string into structured filters.
    Example: "sector:defi amount:>5M investor:paradigm"
    
    Args:
        filter_str: Filter string
        
    Returns:
        Dictionary of filters
    """
    filters = {}
    
    # Split by spaces (respecting quotes)
    parts = re.findall(r'(\w+):([^\s]+)', filter_str)
    
    for key, value in parts:
        key = key.lower()
        
        # Handle special operators
        if value.startswith(">"):
            filters[key] = {"operator": ">", "value": parse_amount(value[1:])}
        elif value.startswith("<"):
            filters[key] = {"operator": "<", "value": parse_amount(value[1:])}
        else:
            filters[key] = {"operator": "=", "value": value}
    
    return filters


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string like "5M" or "500K" to float.
    
    Args:
        amount_str: Amount string
        
    Returns:
        Amount as float
    """
    amount_str = amount_str.upper().strip()
    
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    
    for suffix, multiplier in multipliers.items():
        if amount_str.endswith(suffix):
            try:
                number = float(amount_str[:-1])
                return number * multiplier
            except ValueError:
                pass
    
    try:
        return float(amount_str)
    except ValueError:
        return 0.0


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        dictionary: Dictionary to search
        keys: Nested keys
        default: Default value if not found
        
    Returns:
        Value or default
    """
    value = dictionary
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        
        if value is None:
            return default
    
    return value
