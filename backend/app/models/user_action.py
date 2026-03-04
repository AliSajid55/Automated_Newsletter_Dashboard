"""
UserAction model — tracks saves (bookmarks) and dismisses (left swipes)
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserAction(Base):
    __tablename__ = "user_actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # "save" or "dismiss"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    article = relationship("Article", back_populates="user_actions")

    def __repr__(self) -> str:
        return f"<UserAction article_id={self.article_id} action='{self.action}'>"
