import logging

from database.db_models import upsert_event
from parsers.events_parser import fetch_investing_events

# --- Базовое логирование ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def main():
    # 1. Получаем события с Investing (сегодня + 1 день)
    events = fetch_investing_events(limit_days=1)
    logger.info(f"Получено {len(events)} событий")

    # 2. Записываем в Supabase
    if events:
        upsert_event(events)
    else:
        logger.warning("События не получены, ничего не вставлено")


if __name__ == "__main__":
    main()
