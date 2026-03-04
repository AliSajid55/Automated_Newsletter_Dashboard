"""
Tag count schema — used by the filter sidebar
"""

from pydantic import BaseModel


class TagCount(BaseModel):
    tag: str
    count: int
