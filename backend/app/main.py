"""
FastAPI application entry point
"""

import logging
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.api.routes import feed, article, tags
from app.api.deps import get_db
from app.models.source import Source
from app.models.article import Article
from app.models.ai_output import AIOutput
from app.services.rss_collector import fetch_rss_feed
from app.services.parser import normalize_entry
from app.services.dedup import generate_content_hash
from app.services.gemini_ai import analyze_article as ai_analyze

logger = logging.getLogger(__name__)

app = FastAPI(
    title="The CTO's Morning Brief",
    description="Automated Tech Newsletter Dashboard — 50 sources, AI-powered summaries, Tinder-style UI",
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(feed.router, tags=["Feed"])
app.include_router(article.router, tags=["Articles"])
app.include_router(tags.router, tags=["Tags"])


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "CTO's Morning Brief", "version": "1.0.0"}


@app.post("/sync", tags=["Sync"])
async def manual_sync(
    max_sources: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Manual RSS sync — fetches feeds from active sources directly (no Celery needed).
    Useful for development and initial data population.
    """
    # Get active sources
    result = await db.execute(
        select(Source).where(Source.active == True).limit(max_sources)
    )
    sources = result.scalars().all()

    # Get existing hashes for dedup
    hash_result = await db.execute(select(Article.content_hash))
    existing_hashes = {row[0] for row in hash_result.fetchall()}

    total_new = 0
    errors = []

    for source in sources:
        try:
            entries = await fetch_rss_feed(source.rss_url)
            source_new = 0

            for raw_entry in entries:
                normalized = normalize_entry(raw_entry)

                if not normalized["title"] or not normalized["url"]:
                    continue

                content_hash = generate_content_hash(normalized["title"], normalized["url"])

                if content_hash in existing_hashes:
                    continue

                article = Article(
                    source_id=source.id,
                    title=normalized["title"],
                    url=normalized["url"],
                    published_at=normalized["published_at"],
                    author=normalized["author"],
                    raw_summary=normalized["raw_summary"],
                    content_hash=content_hash,
                )
                db.add(article)
                try:
                    await db.flush()
                except IntegrityError:
                    await db.rollback()
                    continue
                existing_hashes.add(content_hash)
                source_new += 1

            source.last_fetched_at = datetime.utcnow()
            total_new += source_new
            logger.info(f"Source '{source.name}': {source_new} new articles")

        except Exception as e:
            errors.append({"source": source.name, "error": str(e)})
            logger.error(f"Failed to fetch {source.name}: {e}")

    await db.commit()

    return {
        "status": "ok",
        "sources_processed": len(sources),
        "new_articles": total_new,
        "errors": errors,
    }


@app.post("/analyze", tags=["AI"])
async def analyze_articles(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze un-processed articles with Gemini AI.
    Picks articles that don't have an AI output yet.
    """
    subq = select(AIOutput.article_id).scalar_subquery()
    query = (
        select(Article)
        .where(Article.id.notin_(subq))
        .order_by(Article.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    articles = result.scalars().all()

    analyzed = 0
    errors = []

    for art in articles:
        try:
            content = art.raw_summary or art.title
            ai_result = await ai_analyze(art.title, content)

            ai_output = AIOutput(
                article_id=art.id,
                summary_short=ai_result["summary_short"],
                summary_bullets=ai_result["bullets"],
                tags=ai_result["tags"],
                importance_score=ai_result["importance_score"],
                sentiment=ai_result["sentiment"],
                model_name="gemini-2.5-flash",
            )
            db.add(ai_output)
            await db.flush()
            analyzed += 1
            logger.info(f"Analyzed article {art.id}: score={ai_result['importance_score']}")
        except Exception as e:
            errors.append({"article_id": art.id, "error": str(e)})
            logger.error(f"AI analysis failed for article {art.id}: {e}")

    await db.commit()

    return {
        "status": "ok",
        "analyzed": analyzed,
        "total_pending": len(articles),
        "errors": errors,
    }
