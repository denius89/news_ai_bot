"""
Pydantic-модель для таблицы news.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _parse_iso8601(value: Optional[str | datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # Поддержка 'Z' как UTC
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


class NewsItem(BaseModel):
    """Модель новости из Supabase."""

    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=512)
    content: str
    link: Optional[str] = None
    importance: Optional[float] = None
    credibility: Optional[float] = None
    published_at: Optional[datetime] = None
    source: Optional[str] = None
    category: Optional[str] = None

    @field_validator("published_at", mode="before")
    @classmethod
    def _coerce_published_at(cls, v):
        return _parse_iso8601(v)

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, v):
        if v is None:
            return None
        try:
            return str(v)
        except Exception:
            return None

    @property
    def published_at_fmt(self) -> Optional[str]:
        """
        Форматированная дата публикации для обратной совместимости.
        Использует utils.formatters.format_date.
        """
        from utils.formatters import format_date

        return format_date(self.published_at)

    @property
    def published_at_dt(self) -> Optional[datetime]:
        """
        Совместимый алиас для datetime-представления даты публикации.
        """
        return self.published_at


__all__ = ["NewsItem"]
