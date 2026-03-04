"""
AIOutput model — Gemini-generated summaries, tags, scores
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIOutput(Base):
    __tablename__ = "ai_outputs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), unique=True, nullable=False)
    summary_short: Mapped[str] = mapped_column(Text, nullable=False)           # max 300 chars
    summary_bullets: Mapped[list] = mapped_column(JSONB, nullable=False)        # JSONB array of strings
    tags: Mapped[list] = mapped_column(JSONB, nullable=False)                   # JSONB array of tag strings
    importance_score: Mapped[int] = mapped_column(Integer, default=5)           # 1-10
    sentiment: Mapped[str] = mapped_column(String(20), default="Neutral")       # Positive / Negative / Neutral
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-pro")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    article = relationship("Article", back_populates="ai_output")

    def __repr__(self) -> str:
        return f"<AIOutput article_id={self.article_id} score={self.importance_score}>"
