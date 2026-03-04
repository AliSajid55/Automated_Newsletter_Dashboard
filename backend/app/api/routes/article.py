"""
Article endpoints:
  GET  /article/{id}        — full detail + AI summary
  POST /article/{id}/save   — bookmark
  POST /article/{id}/dismiss — left-swipe dismiss
  POST /article/{id}/undo   — undo last dismiss
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.article import Article
from app.models.user_action import UserAction
from app.schemas.article import ArticleDetail, AIOutputFull

router = APIRouter()


@router.get("/article/{article_id}", response_model=ArticleDetail)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Full article detail with AI summary, bullets, tags."""
    query = (
        select(Article)
        .options(
            selectinload(Article.ai_output),
            selectinload(Article.user_actions),
            selectinload(Article.source),
        )
        .where(Article.id == article_id)
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    saved = any(ua.action == "save" for ua in article.user_actions)

    ai_full = None
    if article.ai_output:
        ai_full = AIOutputFull(
            tags=article.ai_output.tags,
            importance_score=article.ai_output.importance_score,
            sentiment=article.ai_output.sentiment,
            summary_short=article.ai_output.summary_short,
            summary_bullets=article.ai_output.summary_bullets,
            model_name=article.ai_output.model_name,
            generated_at=article.ai_output.generated_at,
        )

    return ArticleDetail(
        id=article.id,
        title=article.title,
        url=article.url,
        source_name=article.source.name if article.source else "Unknown",
        author=article.author,
        published_at=article.published_at,
        raw_summary=article.raw_summary,
        ai=ai_full,
        is_saved=saved,
    )


@router.post("/article/{article_id}/save")
async def save_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Bookmark an article (right swipe / save button)."""
    # Verify article exists
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if already saved
    existing = await db.execute(
        select(UserAction).where(
            UserAction.article_id == article_id,
            UserAction.action == "save",
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already saved"}

    action = UserAction(article_id=article_id, action="save")
    db.add(action)
    await db.commit()
    return {"message": "Article saved", "article_id": article_id}


@router.post("/article/{article_id}/dismiss")
async def dismiss_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Dismiss an article (left swipe)."""
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    existing = await db.execute(
        select(UserAction).where(
            UserAction.article_id == article_id,
            UserAction.action == "dismiss",
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already dismissed"}

    action = UserAction(article_id=article_id, action="dismiss")
    db.add(action)
    await db.commit()
    return {"message": "Article dismissed", "article_id": article_id}


@router.post("/article/{article_id}/undo")
async def undo_dismiss(article_id: int, db: AsyncSession = Depends(get_db)):
    """Undo dismiss — remove the dismiss action (for the Undo floating button)."""
    existing = await db.execute(
        select(UserAction).where(
            UserAction.article_id == article_id,
            UserAction.action == "dismiss",
        )
    )
    action = existing.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="No dismiss action found to undo")

    await db.delete(action)
    await db.commit()
    return {"message": "Dismiss undone", "article_id": article_id}
