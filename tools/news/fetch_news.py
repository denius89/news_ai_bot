#!/usr/bin/env python3
"""
Объединенный инструмент для получения новостей.
Объединяет функциональность fetch_and_store_news.py, fetch_loop.py, fetch_optimized.py
"""


# === ИЗ fetch_and_store_news.py ===

#!/usr/bin/env python3
"""
Скрипт для запуска продвинутого парсера новостей.

Использует AdvancedParser для извлечения новостей из всех источников,
применяет AI-фильтры и сохраняет релевантные новости в базу данных.

Пример использования:
    python tools/fetch_and_store_news.py
    python tools/fetch_and_store_news.py --min-importance 0.5 --max-concurrent 5
"""

from parsers.advanced_parser import AdvancedParser
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/advanced_parser.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска парсера."""
    parser = argparse.ArgumentParser(description="Запуск продвинутого парсера новостей")
    parser.add_argument(
        "--min-importance",
        type=float,
        default=0.3,
        help="Минимальный порог важности для сохранения новости (по умолчанию: 0.3)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Максимальное количество одновременных запросов (по умолчанию: 10)",
    )
    parser.add_argument("--verbose", action="store_true", help="Подробное логирование")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("🚀 Запуск продвинутого парсера новостей")
    logger.info(
        f"📊 Параметры: min_importance={args.min_importance}, max_concurrent={args.max_concurrent}")

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


# === ИЗ fetch_loop.py ===

#!/usr/bin/env python3
"""
Fetch Loop with Auto-Posting Integration.

This script runs a continuous loop to fetch news, generate digests,
and automatically post them to Telegram channels.
"""

from ai_modules.metrics import get_metrics
from telegram_bot.handlers.digest_handler import get_digest_handler, auto_post_digest
from parsers.optimized_parser import run_optimized_parser
import asyncio
import argparse
import logging
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/fetch_loop.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


class FetchLoop:
    """
    Continuous fetch loop with auto-posting integration.

    Features:
    - Configurable intervals
    - AI filtering
    - Auto-posting to Telegram
    - Graceful shutdown
    - Metrics tracking
    """

    def __init__(self, interval: int = 30, ai_filter: bool = True, auto_post: bool = False):
        """Initialize fetch loop."""
        self.interval = interval
        self.ai_filter = ai_filter
        self.auto_post = auto_post
        self.running = False
        self.metrics = get_metrics()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(
            f"FetchLoop initialized: interval={interval}s, ai_filter={ai_filter}, auto_post={auto_post}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def _run_fetch_cycle(self) -> bool:
        """
        Run a single fetch cycle.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting fetch cycle...")
            start_time = datetime.now(timezone.utc)

            # Run optimized parser
            if self.ai_filter:
                logger.info("Running with AI filtering enabled")
                result = await run_optimized_parser()
            else:
                logger.info("Running without AI filtering")
                result = await run_optimized_parser()

            if not result.get("success", False):
                logger.error(f"Fetch cycle failed: {result.get('error', 'Unknown error')}")
                return False

            # Log results
            processed = result.get("processed", 0)
            saved = result.get("saved", 0)
            ai_calls = result.get("ai_calls", 0)

            logger.info(
                f"Fetch cycle completed: processed={processed}, saved={saved}, ai_calls={ai_calls}")

            # Run auto-posting if enabled
            if self.auto_post:
                logger.info("Running auto-posting...")
                post_result = await auto_post_digest()

                if post_result.get("success", False):
                    published = post_result.get("published_count", 0)
                    logger.info(f"Auto-posting completed: published={published} digests")
                else:
                    logger.warning(
                        f"Auto-posting failed: {post_result.get('reason', 'Unknown error')}")

            # Calculate cycle time
            cycle_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Cycle completed in {cycle_time:.2f} seconds")

            return True

        except Exception as e:
            logger.error(f"Error in fetch cycle: {e}")
            return False

    async def run(self):
        """Run the continuous fetch loop."""
        self.running = True
        logger.info("Starting fetch loop...")

        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"Starting cycle #{cycle_count}")

                # Run fetch cycle
                success = await self._run_fetch_cycle()

                if success:
                    logger.info(f"Cycle #{cycle_count} completed successfully")
                else:
                    logger.error(f"Cycle #{cycle_count} failed")

                # Wait for next cycle
                if self.running:
                    logger.info(f"Waiting {self.interval} seconds until next cycle...")
                    await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                logger.info("Fetch loop cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in fetch loop: {e}")
                if self.running:
                    logger.info(f"Waiting {self.interval} seconds before retry...")
                    await asyncio.sleep(self.interval)

        logger.info("Fetch loop stopped")

    async def stop(self):
        """Stop the fetch loop gracefully."""
        logger.info("Stopping fetch loop...")
        self.running = False


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fetch loop with auto-posting")
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval between cycles in seconds (default: 30)")
    parser.add_argument("--ai-filter", action="store_true", help="Enable AI filtering")
    parser.add_argument("--auto-post", action="store_true", help="Enable auto-posting to Telegram")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run only once instead of continuous loop")

    args = parser.parse_args()

    # Create fetch loop
    fetch_loop = FetchLoop(
        interval=args.interval,
        ai_filter=args.ai_filter,
        auto_post=args.auto_post)

    try:
        if args.once:
            # Run single cycle
            logger.info("Running single fetch cycle...")
            success = await fetch_loop._run_fetch_cycle()
            if success:
                logger.info("Single cycle completed successfully")
                sys.exit(0)
            else:
                logger.error("Single cycle failed")
                sys.exit(1)
        else:
            # Run continuous loop
            await fetch_loop.run()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await fetch_loop.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


