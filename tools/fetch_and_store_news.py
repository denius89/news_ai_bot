#!/usr/bin/env python3
"""
Скрипт для запуска продвинутого парсера новостей.

Использует AdvancedParser для извлечения новостей из всех источников,
применяет AI-фильтры и сохраняет релевантные новости в базу данных.

Пример использования:
    python tools/fetch_and_store_news.py
    python tools/fetch_and_store_news.py --min-importance 0.5 --max-concurrent 5
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.advanced_parser import AdvancedParser

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/advanced_parser.log', encoding='utf-8'),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска парсера."""
    parser = argparse.ArgumentParser(description='Запуск продвинутого парсера новостей')
    parser.add_argument(
        '--min-importance',
        type=float,
        default=0.3,
        help='Минимальный порог важности для сохранения новости (по умолчанию: 0.3)',
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='Максимальное количество одновременных запросов (по умолчанию: 10)',
    )
    parser.add_argument('--verbose', action='store_true', help='Подробное логирование')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("🚀 Запуск продвинутого парсера новостей")
    logger.info(
        f"📊 Параметры: min_importance={args.min_importance}, max_concurrent={args.max_concurrent}"
    )

    try:
        async with AdvancedParser(
            max_concurrent=args.max_concurrent, min_importance=args.min_importance
        ) as parser_instance:

            stats = await parser_instance.run()

            logger.info("✅ Парсинг завершен")
            logger.info(f"📈 Статистика: {stats}")

            # Выводим результаты
            print("\n" + "=" * 60)
            print("📊 РЕЗУЛЬТАТЫ ПАРСИНГА")
            print("=" * 60)
            print(f"📰 Всего источников: {stats.get('total_sources', 0)}")
            print(f"✅ Успешно обработано: {stats.get('successful', 0)}")
            print(f"❌ Неудачно: {stats.get('failed', 0)}")
            print(f"🔄 Всего новостей обработано: {stats.get('total_processed', 0)}")
            print(f"💾 Сохранено в БД: {stats.get('total_saved', 0)}")

            if stats.get('errors'):
                print(f"\n⚠️  Ошибки ({len(stats['errors'])}):")
                for error in stats['errors'][:5]:  # Показываем первые 5 ошибок
                    print(f"   • {error}")
                if len(stats['errors']) > 5:
                    print(f"   ... и еще {len(stats['errors']) - 5} ошибок")

            print("=" * 60)

            # Возвращаем код выхода в зависимости от результатов
            if stats.get('total_saved', 0) > 0:
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
