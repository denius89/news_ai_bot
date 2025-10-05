#!/usr/bin/env python3
"""
Заполняет AI анализ (importance, credibility) для всех новостей в базе данных.
"""

import sys
import logging
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent.parent))

from database.db_models import supabase, safe_execute
from ai_modules.importance import evaluate_importance
from ai_modules.credibility import evaluate_credibility

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_news_without_ai_analysis():
    """Получает новости без AI анализа."""
    if not supabase:
        logger.error("Supabase не подключен")
        return []

    try:
        # Получаем новости где importance или credibility равны 0 или NULL
        result = safe_execute(
            supabase.table("news")
            .select("id, uid, title, content, source, category, subcategory")
            .or_("importance.is.null,importance.eq.0,credibility.is.null,credibility.eq.0")
            .limit(100)  # Обрабатываем по 100 новостей за раз
        )

        return result.data or []
    except Exception as e:
        logger.error(f"Ошибка получения новостей: {e}")
        return []


def update_news_ai_analysis(news_id: int, importance: float, credibility: float):
    """Обновляет AI анализ для новости."""
    if not supabase:
        return False

    try:
        safe_execute(
            supabase.table("news")
            .update({"importance": importance, "credibility": credibility})
            .eq("id", news_id)
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления новости {news_id}: {e}")
        return False


def analyze_news_ai(news_item):
    """Анализирует новость с помощью AI."""
    try:
        # Оценка важности - передаем весь объект новости
        importance = evaluate_importance(news_item)

        # Оценка достоверности - передаем весь объект новости
        credibility = evaluate_credibility(news_item)

        return importance, credibility

    except Exception as e:
        logger.error(f"Ошибка AI анализа для новости {news_item.get('id')}: {e}")
        return 0.0, 0.0


def main():
    """Основная функция."""
    logger.info("🚀 Начинаем заполнение AI анализа для всех новостей")

    total_processed = 0
    total_updated = 0

    while True:
        # Получаем новости без AI анализа
        news_items = get_news_without_ai_analysis()

        if not news_items:
            logger.info("✅ Все новости обработаны!")
            break

        logger.info(f"📰 Обрабатываем {len(news_items)} новостей...")

        for news_item in news_items:
            try:
                # AI анализ
                importance, credibility = analyze_news_ai(news_item)

                # Обновляем в базе данных
                if update_news_ai_analysis(news_item["id"], importance, credibility):
                    total_updated += 1
                    logger.info(
                        f"✅ {news_item['id']}: importance={importance:.2f}, credibility={credibility:.2f}"
                    )
                else:
                    logger.error(f"❌ Не удалось обновить новость {news_item['id']}")

                total_processed += 1

            except Exception as e:
                logger.error(f"❌ Ошибка обработки новости {news_item.get('id')}: {e}")
                continue

        logger.info(f"📊 Обработано: {total_processed}, обновлено: {total_updated}")

        # Если новостей меньше 100, значит это последняя партия
        if len(news_items) < 100:
            break

    logger.info(f"🎉 Завершено! Всего обработано: {total_processed}, обновлено: {total_updated}")


if __name__ == "__main__":
    main()
