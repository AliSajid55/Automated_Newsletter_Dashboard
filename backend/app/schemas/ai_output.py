"""
AI Output schema
"""

from datetime import datetime
from pydantic import BaseModel


class AIOutputOut(BaseModel):
    id: int
    article_id: int
    summary_short: str
    summary_bullets: list[str]
    tags: list[str]
    importance_score: int
    sentiment: str
    model_name: str
    generated_at: datetime

    class Config:
        from_attributes = True
