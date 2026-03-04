"""
Celery Tasks — the background workers that fetch, dedup, and analyze articles.

Task Chain:
  1. run_sync_cycle()        → Fetches all active sources, triggers per-source tasks
  2. fetch_and_process_feed() → Fetches RSS, dedup, stores new articles
  3. analyze_with_ai()       → Calls Gemini for tags/summary on a single article
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.config import settings
from app.worker.celery_app import celery_app
from app.models.source import Source
from app.models.article import Article
from app.models.ai_output import AIOutput
from app.services.rss_collector import fetch_rss_feed
from app.services.parser import normalize_entry
from app.services.dedup import generate_content_hash
from app.services.gemini_ai import analyze_article

logger = logging.getLogger(__name__)


def _get_session_factory():
    """
    Create a fresh engine + session factory per task call.
    NullPool ensures no connections are shared across event loops (required for asyncpg + Celery).
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def _run_async(coro):
    """Helper to run async code inside Celery (sync) tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ──────────────────────────────────────────────
# TASK 1: Main Sync Cycle
# ──────────────────────────────────────────────
@celery_app.task(name="app.worker.tasks.run_sync_cycle")
def run_sync_cycle():
    """
    Master task — runs every 2 hours via Celery Beat.
    Fetches all active sources from DB and triggers a per-source fetch.
    """
    logger.info("🔄 Starting feed sync cycle...")
    _run_async(_run_sync_cycle_async())


async def _run_sync_cycle_async():
    async with _get_session_factory()() as session:
        result = await session.execute(
            select(Source).where(Source.active == True)
        )
        sources = result.scalars().all()
        logger.info(f"Found {len(sources)} active sources to sync")

    for source in sources:
        # Dispatch each source as a separate Celery task
        celery_app.send_task(
            "app.worker.tasks.fetch_and_process_feed",
            args=[source.id],
        )


# ──────────────────────────────────────────────
# TASK 2: Fetch & Process a Single Feed
# ──────────────────────────────────────────────
@celery_app.task(name="app.worker.tasks.fetch_and_process_feed", bind=True, max_retries=2)
def fetch_and_process_feed(self, source_id: int):
    """
    Fetches RSS entries for one source, dedup-checks, and stores new articles.
    """
    try:
        _run_async(_fetch_and_process_async(source_id))
    except Exception as exc:
        logger.error(f"Error processing source {source_id}: {exc}")
        self.retry(countdown=60, exc=exc)


async def _fetch_and_process_async(source_id: int):
    async with _get_session_factory()() as session:
        source = await session.get(Source, source_id)
        if not source:
            logger.warning(f"Source {source_id} not found")
            return

        # Fetch RSS
        entries = await fetch_rss_feed(source.rss_url)

        # Get existing hashes AND urls for dedup (url has a unique constraint too)
        result = await session.execute(select(Article.content_hash, Article.url))
        rows = result.fetchall()
        existing_hashes = {row[0] for row in rows}
        existing_urls = {row[1] for row in rows}

        new_count = 0
        new_article_ids = []  # Collect IDs, dispatch AFTER commit

        for raw_entry in entries:
            normalized = normalize_entry(raw_entry)

            if not normalized["title"] or not normalized["url"]:
                continue

            content_hash = generate_content_hash(normalized["title"], normalized["url"])

            # Skip if duplicate by hash OR by url
            if content_hash in existing_hashes or normalized["url"] in existing_urls:
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
            session.add(article)
            await session.flush()  # Get the article.id assigned by DB
            new_article_ids.append(article.id)
            new_count += 1
            existing_hashes.add(content_hash)
            existing_urls.add(normalized["url"])

        # Update last_fetched_at and commit ALL articles first
        source.last_fetched_at = datetime.utcnow()
        await session.commit()

        # Only dispatch AI tasks AFTER articles are fully committed in DB
        for article_id in new_article_ids:
            celery_app.send_task(
                "app.worker.tasks.analyze_with_ai",
                args=[article_id],
            )

        logger.info(f"Source '{source.name}': {new_count} new articles (out of {len(entries)} entries)")


# ──────────────────────────────────────────────
# TASK 3: Analyze Single Article with Gemini AI
# ──────────────────────────────────────────────
@celery_app.task(name="app.worker.tasks.analyze_with_ai", bind=True, max_retries=3)
def analyze_with_ai(self, article_id: int):
    """
    Calls Gemini to generate tags, summary, importance score, sentiment
    for a single article — then stores in ai_outputs table.
    """
    try:
        _run_async(_analyze_with_ai_async(article_id))
    except Exception as exc:
        logger.error(f"AI analysis failed for article {article_id}: {exc}")
        self.retry(countdown=30, exc=exc)


async def _analyze_with_ai_async(article_id: int):
    async with _get_session_factory()() as session:
        article = await session.get(Article, article_id)
        if not article:
            logger.warning(f"Article {article_id} not found for AI analysis")
            return

        # Check if already analyzed
        existing = await session.execute(
            select(AIOutput).where(AIOutput.article_id == article_id)
        )
        if existing.scalar_one_or_none():
            logger.info(f"Article {article_id} already analyzed — skipping")
            return

        # Call Gemini
        content = article.raw_summary or article.title
        ai_result = await analyze_article(article.title, content)

        ai_output = AIOutput(
            article_id=article.id,
            summary_short=ai_result["summary_short"],
            summary_bullets=ai_result["bullets"],
            tags=ai_result["tags"],
            importance_score=ai_result["importance_score"],
            sentiment=ai_result["sentiment"],
            model_name="gemini-2.5-flash",
        )
        session.add(ai_output)
        await session.commit()

        logger.info(f"✅ AI analysis complete for article {article_id}: score={ai_result['importance_score']}, tags={ai_result['tags']}")
