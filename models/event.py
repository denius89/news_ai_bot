"""
Модель данных для событий.
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
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


class EventItem(BaseModel):
    """
    Pydantic-модель для события календаря.
    """

    event_id: Optional[str]
    event_time: Optional[datetime] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    currency: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=512)
    importance: Optional[int] = 0
    priority: Optional[str] = None
    fact: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("event_time", mode="before")
    @classmethod
    def _coerce_event_time(cls, v):
        return _parse_iso8601(v)

    @property
    def event_time_fmt(self) -> Optional[str]:
        if not self.event_time:
            return "—"
        try:
            return self.event_time.strftime("%d %b %Y, %H:%M")
        except Exception:
            return "—"


__all__ = ["EventItem"]
