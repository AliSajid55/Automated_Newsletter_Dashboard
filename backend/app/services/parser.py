"""
Parser & Normalizer — cleans raw RSS entry data into a consistent format.
"""

import re
import html


def normalize_entry(raw_entry: dict) -> dict:
    """
    Takes a raw RSS entry dict and returns a cleaned, normalized version.
    """
    return {
        "title": _clean_text(raw_entry.get("title", "")),
        "url": raw_entry.get("link", "").strip(),
        "published_at": raw_entry.get("published"),
        "author": _clean_text(raw_entry.get("author", "")) or None,
        "raw_summary": _strip_html(raw_entry.get("summary", "")),
    }


def _clean_text(text: str) -> str:
    """Remove extra whitespace and HTML entities."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)       # Strip HTML tags
    text = re.sub(r"\s+", " ", text).strip()   # Collapse whitespace
    return text


def _strip_html(text: str) -> str:
    """Strip HTML tags from summary content."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000]  # Truncate for storage
