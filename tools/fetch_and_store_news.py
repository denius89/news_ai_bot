import logging

from database.db_models import enrich_news_with_ai, upsert_news
from parsers.rss_parser import fetch_rss, load_sources

logger = logging.getLogger("main")


def main():
    # 1. Загружаем список источников
    sources = load_sources()
    logger.info(f"Загружено {len(sources)} источников")

    # 2. Парсим RSS
    items = fetch_rss(sources, per_source_limit=10)  # ограничим, чтобы не тянуть слишком много
    logger.info(f"Получено {len(items)} новостей")

    if not items:
        logger.warning("Новости не получены, завершаем работу")
        return

    # 3. Дополняем AI-аннотацией
    enriched = [enrich_news_with_ai(item) for item in items]

    # 4. Сохраняем в БД
    upsert_news(enriched)
    logger.info("✅ Пайплайн завершён")


if __name__ == "__main__":
    main()
