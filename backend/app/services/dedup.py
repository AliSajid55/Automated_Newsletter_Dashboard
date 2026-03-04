"""
De-duplication Engine — detects duplicate articles via content_hash.

Strategy:
  1. normalized_title = lower(title) + remove punctuation + remove stopwords
  2. content_hash = SHA-256(domain + normalized_title)
  3. Same day + similar title => duplicate
"""

import hashlib
import re
from urllib.parse import urlparse

# Common English stopwords to remove for normalization
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "it", "its", "this",
    "that", "these", "those", "i", "we", "you", "he", "she", "they",
}


def normalize_title(title: str) -> str:
    """
    Lowercase, remove punctuation, remove stopwords.
    """
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)  # Remove punctuation
    words = title.split()
    words = [w for w in words if w not in STOPWORDS]
    return " ".join(words)


def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or ""
    except Exception:
        return ""


def generate_content_hash(title: str, url: str) -> str:
    """
    Generate a unique hash for dedup: SHA-256(domain + normalized_title).
    """
    normalized = normalize_title(title)
    domain = extract_domain(url)
    raw_string = f"{domain}|{normalized}"
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()


def is_duplicate(content_hash: str, existing_hashes: set[str]) -> bool:
    """Check if a content_hash already exists."""
    return content_hash in existing_hashes
