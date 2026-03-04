"""
GET /tags — all tags with article counts (for the filter sidebar).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.tag import TagCount

router = APIRouter()


@router.get("/tags", response_model=list[TagCount])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """
    Returns each tag and its article count.
    Uses a raw SQL query to unnest the JSON tags array.
    """
    query = text("""
        SELECT tag, COUNT(*) as count
        FROM ai_outputs, jsonb_array_elements_text(tags) AS tag
        GROUP BY tag
        ORDER BY count DESC
    """)
    result = await db.execute(query)
    rows = result.fetchall()
    return [TagCount(tag=row[0], count=row[1]) for row in rows]
