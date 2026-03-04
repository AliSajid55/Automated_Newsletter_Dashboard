"""
Seed script — populates the sources table with 50 popular tech RSS feeds.
Run: python -m app.seeds.seed_sources
"""

import asyncio
import logging
from app.database import AsyncSessionLocal, engine, Base
from app.models.source import Source

logger = logging.getLogger(__name__)

TECH_RSS_SOURCES = [
    # ── Major Tech News ──
    {"name": "TechCrunch", "rss_url": "https://techcrunch.com/feed/"},
    {"name": "The Verge", "rss_url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Ars Technica", "rss_url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "Wired", "rss_url": "https://www.wired.com/feed/rss"},
    {"name": "MIT Technology Review", "rss_url": "https://www.technologyreview.com/feed/"},
    {"name": "ZDNet", "rss_url": "https://www.zdnet.com/news/rss.xml"},
    {"name": "Engadget", "rss_url": "https://www.engadget.com/rss.xml"},
    {"name": "VentureBeat", "rss_url": "https://venturebeat.com/feed/"},
    {"name": "The Next Web", "rss_url": "https://thenextweb.com/feed/"},
    {"name": "Mashable Tech", "rss_url": "https://mashable.com/feeds/rss/tech"},
    # ── Dev / Engineering ──
    {"name": "Hacker News (Best)", "rss_url": "https://hnrss.org/best"},
    {"name": "Dev.to", "rss_url": "https://dev.to/feed"},
    {"name": "CSS Tricks", "rss_url": "https://css-tricks.com/feed/"},
    {"name": "Smashing Magazine", "rss_url": "https://www.smashingmagazine.com/feed/"},
    {"name": "freeCodeCamp", "rss_url": "https://www.freecodecamp.org/news/rss/"},
    {"name": "A List Apart", "rss_url": "https://alistapart.com/main/feed/"},
    {"name": "GitHub Blog", "rss_url": "https://github.blog/feed/"},
    {"name": "Stack Overflow Blog", "rss_url": "https://stackoverflow.blog/feed/"},
    {"name": "Martin Fowler", "rss_url": "https://martinfowler.com/feed.atom"},
    {"name": "The Pragmatic Engineer", "rss_url": "https://blog.pragmaticengineer.com/rss/"},
    # ── AI / Data ──
    {"name": "Google AI Blog", "rss_url": "https://blog.google/technology/ai/rss/"},
    {"name": "OpenAI Blog", "rss_url": "https://openai.com/blog/rss.xml"},
    {"name": "Towards Data Science", "rss_url": "https://towardsdatascience.com/feed"},
    {"name": "Machine Learning Mastery", "rss_url": "https://machinelearningmastery.com/feed/"},
    {"name": "Analytics Vidhya", "rss_url": "https://www.analyticsvidhya.com/feed/"},
    # ── Cybersecurity ──
    {"name": "Krebs on Security", "rss_url": "https://krebsonsecurity.com/feed/"},
    {"name": "The Hacker News (Security)", "rss_url": "https://feeds.feedburner.com/TheHackersNews"},
    {"name": "Dark Reading", "rss_url": "https://www.darkreading.com/rss.xml"},
    {"name": "Schneier on Security", "rss_url": "https://www.schneier.com/feed/atom/"},
    {"name": "Naked Security (Sophos)", "rss_url": "https://nakedsecurity.sophos.com/feed/"},
    # ── Cloud / DevOps ──
    {"name": "AWS Blog", "rss_url": "https://aws.amazon.com/blogs/aws/feed/"},
    {"name": "Google Cloud Blog", "rss_url": "https://cloud.google.com/blog/feed"},
    {"name": "Azure Blog", "rss_url": "https://azure.microsoft.com/en-us/blog/feed/"},
    {"name": "Kubernetes Blog", "rss_url": "https://kubernetes.io/feed.xml"},
    {"name": "Docker Blog", "rss_url": "https://www.docker.com/blog/feed/"},
    # ── FinTech / Startups ──
    {"name": "Finextra", "rss_url": "https://www.finextra.com/rss/headlines.aspx"},
    {"name": "TechFunding News", "rss_url": "https://techfundingnews.com/feed/"},
    {"name": "Crunchbase News", "rss_url": "https://news.crunchbase.com/feed/"},
    {"name": "SaaStr", "rss_url": "https://www.saastr.com/feed/"},
    {"name": "First Round Review", "rss_url": "https://review.firstround.com/feed.xml"},
    # ── Databases / Infra ──
    {"name": "PostgreSQL News", "rss_url": "https://www.postgresql.org/news.rss"},
    {"name": "MongoDB Blog", "rss_url": "https://www.mongodb.com/blog/rss"},
    {"name": "Redis Blog", "rss_url": "https://redis.io/blog/feed/"},
    {"name": "Cloudflare Blog", "rss_url": "https://blog.cloudflare.com/rss/"},
    {"name": "Netlify Blog", "rss_url": "https://www.netlify.com/blog/rss.xml"},
    # ── General / Misc ──
    {"name": "Lobsters", "rss_url": "https://lobste.rs/rss"},
    {"name": "Slashdot", "rss_url": "https://rss.slashdot.org/Slashdot/slashdotMain"},
    {"name": "InfoQ", "rss_url": "https://feed.infoq.com/"},
    {"name": "DZone", "rss_url": "https://feeds.dzone.com/home"},
    {"name": "IEEE Spectrum", "rss_url": "https://spectrum.ieee.org/feeds/feed.rss"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for src in TECH_RSS_SOURCES:
            existing = await session.execute(
                Source.__table__.select().where(Source.rss_url == src["rss_url"])
            )
            if not existing.first():
                session.add(Source(name=src["name"], rss_url=src["rss_url"], active=True))
        await session.commit()
        logger.info(f"Seeded {len(TECH_RSS_SOURCES)} RSS sources.")


if __name__ == "__main__":
    asyncio.run(seed())
