#!/usr/bin/env python3
"""
Умный парсинг с автоматическим переобучением локальных моделей.

Этот скрипт:
1. Парсит свежие новости из всех источников
2. Проверяет, нужно ли переобучение
3. Автоматически переобучает модели при необходимости

Использование:
    python tools/news/fetch_and_train.py
    python tools/news/fetch_and_train.py --force-train  # Принудительное переобучение
    python tools/news/fetch_and_train.py --skip-train   # Только парсинг
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parsers.advanced_parser import AdvancedParser
from ai_modules.self_tuning_collector import get_self_tuning_collector
from ai_modules.self_tuning_trainer import get_self_tuning_trainer
from ai_modules.metrics import get_metrics

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/fetch_and_train.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def should_retrain(trainer, force: bool = False) -> bool:
    """
    Проверяет, нужно ли переобучение.

    Args:
        trainer: Экземпляр SelfTuningTrainer
        force: Принудительное переобучение

    Returns:
        True если нужно переобучение
    """
    if force:
        logger.info("🔄 Принудительное переобучение запрошено")
        return True

    try:
        # Получаем метаданные последнего обучения
        metadata = trainer._load_existing_metadata()

        if not metadata:
            logger.info("📊 Модели не найдены, требуется первое обучение")
            return True

        # Проверяем временной интервал
        last_training_str = metadata.get("timestamp")
        if not last_training_str:
            logger.info("⏰ Нет информации о последнем обучении")
            return True

        last_training = datetime.fromisoformat(last_training_str.replace("Z", "+00:00"))
        interval_days = trainer.config.get("self_tuning", {}).get("interval_days", 2)
        next_training = last_training + timedelta(days=interval_days)
        now = datetime.now(timezone.utc)

        if now >= next_training:
            days_since = (now - last_training).days
            logger.info(f"✅ Интервал переобучения достигнут ({days_since} дней с последнего обучения)")
            return True
        else:
            remaining = next_training - now
            logger.info(f"⏳ До переобучения осталось: {remaining}")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Ошибка проверки интервала переобучения: {e}")
        return False


async def fetch_news(max_concurrent: int = 10) -> dict:
    """
    Парсинг новостей из всех источников.

    Args:
        max_concurrent: Максимум одновременных запросов

    Returns:
        Статистика парсинга
    """
    logger.info("📰 Запуск парсинга новостей...")

    async with AdvancedParser(max_concurrent=max_concurrent) as parser:
        stats = await parser.run()

    logger.info(f"✅ Парсинг завершен: обработано {stats.get('total_sources', 0)} источников")
    return stats


def train_models(force_train: bool = False) -> dict:
    """
    Переобучение локальных моделей.

    Args:
        force_train: Принудительное переобучение

    Returns:
        Результаты обучения
    """
    logger.info("🤖 Проверка необходимости переобучения...")

    collector = get_self_tuning_collector()
    trainer = get_self_tuning_trainer()

    # Проверка, включено ли самообучение
    if not collector.is_enabled() or not trainer.is_enabled():
        logger.warning("⚠️ Self-tuning отключен в конфигурации")
        return {"success": False, "reason": "disabled"}

    # Проверка интервала переобучения
    if not should_retrain(trainer, force=force_train):
        logger.info("⏭️ Переобучение не требуется")
        return {"success": True, "reason": "interval_not_reached"}

    # Сбор данных для обучения
    logger.info("📊 Сбор обучающих данных...")
    collection_result = collector.collect_training_data()

    if not collection_result["success"]:
        logger.error(f"❌ Ошибка сбора данных: {collection_result.get('error')}")
        return collection_result

    dataset_size = collection_result["dataset_size"]
    logger.info(f"✅ Собрано {dataset_size} примеров")

    # Обучение моделей
    logger.info("🧠 Обучение моделей...")
    dataset_path = Path(collection_result["dataset_path"])
    training_result = trainer.train_models(dataset_path)

    if not training_result["success"]:
        logger.error(f"❌ Ошибка обучения: {training_result.get('error')}")
        return training_result

    # Вывод результатов
    improvements = training_result.get("improvements", {})
    for model_name, result in improvements.items():
        f1_score = result.get("f1_score", 0.0)
        improvement = result.get("improvement", 0.0)
        replaced = result.get("replaced", False)

        status = "✅ ЗАМЕНЕНА" if replaced else "⏸️ НЕ ЗАМЕНЕНА"
        logger.info(f"   {model_name}: F1={f1_score:.3f}, улучшение={improvement:.3f} ({status})")

    logger.info("🎉 Переобучение завершено успешно!")
    return training_result


async def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Парсинг новостей с автоматическим переобучением моделей")

    # Параметры парсинга
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Максимум одновременных запросов (по умолчанию: 10)",
    )

    # Параметры переобучения
    parser.add_argument(
        "--force-train",
        action="store_true",
        help="Принудительное переобучение (игнорировать интервал)",
    )
    parser.add_argument(
        "--skip-train",
        action="store_true",
        help="Пропустить переобучение (только парсинг)",
    )

    # Другие параметры
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("🚀 Запуск умного парсинга с автообучением")
    logger.info("=" * 60)

    start_time = datetime.now(timezone.utc)

    try:
        # Шаг 1: Парсинг новостей
        logger.info("📰 ШАГ 1: Парсинг свежих новостей")
        logger.info("-" * 60)

        fetch_stats = await fetch_news(max_concurrent=args.max_concurrent)

        if not fetch_stats.get("total_saved", 0):
            logger.warning("⚠️ Нет новых новостей для обработки")

        logger.info("")

        # Шаг 2: Переобучение моделей (если нужно)
        if not args.skip_train:
            logger.info("🤖 ШАГ 2: Проверка и переобучение локальных моделей")
            logger.info("-" * 60)

            train_result = train_models(force_train=args.force_train)

            if train_result.get("success"):
                if train_result.get("reason") == "interval_not_reached":
                    logger.info("⏭️ Переобучение пропущено (интервал не достигнут)")
                elif train_result.get("reason") == "disabled":
                    logger.info("⏭️ Self-tuning отключен в конфигурации")
                else:
                    logger.info("✅ Модели успешно переобучены")
            else:
                logger.error("❌ Ошибка переобучения")
        else:
            logger.info("⏭️ ШАГ 2: Переобучение пропущено (--skip-train)")

        logger.info("")

        # Итоговая статистика
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("📊 ИТОГОВАЯ СТАТИСТИКА")
        logger.info("=" * 60)
        logger.info(f"⏱️ Время выполнения: {duration:.1f}с")
        logger.info(f"📰 Источников обработано: {fetch_stats.get('total_sources', 0)}")
        logger.info(f"✅ Успешно: {fetch_stats.get('successful', 0)}")
        logger.info(f"❌ Ошибок: {fetch_stats.get('failed', 0)}")
        logger.info(f"💾 Новостей сохранено: {fetch_stats.get('total_saved', 0)}")

        # Метрики оптимизации
        metrics = get_metrics()
        metrics_summary = metrics.get_metrics_summary()

        if metrics_summary.get("self_tuning_last_run_timestamp"):
            logger.info(f"🤖 Последнее обучение: {metrics_summary['self_tuning_last_run_timestamp']}")
            logger.info(f"🎯 Версия модели: v{metrics_summary['self_tuning_current_model_version']}")
            logger.info(f"📊 Размер датасета: {metrics_summary['self_tuning_dataset_size']}")

        logger.info("=" * 60)
        logger.info("🎉 Все операции завершены успешно!")

        return 0

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


