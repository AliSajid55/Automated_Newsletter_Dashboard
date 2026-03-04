"""
RSS Collector — fetches feed entries from a given RSS URL.
"""

import logging
from datetime import datetime

import feedparser
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
async def fetch_rss_feed(rss_url: str) -> list[dict]:
    """
    Fetches and parses an RSS feed URL.
    Returns a list of normalized entry dicts.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(rss_url, follow_redirects=True)
            response.raise_for_status()

        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            logger.warning(f"Malformed feed (bozo): {rss_url}")
            return []

        entries = []
        for entry in feed.entries:
            title = entry.get("title") or ""
            link = entry.get("link") or ""
            entries.append({
                "title": str(title).strip(),
                "link": str(link).strip(),
                "published": _parse_date(entry),
                "author": entry.get("author", None),
                "summary": _extract_summary(entry),
            })

        logger.info(f"Fetched {len(entries)} entries from {rss_url}")
        return entries

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {rss_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {rss_url}: {e}")
        raise


def _parse_date(entry) -> datetime | None:
    """Try to parse the published date from common RSS fields."""
    from dateutil import parser as date_parser

    for field in ("published", "updated", "created"):
        raw = entry.get(field)
        if raw:
            try:
                dt = date_parser.parse(raw)
                return dt.replace(tzinfo=None)  # Strip timezone for asyncpg
            except (ValueError, TypeError):
                continue
    return None


def _extract_summary(entry) -> str:
    """Extract the best available summary / content snippet."""
    # Prefer content over summary
    if "content" in entry and entry["content"]:
        return entry["content"][0].get("value", "")[:2000]
    return entry.get("summary", "")[:2000]
