import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import logging

BASE_URL = "https://www.investing.com/economic-calendar/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}


def parse_importance(cell):
    """Определяем важность по количеству звёзд"""
    if not cell:
        return 1  # минимальная важность
    stars = cell.find_all("i", class_="icon-gray-full-bullish")
    count = len(stars)
    if count < 1:
        return 1
    if count > 3:
        return 3
    return count


def clean_text(el):
    """Возвращает текст или None, если пусто"""
    if not el:
        return None
    text = el.get_text(strip=True)
    return text if text else None


def fetch_investing_events(limit_days: int = 2):
    """
    Парсинг экономического календаря Investing.com.
    Берём события за сегодня + limit_days.
    """
    results = []
    try:
        today = datetime.utcnow().date()
        for d in range(limit_days):
            day = today + timedelta(days=d)
            url = f"{BASE_URL}?date={day.strftime('%Y-%m-%d')}"
            logging.info(f"[Investing] Загружаем {url}")

            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                logging.warning(f"[Investing] Ошибка {resp.status_code} для {url}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", {"id": "economicCalendarData"})
            if not table:
                logging.warning(f"[Investing] Таблица не найдена на {url}")
                continue

            for row in table.find_all("tr", class_="js-event-item"):
                try:
                    time_cell = row.find("td", class_="time")
                    country_cell = row.find("td", class_="flagCur")
                    country_span = country_cell.find("span") if country_cell else None

                    event_cell = row.find("td", class_="event")
                    imp_cell = row.find("td", class_="sentiment")
                    actual_cell = row.find("td", class_="actual")
                    forecast_cell = row.find("td", class_="forecast")
                    previous_cell = row.find("td", class_="previous")

                    # Время (UTC)
                    event_time_str = time_cell.get_text(strip=True) if time_cell else ""
                    if not event_time_str or event_time_str.lower() in ("all day", "tentative"):
                        event_time = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
                    else:
                        try:
                            event_time = datetime.strptime(
                                f"{day} {event_time_str}", "%Y-%m-%d %H:%M"
                            ).replace(tzinfo=timezone.utc)
                        except ValueError:
                            event_time = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)

                    importance = parse_importance(imp_cell)

                    results.append({
                        "event_time": event_time.isoformat(),
                        "country": country_span.get("title", "").lower() if country_span else None,
                        "currency": clean_text(country_cell),
                        "title": clean_text(event_cell) or "",
                        "importance": importance,
                        "fact": clean_text(actual_cell),
                        "forecast": clean_text(forecast_cell),
                        "previous": clean_text(previous_cell),
                    })
                except Exception as e:
                    logging.error(f"[Investing] Ошибка парсинга строки: {e}")

    except Exception as e:
        logging.error(f"[Investing] Ошибка: {e}")

    return results