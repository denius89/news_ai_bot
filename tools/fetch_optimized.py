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

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.optimized_parser import run_optimized_parser
from ai_modules.metrics import get_metrics

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
        os.environ['LOCAL_PREDICTOR_ENABLED'] = 'true'
    
    if args.disable_cache:
        os.environ['CACHE_ENABLED'] = 'false'
    
    if args.disable_prefilter:
        os.environ['PREFILTER_ENABLED'] = 'false'
    
    # Сброс метрик если запрошен
    if args.reset_metrics:
        metrics = get_metrics()
        metrics.reset_metrics()
        logger.info("Метрики сброшены")
    
    logger.info("🚀 Запуск оптимизированного парсера новостей")
    logger.info(f"📊 Параметры: concurrent={args.max_concurrent}, "
                f"importance≥{args.min_importance}, credibility≥{args.min_credibility}")
    
    try:
        # Запуск оптимизированного парсера
        result = await run_optimized_parser(max_concurrent=args.max_concurrent)
        
        if result['success']:
            logger.info("✅ Парсинг завершен успешно")
            logger.info(f"📰 Обработано новостей: {result['processed_items']}")
            logger.info(f"💾 Сохранено в БД: {result['saved_items']}")
            logger.info(f"⏱️ Время выполнения: {result['processing_time_seconds']}s")
            
            # Показать метрики оптимизации
            metrics_summary = result.get('metrics', {})
            logger.info("📈 Метрики оптимизации:")
            logger.info(f"   🤖 AI вызовов: {metrics_summary.get('ai_calls_total', 0)}")
            logger.info(f"   🚫 Пропущено предфильтром: {metrics_summary.get('ai_skipped_prefilter_total', 0)}")
            logger.info(f"   💾 Пропущено кэшем: {metrics_summary.get('ai_skipped_cache_total', 0)}")
            logger.info(f"   🧠 Пропущено предиктором: {metrics_summary.get('ai_skipped_local_pred_total', 0)}")
            logger.info(f"   💰 Всего сэкономлено вызовов: {metrics_summary.get('ai_calls_saved_total', 0)}")
            logger.info(f"   📊 Экономия: {metrics_summary.get('ai_calls_saved_percentage', 0)}%")
            
            if args.show_metrics:
                print("\n" + "="*60)
                print("📊 ПОДРОБНЫЕ МЕТРИКИ")
                print("="*60)
                for key, value in metrics_summary.items():
                    print(f"{key}: {value}")
                print("="*60)
            
            # Проверка эффективности
            ai_calls_saved = metrics_summary.get('ai_calls_saved_total', 0)
            news_processed = metrics_summary.get('news_processed_total', 0)
            
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
