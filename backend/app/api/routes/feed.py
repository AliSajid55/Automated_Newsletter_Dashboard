"""
GET /feed — paginated news cards for the swipe interface.
Uses cursor-based pagination (opaque base64 cursor) for stable sequencing.
Sort order: importance_score DESC NULLS LAST, published_at DESC NULLS LAST, id DESC
Cursor encodes (importance_score, published_at, id) of the last returned item.
"""

import base64
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, case, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.article import Article
from app.models.ai_output import AIOutput
from app.models.user_action import UserAction
from app.schemas.article import ArticleCard, AIOutputBrief, FeedResponse

router = APIRouter()


def _encode_cursor(importance_score, published_at, article_id: int) -> str:
    """Encode (importance_score, published_at, id) as an opaque base64 cursor."""
    data = {
        "s": importance_score,
        "p": published_at.isoformat() if published_at else None,
        "i": article_id,
    }
    return base64.b64encode(json.dumps(data, separators=(",", ":")).encode()).decode()


def _decode_cursor(cursor: str) -> dict | None:
    """Decode opaque cursor, returns None on invalid input."""
    try:
        return json.loads(base64.b64decode(cursor.encode()).decode())
    except Exception:
        return None


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    tag: str | None = Query(None, description="Filter by tag"),
    cursor: str | None = Query(None, description="Opaque pagination cursor from previous response"),
    limit: int = Query(15, ge=1, le=50, description="Number of cards to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns paginated news cards sorted by importance_score DESC, published_at DESC, id DESC.
    Uses tuple cursor (importance_score, published_at, id) — no duplicates, no skips.
    Articles without AI output are still included (outerjoin).
    """
    query = (
        select(Article)
        .options(
            selectinload(Article.ai_output),
            selectinload(Article.user_actions),
            selectinload(Article.source),
        )
        .outerjoin(AIOutput, Article.id == AIOutput.article_id)
    )

    # ── Tuple cursor pagination ──
    # Sort: importance_score DESC NULLS LAST, published_at DESC NULLS LAST, id DESC
    # NULL importance_score is treated as -1 (comes last, same as NULLS LAST)
    if cursor:
        cur = _decode_cursor(cursor)
        if cur:
            c_score = cur["s"]          # int or None
            c_pub_str = cur["p"]        # ISO string or None
            c_id = cur["i"]             # int
            c_pub = datetime.fromisoformat(c_pub_str) if c_pub_str else None

            # Normalize NULL score to -1 (NULLS LAST means NULL = lowest priority)
            score_col = case((AIOutput.importance_score.is_(None), -1), else_=AIOutput.importance_score)
            c_score_norm = c_score if c_score is not None else -1

            if c_pub is not None:
                cursor_filter = or_(
                    score_col < c_score_norm,
                    and_(score_col == c_score_norm, Article.published_at < c_pub),
                    and_(score_col == c_score_norm, Article.published_at == c_pub, Article.id < c_id),
                )
            else:
                # cursor's published_at is NULL — only id tiebreak remains
                cursor_filter = or_(
                    score_col < c_score_norm,
                    and_(score_col == c_score_norm, Article.published_at.is_(None), Article.id < c_id),
                )
            query = query.where(cursor_filter)

    # ── Tag filter (JSONB @> operator) ──
    if tag:
        query = query.where(AIOutput.tags.contains([tag]))

    # ── Exclude dismissed articles ──
    dismissed_subq = (
        select(UserAction.article_id)
        .where(UserAction.action == "dismiss")
        .scalar_subquery()
    )
    query = query.where(Article.id.notin_(dismissed_subq))

    # ── Sorting: importance first (nulls last), then newest, then id for determinism ──
    query = query.order_by(
        AIOutput.importance_score.desc().nulls_last(),
        Article.published_at.desc().nulls_last(),
        Article.id.desc(),
    ).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()

    cards = []
    for art in articles:
        saved = any(ua.action == "save" for ua in art.user_actions)
        dismissed = any(ua.action == "dismiss" for ua in art.user_actions)

        ai_brief = None
        if art.ai_output:
            ai_brief = AIOutputBrief(
                tags=art.ai_output.tags,
                importance_score=art.ai_output.importance_score,
                sentiment=art.ai_output.sentiment,
                summary_short=art.ai_output.summary_short,
            )

        cards.append(ArticleCard(
            id=art.id,
            title=art.title,
            url=art.url,
            source_name=art.source.name if art.source else "Unknown",
            published_at=art.published_at,
            ai=ai_brief,
            is_saved=saved,
            is_dismissed=dismissed,
        ))

    # ── Build next_cursor from last item ──
    next_cursor = None
    if len(articles) == limit:
        last = articles[-1]
        last_score = last.ai_output.importance_score if last.ai_output else None
        next_cursor = _encode_cursor(last_score, last.published_at, last.id)

    return FeedResponse(items=cards, next_cursor=next_cursor)