# === ИЗ fetch_optimized.py ===

#!/usr/bin/env python3
"""
Optimized news fetching tool with AI call reduction.

This script uses the optimized parser to fetch news with reduced AI API calls
while maintaining quality through pre-filtering, caching, and local prediction.

Example usage:
    python tools/fetch_optimized.py
    python tools/fetch_optimized.py --max-concurrent 5 --min-importance 0.6
    python tools/fetch_optimized.py --enable-local-predictor --disable-cache
"""

from ai_modules.metrics import get_metrics
from parsers.optimized_parser import run_optimized_parser
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/fetch_optimized.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска оптимизированного парсера."""
    parser = argparse.ArgumentParser(description="Запуск оптимизированного парсера новостей")
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Максимальное количество одновременных запросов (по умолчанию: 10)",
    )
    parser.add_argument(
        "--min-importance",
        type=float,
        default=0.6,
        help="Минимальный порог важности (по умолчанию: 0.6)",
    )
    parser.add_argument(
        "--min-credibility",
        type=float,
        default=0.7,
        help="Минимальный порог достоверности (по умолчанию: 0.7)",
    )
    parser.add_argument(
        "--enable-local-predictor",
        action="store_true",
        help="Включить локальный предиктор",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Отключить кэширование",
    )
    parser.add_argument(
        "--disable-prefilter",
        action="store_true",
        help="Отключить предфильтрацию",
    )
    parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Показать метрики после завершения",
    )
    parser.add_argument(
        "--reset-metrics",
        action="store_true",
        help="Сбросить метрики перед запуском",
    )

    args = parser.parse_args()

    # Настройка конфигурации через переменные окружения
    import os

    if args.enable_local_predictor:
        os.environ["LOCAL_PREDICTOR_ENABLED"] = "true"

    if args.disable_cache:
        os.environ["CACHE_ENABLED"] = "false"

    if args.disable_prefilter:
        os.environ["PREFILTER_ENABLED"] = "false"

    # Сброс метрик если запрошен
    if args.reset_metrics:
        metrics = get_metrics()
        metrics.reset_metrics()
        logger.info("Метрики сброшены")

    logger.info("🚀 Запуск оптимизированного парсера новостей")
    logger.info(
        f"📊 Параметры: concurrent={args.max_concurrent}, "
        f"importance≥{args.min_importance}, credibility≥{args.min_credibility}"
    )

    try:
        # Запуск оптимизированного парсера
        result = await run_optimized_parser(max_concurrent=args.max_concurrent)

        if result["success"]:
            logger.info("✅ Парсинг завершен успешно")
            logger.info(f"📰 Обработано новостей: {result['processed_items']}")
            logger.info(f"💾 Сохранено в БД: {result['saved_items']}")
            logger.info(f"⏱️ Время выполнения: {result['processing_time_seconds']}s")

            # Показать метрики оптимизации
            metrics_summary = result.get("metrics", {})
            logger.info("📈 Метрики оптимизации:")
            logger.info(f"   🤖 AI вызовов: {metrics_summary.get('ai_calls_total', 0)}")
            logger.info(
                f"   🚫 Пропущено предфильтром: {metrics_summary.get('ai_skipped_prefilter_total', 0)}")
            logger.info(f"   💾 Пропущено кэшем: {metrics_summary.get('ai_skipped_cache_total', 0)}")
            logger.info(
                f"   🧠 Пропущено предиктором: {metrics_summary.get('ai_skipped_local_pred_total', 0)}")
            logger.info(
                f"   💰 Всего сэкономлено вызовов: {metrics_summary.get('ai_calls_saved_total', 0)}")
            logger.info(f"   📊 Экономия: {metrics_summary.get('ai_calls_saved_percentage', 0)}%")

            if args.show_metrics:
                print("\n" + "=" * 60)
                print("📊 ПОДРОБНЫЕ МЕТРИКИ")
                print("=" * 60)
                for key, value in metrics_summary.items():
                    print(f"{key}: {value}")
                print("=" * 60)

            # Проверка эффективности
            ai_calls_saved = metrics_summary.get("ai_calls_saved_total", 0)
            news_processed = metrics_summary.get("news_processed_total", 0)

            if news_processed > 0:
                efficiency = (ai_calls_saved / news_processed) * 100
                logger.info(f"🎯 Эффективность оптимизации: {efficiency:.1f}%")

                if efficiency >= 60:
                    logger.info("🎉 Отличная эффективность! Цель достигнута (≥60%)")
                elif efficiency >= 30:
                    logger.info("✅ Хорошая эффективность")
                else:
                    logger.warning("⚠️ Низкая эффективность. Рассмотрите настройку параметров")

        else:
            logger.error(f"❌ Ошибка парсинга: {result.get('error', 'Неизвестная ошибка')}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
