import re
from enum import Enum
from typing import Tuple

class QueryType(Enum):
    HANDLE = "Social Handle (@)"
    DOMAIN = "Web Domain"
    SLUG = "GitHub Slug"
    NAME = "General Project Name"

def classify_input(query: str) -> Tuple[QueryType, str]:
    """
    Classifies the user input to determine the research strategy.
    
    Returns:
        (QueryType, clean_query)
    """
    query = query.strip()
    
    # 1. Detect Social Handle / X URL
    if query.startswith("@"):
        return QueryType.HANDLE, query.replace("@", "")
    
    x_match = re.search(r'(?:x\.com|twitter\.com)/([a-zA-Z0-9_]{1,15})', query.lower())
    if x_match:
        return QueryType.HANDLE, x_match.group(1)
    
    # 2. Detect Domain
    # Pattern: words followed by .io, .xyz, .net, .com, .build, .network, .ai
    if re.search(r'\.[a-z]{2,10}$', query.lower()) and not " " in query:
        return QueryType.DOMAIN, query.lower()
        
    # 3. Detect GitHub Slug (org/repo)
    if re.match(r'^[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+$', query) and not " " in query:
        return QueryType.SLUG, query
        
    # 4. Detect "App/Fi" suffixes as handles
    if any(query.lower().endswith(suffix) for suffix in ["_app", "_fi", "_xyz", "_network"]):
        return QueryType.HANDLE, query
        
    # Default to Name
    return QueryType.NAME, query
