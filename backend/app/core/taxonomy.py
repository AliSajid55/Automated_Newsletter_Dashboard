"""
Fixed taxonomy constants and Gemini prompt template.
"""

from app.core import ALL_TAGS

GEMINI_PROMPT_TEMPLATE = """You are an Expert Tech Editor. Analyze the article below and return ONLY a valid JSON object. No conversational text, no markdown blocks, no extra explanation.

ARTICLE:
Title: {title}
Content: {content}

RULES:
1. "tags" must be chosen ONLY from this list: {allowed_tags}
2. Pick 3–6 tags that best describe the article's domain.
3. "summary_short" must be <= 300 characters.
4. "bullets" must contain exactly 3 to 6 concise bullet-point highlights.
5. "importance_score" is an integer between 1 and 10 (10 = most important).
6. "sentiment" must be one of: "Positive", "Negative", "Neutral".

OUTPUT FORMAT (return this JSON exactly):
{{
  "tags": [],
  "summary_short": "",
  "bullets": [],
  "importance_score": 0,
  "sentiment": ""
}}"""


def build_gemini_prompt(title: str, content: str) -> str:
    """Build the final prompt string for Gemini."""
    return GEMINI_PROMPT_TEMPLATE.format(
        title=title,
        content=content[:2000],  # Token optimization — truncate long content
        allowed_tags=ALL_TAGS,
    )
