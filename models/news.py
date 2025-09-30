"""
Модель данных для новостей.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class NewsItem(BaseModel):
    """
    Pydantic-модель для новости.
    Гарантирует наличие title, ограничивает длину и нормализует поля.
    """

    uid: Optional[str]
    title: str = Field(..., min_length=1, max_length=512)
    content: str
    link: Optional[HttpUrl] = None
    source: Optional[str] = None
    category: Optional[str] = None
    published_at: Optional[datetime] = None
    credibility: Optional[float] = None
    importance: Optional[float] = None
