"""
Article model — normalized news articles
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source = relationship("Source", back_populates="articles")
    ai_output = relationship("AIOutput", back_populates="article", uselist=False, lazy="selectin")
    user_actions = relationship("UserAction", back_populates="article", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Article id={self.id} title='{self.title[:50]}'>"
