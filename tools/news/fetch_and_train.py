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
import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parsers.advanced_parser import AdvancedParser
from ai_modules.self_tuning_collector import get_self_tuning_collector
from ai_modules.self_tuning_trainer import get_self_tuning_trainer
from ai_modules.metrics import get_metrics
from tools.news.progress_state import (
    reset_progress_state,
    update_progress_state,
    get_progress_state as get_state_for_api,
    load_progress_state,
)

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


# Глобальное состояние больше не используется - используется progress_state.py


def log_progress(event_type: str = "parsing_progress", **extra_data):
    """
    Логирует прогресс в JSON формате для real-time мониторинга.

    Args:
        event_type: Тип события
        **extra_data: Дополнительные данные
    """
    # Получаем текущее состояние из JSON файла
    state = load_progress_state()

    progress_percent = 0
    if state["sources_total"] > 0:
        progress_percent = round((state["sources_processed"] / state["sources_total"]) * 100, 1)

    # Вычисляем ETA
    eta_seconds = 0
    if state["start_time"] and state["sources_processed"] > 0:
        try:
            start_time = datetime.fromisoformat(state["start_time"].replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            avg_time_per_source = elapsed / state["sources_processed"]
            remaining_sources = state["sources_total"] - state["sources_processed"]
            eta_seconds = int(avg_time_per_source * remaining_sources)
        except (ValueError, TypeError):
            eta_seconds = 0

    log_data = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources_total": state["sources_total"],
        "sources_processed": state["sources_processed"],
        "sources_remaining": state["sources_total"] - state["sources_processed"],
        "progress_percent": progress_percent,
        "news_found": state["news_found"],
        "news_saved": state["news_saved"],
        "news_filtered": state["news_filtered"],
        "errors_count": state["errors_count"],
        "current_source": state["current_source"],
        "eta_seconds": eta_seconds,
        **extra_data,
    }

    logger.info(json.dumps(log_data))


def update_progress(
    sources_total: int = None,
    sources_processed_delta: int = 0,
    news_found_delta: int = 0,
    news_saved_delta: int = 0,
    news_filtered_delta: int = 0,
    current_source: str = None,
    error: Dict = None,
    source_stats: Dict = None,
    category: str = None,
    ai_stats: Dict = None,
):
    """Обновляет состояние прогресса через JSON файл."""
    # Используем новый модуль для атомарного обновления
    update_progress_state(
        sources_total=sources_total,
        sources_processed_delta=sources_processed_delta,
        news_found_delta=news_found_delta,
        news_saved_delta=news_saved_delta,
        news_filtered_delta=news_filtered_delta,
        current_source=current_source,
        error=error,
        source_stats=source_stats,
        category=category,
        ai_stats=ai_stats,
    )

    # Логируем прогресс
    if sources_total is not None:
        # Логируем когда устанавливается sources_total
        log_progress(event_type="sources_initialized", sources_total=sources_total)
    elif sources_processed_delta > 0:
        # Логируем каждые 2 источника для более частых обновлений
        state = load_progress_state()
        if state["sources_processed"] % 2 == 0:
            log_progress()
    elif error:
        log_progress(event_type="parsing_error", error=error)
    elif current_source:
        # Логируем при смене источника
        log_progress(event_type="source_change", current_source=current_source)


def get_progress_state() -> Dict:
    """
    Возвращает текущее состояние прогресса для API.

    Returns:
        Dict с актуальными метриками
    """
    # Используем новый модуль для получения состояния
    return get_state_for_api()


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


async def fetch_news(
    max_concurrent: int = 10, categories: Optional[List[str]] = None, subcategories: Optional[List[str]] = None
) -> dict:
    """
    Парсинг новостей из всех источников.

    Args:
        max_concurrent: Максимум одновременных запросов
        categories: Список категорий для обработки
        subcategories: Список субкатегорий для обработки

    Returns:
        Статистика парсинга
    """
    logger.info("📰 Запуск парсинга новостей...")

    # Сброс состояния прогресса через новый модуль
    reset_progress_state()

    if categories:
        logger.info(f"🔍 Фильтр категорий: {categories}")
    if subcategories:
        logger.info(f"🔍 Фильтр субкатегорий: {subcategories}")

    async with AdvancedParser(
        max_concurrent=max_concurrent, min_importance=0.1, categories=categories, subcategories=subcategories
    ) as parser:
        # Получаем общее количество источников для прогресса (инициализация уже выполнена в __aenter__)
        total_sources = parser.get_total_sources_count()
        logger.info(f"📍 Найдено источников для парсинга: {total_sources}")
        if total_sources > 0:
            update_progress(sources_total=total_sources)
        else:
            logger.warning("⚠️ Не найдено источников для парсинга - возможно проблема с конфигурацией или фильтрами")

        # Логируем начало после установки sources_total
        log_progress(event_type="fetch_started", categories=categories, subcategories=subcategories)

        # Запускаем парсинг с отслеживанием прогресса
        stats = await parser.run()
        # Обновляем финальную статистику на основе результатов
        if stats:
            update_progress(
                sources_processed_delta=stats.get("successful", 0),
                news_saved_delta=stats.get("total_saved", 0),
                news_found_delta=stats.get("total_processed", 0),
                news_filtered_delta=stats.get("total_processed", 0) - stats.get("total_saved", 0),
            )

    logger.info(f"✅ Парсинг завершен: обработано {stats.get('total_sources', 0)} источников")

    # Финальный лог
    final_state = load_progress_state()
    log_progress(
        event_type="fetch_completed",
        final_stats={
            "total_sources": stats.get("total_sources", 0),
            "news_found": final_state["news_found"],
            "news_saved": final_state["news_saved"],
            "news_filtered": final_state["news_filtered"],
            "errors_count": final_state["errors_count"],
        },
    )

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

    # Параметры фильтрации
    parser.add_argument(
        "--categories",
        type=str,
        help="Список категорий для обработки (через запятую)",
    )
    parser.add_argument(
        "--subcategories",
        type=str,
        help="Список субкатегорий для обработки (через запятую)",
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

        # Парсим параметры категорий
        categories = None
        if args.categories:
            categories = [cat.strip() for cat in args.categories.split(",")]

        subcategories = None
        if args.subcategories:
            subcategories = [subcat.strip() for subcat in args.subcategories.split(",")]

        fetch_stats = await fetch_news(
            max_concurrent=args.max_concurrent, categories=categories, subcategories=subcategories
        )

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
