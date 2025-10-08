import hashlib
import logging
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

from utils.text.clean_text import extract_text as clean_text

BASE_URL = "https://www.investing.com/economic-calendar/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

logger = logging.getLogger("parsers.events")


# --- Importance → Priority ---
IMPORTANCE_TO_PRIORITY = {
    1: "low",
    2: "medium",
    3: "high",
}


def parse_importance(cell) -> tuple[int, str]:
    """
    Определяем важность по количеству звёзд (1–3).
    Возвращает кортеж: (importance, priority).
    """
    if not cell:
        return 1, "low"

    stars = cell.find_all("i", class_="icon-gray-full-bullish")
    count = len(stars)
    importance = min(max(count, 1), 3)
    return importance, IMPORTANCE_TO_PRIORITY[importance]


def make_event_id(event_time: str, title: str, country: str) -> str:
    """
    Строим уникальный event_id из времени, названия и страны.
    """
    raw = f"{event_time}|{title}|{country}"
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize_datetime(day: datetime.date, time_str: str | None):
    """
    Преобразует время события в UTC datetime.
    Если время отсутствует/«all day»/«tentative»/«n/a» → возвращаем начало дня.
    """
    if not time_str or time_str.lower() in ("all day", "tentative", "n/a"):
        return datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)

    try:
        dt_local = datetime.strptime(time_str.strip(), "%H:%M")
        return datetime.combine(day, dt_local.time()).replace(tzinfo=timezone.utc)
    except Exception:
        logger.warning(f"⚠️ Не удалось распарсить время: {time_str}")
        return datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)


def fetch_investing_events(limit_days: int = 2):
    """
    Парсинг экономического календаря Investing.com.
    Забираем события за сегодня + limit_days.
    Возвращает список словарей событий.
    """
    results = []
    today = datetime.utcnow().date()

    for d in range(limit_days):
        day = today + timedelta(days=d)
        url = f"{BASE_URL}?date={day.strftime('%Y-%m-%d')}"
        logger.info(f"🔄 [Investing] Загружаем {url}")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"⚠️ [Investing] Ошибка {resp.status_code} для {url}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", {"id": "economicCalendarData"})
            if not table:
                logger.warning(f"⚠️ [Investing] Таблица не найдена на {url}")
                continue

            events_before = len(results)
            for row in table.find_all("tr", class_="js-event-item"):
                try:
                    time_cell = row.find("td", class_="time")
                    country_cell = row.find("td", class_="flagCur")
                    country_span = country_cell.find("span") if country_cell else None
                    event_cell = row.find("td", class_="event")
                    importance_cell = row.find("td", class_="sentiment")

                    title = clean_text(event_cell)
                    country = clean_text(country_span)
                    time_str = clean_text(time_cell)

                    importance, priority = parse_importance(importance_cell)
                    dt = normalize_datetime(day, time_str)

                    event_id = make_event_id(dt.isoformat(), title or "", country or "")

                    results.append(
                        {
                            "event_id": event_id,
                            "title": title,
                            "country": country,
                            "datetime": dt.isoformat(),
                            "importance": importance,
                            "priority": priority,
                            "fact": clean_text(row.find("td", class_="actual")),
                            "forecast": clean_text(row.find("td", class_="forecast")),
                            "previous": clean_text(row.find("td", class_="previous")),
                            "source": "investing",
                            "category": "markets",
                            "subcategory": "macro",
                        }
                    )
                except Exception as e:
                    logger.error(f"❌ [Investing] Ошибка парсинга строки: {e}", exc_info=True)

            added = len(results) - events_before
            if added > 0:
                logger.info(f"✅ [Investing] {day}: добавлено {added} событий")
            else:
                logger.warning(f"⚠️ [Investing] {day}: событий не найдено")

        except Exception as e:
            logger.error(f"❌ [Investing] Ошибка загрузки {url}: {e}", exc_info=True)

    return results
