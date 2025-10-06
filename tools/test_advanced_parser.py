#!/usr/bin/env python3
"""
Тестовый скрипт для AdvancedParser с ограничением по количеству новостей.

Загружает по 10 новостей для каждой подкатегории и показывает статистику.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.advanced_parser import AdvancedParser
from database.service import get_async_service
from ai_modules.importance import evaluate_importance
from ai_modules.credibility import evaluate_credibility
from utils.clean_text import clean_text
import feedparser

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/test_advanced_parser.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


class TestAdvancedParser(AdvancedParser):
    """Тестовая версия AdvancedParser с ограничениями."""

    def __init__(self, max_news_per_subcategory=10, **kwargs):
        """
        Инициализация тестового парсера.

        Args:
            max_news_per_subcategory: Максимальное количество новостей на подкатегорию
        """
        super().__init__(**kwargs)
        self.max_news_per_subcategory = max_news_per_subcategory
        self.subcategory_counts = {}

    async def _process_rss_source(self, category, subcategory, name, url, content):
        """Обработка RSS источника с ограничением по количеству."""
        try:
            feed = feedparser.parse(content)
            if not feed.entries:
                return {"success": False, "reason": "no_entries"}

            # Проверяем лимит для подкатегории
            if subcategory not in self.subcategory_counts:
                self.subcategory_counts[subcategory] = 0

            if self.subcategory_counts[subcategory] >= self.max_news_per_subcategory:
                logger.info(f"[{category}/{subcategory}] Достигнут лимит {self.max_news_per_subcategory} новостей")
                return {
                    "success": True,
                    "processed": 0,
                    "saved": 0,
                    "type": "rss",
                    "reason": "limit_reached",
                }

            processed_count = 0
            saved_count = 0

            # Ограничиваем количество записей
            max_entries = min(
                len(feed.entries),
                self.max_news_per_subcategory - self.subcategory_counts[subcategory],
            )

            for entry in feed.entries[:max_entries]:
                try:
                    # Извлекаем данные из RSS
                    title = clean_text(entry.get("title", ""))
                    link = entry.get("link", "")
                    summary = clean_text(entry.get("summary", ""))

                    if not title:
                        continue

                    processed_count += 1

                    # Оценка важности и достоверности
                    text_for_ai = f"{title} {summary}".strip()
                    if not text_for_ai:
                        continue

                    importance = evaluate_importance({"title": title, "content": text_for_ai})
                    credibility = evaluate_credibility({"title": title, "content": text_for_ai})

                    if importance < self.min_importance:
                        logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                        continue

                    # Сохраняем в БД
                    news_item = {
                        "title": title,
                        "content": summary,
                        "link": link,
                        "source": name,
                        "category": category,
                        "subcategory": subcategory,
                        "importance": importance,
                        "credibility": credibility,
                    }

                    # Используем асинхронный сервис БД
                    db_service = get_async_service()
                    await db_service.async_upsert_news([news_item])
                    saved_count += 1
                    self.subcategory_counts[subcategory] += 1

                    logger.info(f"[{category}/{subcategory}] {title[:50]}... -> SAVED (importance: {importance:.2f})")

                except Exception as e:
                    logger.error(f"Ошибка обработки RSS записи: {e}")
                    continue

            return {
                "success": True,
                "processed": processed_count,
                "saved": saved_count,
                "type": "rss",
            }

        except Exception as e:
            return {"success": False, "reason": f"rss_parse_error: {e}"}

    async def _process_html_source(self, category, subcategory, name, url, content):
        """Обработка HTML источника с ограничением по количеству."""
        try:
            # Проверяем лимит для подкатегории
            if subcategory not in self.subcategory_counts:
                self.subcategory_counts[subcategory] = 0

            if self.subcategory_counts[subcategory] >= self.max_news_per_subcategory:
                logger.info(f"[{category}/{subcategory}] Достигнут лимит {self.max_news_per_subcategory} новостей")
                return {
                    "success": True,
                    "processed": 0,
                    "saved": 0,
                    "type": "html",
                    "reason": "limit_reached",
                }

            # Извлекаем контент каскадным методом
            extracted = self._extract_content_cascade(url, content)
            if not extracted:
                return {"success": False, "reason": "content_extraction_failed"}

            title = extracted["title"]
            maintext = extracted["maintext"]
            method = extracted["method"]

            if not title or not maintext:
                return {"success": False, "reason": "insufficient_content"}

            # Оценка важности и достоверности
            text_for_ai = f"{title} {maintext}".strip()
            importance = evaluate_importance({"title": title, "content": text_for_ai})
            credibility = evaluate_credibility({"title": title, "content": text_for_ai})

            if importance < self.min_importance:
                logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                return {"success": False, "reason": "low_importance", "importance": importance}

            # Сохраняем в БД
            news_item = {
                "title": title,
                "content": maintext,
                "link": url,
                "source": name,
                "category": category,
                "subcategory": subcategory,
                "importance": importance,
                "credibility": credibility,
            }

            # Используем асинхронный сервис БД
            db_service = get_async_service()
            await db_service.async_upsert_news([news_item])

            self.subcategory_counts[subcategory] += 1

            logger.info(f"[{category}/{subcategory}] {url} -> SUCCESS ({method}, importance: {importance:.2f})")

            return {
                "success": True,
                "processed": 1,
                "saved": 1,
                "type": "html",
                "method": method,
                "importance": importance,
                "credibility": credibility,
            }

        except Exception as e:
            return {"success": False, "reason": f"html_parse_error: {e}"}


async def main():
    """Основная функция тестирования парсера."""
    print("🚀 Запуск тестирования AdvancedParser")
    print("📊 Параметры: по 10 новостей на подкатегорию")

    try:
        async with TestAdvancedParser(
            max_concurrent=5,  # Ограничиваем параллельность для теста
            min_importance=0.2,  # Снижаем порог для тестирования
            max_news_per_subcategory=10,
        ) as parser:

            stats = await parser.run()

            print("\n" + "=" * 60)
            print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
            print("=" * 60)
            print(f"📰 Всего источников: {stats.get('total_sources', 0)}")
            print(f"✅ Успешно обработано: {stats.get('successful', 0)}")
            print(f"❌ Неудачно: {stats.get('failed', 0)}")
            print(f"🔄 Всего новостей обработано: {stats.get('total_processed', 0)}")
            print(f"💾 Сохранено в БД: {stats.get('total_saved', 0)}")

            # Показываем статистику по подкатегориям
            if hasattr(parser, "subcategory_counts"):
                print(f"\n📈 Статистика по подкатегориям:")
                for subcategory, count in parser.subcategory_counts.items():
                    print(f"   • {subcategory}: {count} новостей")

            if stats.get("errors"):
                print(f"\n⚠️  Ошибки ({len(stats['errors'])}):")
                for error in stats["errors"][:5]:  # Показываем первые 5 ошибок
                    print(f"   • {error}")
                if len(stats["errors"]) > 5:
                    print(f"   ... и еще {len(stats['errors']) - 5} ошибок")

            print("=" * 60)

            # Возвращаем код выхода в зависимости от результатов
            if stats.get("total_saved", 0) > 0:
                return 0  # Успех
            else:
                return 1  # Нет сохраненных новостей

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
