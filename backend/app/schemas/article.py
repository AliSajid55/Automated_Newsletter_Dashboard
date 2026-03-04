"""
Article schemas — Card (list) and Detail (single) views
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AIOutputBrief(BaseModel):
    """Minimal AI data shown on the swipe card."""
    model_config = ConfigDict(from_attributes=True)

    tags: list[str] = []
    importance_score: int = 5
    sentiment: str = "Neutral"
    summary_short: str = ""


class AIOutputFull(AIOutputBrief):
    """Full AI data shown in the detail modal."""
    summary_bullets: list[str] = []
    model_name: str = ""
    generated_at: datetime | None = None


class ArticleCard(BaseModel):
    """Shown in the Tinder-style card stack."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    source_name: str
    published_at: datetime | None = None
    ai: AIOutputBrief | None = None
    is_saved: bool = False
    is_dismissed: bool = False


class ArticleDetail(BaseModel):
    """Shown when user taps a card — full summary view."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    source_name: str
    author: str | None = None
    published_at: datetime | None = None
    raw_summary: str | None = None
    ai: AIOutputFull | None = None
    is_saved: bool = False


class FeedResponse(BaseModel):
    """Paginated feed response with opaque cursor for next page."""
    items: list[ArticleCard]
    next_cursor: str | None = None
