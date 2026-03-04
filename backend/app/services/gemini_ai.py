"""
Gemini AI Integration — generates tags, summaries, importance scores.
Built-in daily call limit to avoid exceeding API quota.
"""

import asyncio
import json
import logging
import re
from datetime import date
from threading import Lock

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.taxonomy import build_gemini_prompt
from app.core import ALL_TAGS, SENTIMENTS

logger = logging.getLogger(__name__)

# ── Daily limit tracker (thread-safe, resets each new day) ──
_counter_lock = Lock()
_call_date: date = date.today()
_call_count: int = 0


def _check_and_increment_limit() -> bool:
    """
    Returns True if a Gemini call is allowed (under daily limit).
    Resets the counter automatically at midnight.
    """
    global _call_date, _call_count
    with _counter_lock:
        today = date.today()
        if today != _call_date:  # New day — reset counter
            _call_date = today
            _call_count = 0
        if _call_count >= settings.GEMINI_DAILY_LIMIT:
            return False
        _call_count += 1
        return True


def _extract_smart_summary(content: str) -> str:
    """
    Extract first 3-4 clean sentences from article content as fallback summary.
    """
    if not content:
        return "Summary unavailable."

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    # Take first 3-4 meaningful sentences (skip very short ones)
    selected = [s.strip() for s in sentences if len(s.strip()) > 30][:4]

    if not selected:
        # Fallback: first 250 chars
        return content.strip()[:250].rstrip() + "..."

    return " ".join(selected)


def _sync_generate(prompt: str) -> str:
    """Synchronous Gemini call — runs in a thread to avoid blocking the event loop."""
    # Configure fresh each call so a rotated API key is always picked up
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1024,
            response_mime_type="application/json",
        ),
    )
    return response.text.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
async def analyze_article(title: str, content: str) -> dict:
    """
    Send article to Gemini and get structured analysis.
    Returns dict with: tags, summary_short, bullets, importance_score, sentiment.
    If daily limit is reached, returns a smart fallback using article content.
    """
    # ── Daily limit check ──
    if not _check_and_increment_limit():
        logger.warning(
            f"Gemini daily limit ({settings.GEMINI_DAILY_LIMIT}) reached. "
            f"Using content-based fallback for: '{title[:60]}'"
        )
        return _content_fallback(content)

    prompt = build_gemini_prompt(title, content)
    raw_text = ""  # ensure defined even if thread raises before assignment

    try:
        raw_text = await asyncio.to_thread(_sync_generate, prompt)

        # Robust JSON extraction — handle markdown fences
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        result = json.loads(raw_text)
        return _validate_and_sanitize(result)

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON for '{title[:50]}': {e}\nRaw: {raw_text[:300]}")
        return _content_fallback(content)
    except Exception as e:
        logger.error(f"Gemini API error for '{title[:50]}': {e}")
        raise


def _validate_and_sanitize(data: dict) -> dict:
    """Validate Gemini output against our taxonomy and constraints."""
    # Filter tags to only allowed ones
    tags = [t for t in data.get("tags", []) if t in ALL_TAGS]
    if not tags:
        tags = ["GeneralTech"]

    # Clamp importance score
    score = data.get("importance_score", 5)
    score = max(1, min(10, int(score)))

    # Validate sentiment
    sentiment = data.get("sentiment", "Neutral")
    if sentiment not in SENTIMENTS:
        sentiment = "Neutral"

    # Truncate summary
    summary = data.get("summary_short", "")[:300]

    # Limit bullets
    bullets = data.get("bullets", [])[:6]

    return {
        "tags": tags,
        "summary_short": summary,
        "bullets": bullets,
        "importance_score": score,
        "sentiment": sentiment,
    }


def _content_fallback(content: str) -> dict:
    """
    Smart fallback when Gemini is skipped (limit hit) or returns invalid JSON.
    Uses first 3-4 sentences of article content as summary.
    """
    summary = _extract_smart_summary(content)
    return {
        "tags": ["GeneralTech"],
        "summary_short": summary,
        "bullets": [summary],
        "importance_score": 5,
        "sentiment": "Neutral",
    }
