# utils/dates.py
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, Union
from config.core.settings import TIMEZONE

try:
    # stdlib c Python 3.9+: без внешних зависимостей
    from zoneinfo import ZoneInfo  # type: ignore
except Exception:  # pragma: no cover
    ZoneInfo = None  # fallback на UTC


logger = logging.getLogger("utils.dates")


def _parse_iso(value: Union[str, datetime, None]) -> Optional[datetime]:
    """Пытается распарсить ISO-дату (поддерживает хвост 'Z'). Возвращает aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip()
        if not s:
            return None
        # Поддержка 'Z' → UTC
        s = s.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            logger.debug("Не удалось распарсить дату: %r", value)
            return None

    # делаем aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _to_local(dt: datetime) -> datetime:
    """Переводим в локальную таймзону из настроек, если доступна."""
    try:
        tz = ZoneInfo(TIMEZONE) if ZoneInfo else timezone.utc
    except Exception:
        tz = timezone.utc
    return dt.astimezone(tz)


def format_datetime(value: Union[str, datetime, None], fmt: str = "%d %b %Y, %H:%M") -> str:
    """
    Безопасно форматирует дату:
      - принимает ISO-строку или datetime,
      - переводит в локальную таймзону (TIMEZONE из config),
      - возвращает строку по fmt,
      - если не получилось — '—'.
    """
    dt = _parse_iso(value)
    if not dt:
        return "—"
    return _to_local(dt).strftime(fmt)


def ensure_utc_iso(value: Union[str, datetime, None]) -> Optional[str]:
    """
    Гарантирует ISO-формат в UTC ('...Z').
    Возвращает строку или None, если парсинг невозможен.
    """
    dt = _parse_iso(value)
    if not dt:
        return None
    iso = dt.astimezone(timezone.utc).isoformat()
    # нормализуем '+00:00' → 'Z'
    return iso.replace("+00:00", "Z")
