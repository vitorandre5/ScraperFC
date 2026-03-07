"""Name normalization utilities for deduplication."""
import re
import unicodedata
from typing import Optional


def normalize_name(name: str) -> str:
    """
    Normalize a name for deduplication matching.
    
    - Converts to lowercase
    - Removes accents/diacritics
    - Removes special characters
    - Normalizes whitespace
    - Removes common prefixes/suffixes
    
    Args:
        name: Original name string
        
    Returns:
        Normalized canonical name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower()
    
    # Remove accents/diacritics
    normalized = unicodedata.normalize('NFKD', normalized)
    normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
    
    # Remove common team prefixes/suffixes in various languages
    prefixes_suffixes = [
        r'\bfc\b', r'\bcf\b', r'\bsc\b', r'\bac\b', r'\bas\b', r'\bsd\b',
        r'\bclub\b', r'\bclube\b', r'\bdeportivo\b', r'\batletico\b',
        r'\bsporting\b', r'\bunited\b', r'\bcity\b', r'\btown\b',
        r'\breal\b', r'\bsociety\b', r'\bsociedad\b'
    ]
    for pattern in prefixes_suffixes:
        normalized = re.sub(pattern, '', normalized)
    
    # Remove special characters, keep only alphanumeric and spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    
    # Normalize whitespace
    normalized = ' '.join(normalized.split())
    
    # Trim
    normalized = normalized.strip()
    
    return normalized


def normalize_league_name(league: str, country: Optional[str] = None) -> str:
    """
    Normalize league name with country context.
    
    Args:
        league: League name
        country: Country name (optional)
        
    Returns:
        Normalized canonical league name
    """
    canonical = normalize_name(league)
    
    if country:
        country_norm = normalize_name(country)
        canonical = f"{country_norm}_{canonical}"
    
    return canonical


def normalize_team_name(team: str) -> str:
    """Normalize team name for matching."""
    return normalize_name(team)


def similarity_score(name1: str, name2: str) -> float:
    """
    Calculate simple similarity score between two normalized names.
    
    Args:
        name1: First name (normalized)
        name2: Second name (normalized)
        
    Returns:
        Similarity score between 0 and 1
    """
    if not name1 or not name2:
        return 0.0
    
    if name1 == name2:
        return 1.0
    
    # Simple Jaccard similarity on words
    words1 = set(name1.split())
    words2 = set(name2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)
