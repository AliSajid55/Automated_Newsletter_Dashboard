"""
Source schemas
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl


class SourceOut(BaseModel):
    id: int
    name: str
    rss_url: str
    active: bool
    last_fetched_at: datetime | None = None

    class Config:
        from_attributes = True
