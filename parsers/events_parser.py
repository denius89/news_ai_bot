import hashlib
import logging
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

from utils.clean_text import extract_text as clean_text

BASE_URL = "https://www.investing.com/economic-calendar/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

logger = logging.getLogger("parsers.events")


def parse_importance(cell):
    """Определяем важность по количеству звёзд (1–3)."""
    if not cell:
        return 1
    stars = cell.find_all("i", class_="icon-gray-full-bullish")
    count = len(stars)
    return min(max(count, 1), 3)


def clean_text(el):
    """Возвращает текст или None, если пусто."""
    if not el:
        return None
    text = el.get_text(strip=True)
    return text if text else None


def make_event_id(date_str: str, title: str, country: str) -> str:
    raw = f"{date_str}|{title}|{country}"
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize_datetime(day: datetime.date, time_str: str | None):
    """Преобразует время события в UTC datetime."""
    if not time_str or time_str.lower() in ("all day", "tentative"):
        # событие без времени → начало дня UTC
        return datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)

    try:
        # Обычно формат HH:MM
        dt_local = datetime.strptime(time_str.strip(), "%H:%M")
        dt = datetime.combine(day, dt_local.time()).replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        logger.warning(f"Не удалось распарсить время: {time_str}")
        return datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)


def fetch_investing_events(limit_days: int = 2):
    """
    Парсинг экономического календаря Investing.com.
    Берём события за сегодня + limit_days.
    """
    results = []
    today = datetime.utcnow().date()

    for d in range(limit_days):
        day = today + timedelta(days=d)
        url = f"{BASE_URL}?date={day.strftime('%Y-%m-%d')}"
        logger.info(f"[Investing] Загружаем {url}")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"[Investing] Ошибка {resp.status_code} для {url}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", {"id": "economicCalendarData"})
            if not table:
                logger.warning(f"[Investing] Таблица не найдена на {url}")
                continue

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
                    priority = parse_importance(importance_cell)
                    dt = normalize_datetime(day, time_str)

                    event_id = make_event_id(str(day), title or "", country or "")

                    results.append(
                        {
                            "event_id": event_id,
                            "title": title,
                            "country": country,
                            "datetime": dt.isoformat(),
                            "priority": priority,
                            "source": "investing",
                            "category": "macro",
                        }
                    )
                except Exception as e:
                    logger.error(f"[Investing] Ошибка парсинга строки: {e}")

        except Exception as e:
            logger.error(f"[Investing] Ошибка загрузки {url}: {e}")

    return results
