"""
Модель данных для событий.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EventItem(BaseModel):
    """
    Pydantic-модель для события календаря.
    """

    event_id: Optional[str]
    event_time: datetime
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
