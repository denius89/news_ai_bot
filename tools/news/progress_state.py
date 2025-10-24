#!/usr/bin/env python3
"""
Модуль для работы с состоянием прогресса парсинга новостей.

Обеспечивает синхронизацию между Flask процессом (API) и процессом парсинга
через JSON файл data/progress_state.json.
"""

import json
import fcntl
import threading
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

# Путь к файлу состояния
PROGRESS_STATE_FILE = Path("data/progress_state.json")

# Блокировка для потокобезопасности
_state_lock = threading.Lock()


def _ensure_data_dir():
    """Создает директорию data если её нет."""
    PROGRESS_STATE_FILE.parent.mkdir(exist_ok=True)


def _get_default_state() -> Dict[str, Any]:
    """Возвращает начальное состояние прогресса."""
    return {
        "sources_total": 0,
        "sources_processed": 0,
        "news_found": 0,
        "news_saved": 0,
        "news_filtered": 0,
        "errors_count": 0,
        "current_source": "",
        "top_sources": {},  # {source_name: {count, avg_time}}
        "recent_errors": [],  # [{source, error_type, message, timestamp}]
        "categories_stats": {},  # {category: count}
        "ai_stats": {"local": 0, "openai": 0, "tokens_saved": 0},
        "start_time": None,
    }


def load_progress_state() -> Dict[str, Any]:
    """
    Загружает состояние прогресса из JSON файла.

    Returns:
        Dict с состоянием прогресса или дефолтное состояние если файл не найден
    """
    _ensure_data_dir()

    if not PROGRESS_STATE_FILE.exists():
        return _get_default_state()

    try:
        with open(PROGRESS_STATE_FILE, "r", encoding="utf-8") as f:
            with _state_lock:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock для чтения
                data = json.load(f)

        # Убеждаемся что все необходимые поля присутствуют
        default_state = _get_default_state()
        for key, default_value in default_state.items():
            if key not in data:
                data[key] = default_value

        return data
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Error loading progress state: {e}")
        return _get_default_state()


def save_progress_state(state: Dict[str, Any]) -> bool:
    """
    Сохраняет состояние прогресса в JSON файл.

    Args:
        state: Словарь с состоянием для сохранения

    Returns:
        True если сохранение успешно, False в противном случае
    """
    _ensure_data_dir()

    try:
        with open(PROGRESS_STATE_FILE, "w", encoding="utf-8") as f:
            with _state_lock:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock для записи

                # Конвертируем datetime в ISO строку
                def datetime_converter(obj):
                    if hasattr(obj, "isoformat"):
                        return obj.isoformat()
                    return str(obj)

                json.dump(state, f, indent=2, ensure_ascii=False, default=datetime_converter)
        return True
    except (IOError, OSError) as e:
        print(f"Error saving progress state: {e}")
        return False


def update_progress_state(**kwargs) -> bool:
    """
    Атомарно обновляет состояние прогресса.

    Args:
        **kwargs: Поля для обновления

    Returns:
        True если обновление успешно
    """
    # Отладочный вывод
    print(f"DEBUG: update_progress_state called with {kwargs}")

    state = load_progress_state()

    # Обновляем переданные поля
    for key, value in kwargs.items():
        if key == "sources_total" and value is not None:
            state["sources_total"] = value
            state["start_time"] = datetime.now(timezone.utc).isoformat()
        elif key == "sources_processed_delta":
            state["sources_processed"] += value
        elif key == "news_found_delta":
            state["news_found"] += value
        elif key == "news_saved_delta":
            state["news_saved"] += value
        elif key == "news_filtered_delta":
            state["news_filtered"] += value
        elif key == "current_source" and value:
            state["current_source"] = value
        elif key == "error" and value:
            state["errors_count"] += 1
            error_entry = {
                "source": value.get("source", ""),
                "error_type": value.get("error_type", ""),
                "message": value.get("message", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            state["recent_errors"].append(error_entry)
            # Храним только последние 20 ошибок
            if len(state["recent_errors"]) > 20:
                state["recent_errors"] = state["recent_errors"][-20:]
        elif key == "source_stats" and value:
            source_name = value.get("name", "unknown")
            if source_name not in state["top_sources"]:
                state["top_sources"][source_name] = {"count": 0, "avg_time": 0}
            state["top_sources"][source_name]["count"] += value.get("news_count", 0)
            state["top_sources"][source_name]["avg_time"] = value.get("time_ms", 0)
        elif key == "category" and value:
            state["categories_stats"][value] = state["categories_stats"].get(value, 0) + 1
        elif key == "ai_stats" and value:
            for ai_key, ai_value in value.items():
                state["ai_stats"][ai_key] = state["ai_stats"].get(ai_key, 0) + ai_value

    return save_progress_state(state)


def reset_progress_state() -> bool:
    """
    Сбрасывает состояние прогресса к начальным значениям.

    Returns:
        True если сброс успешен
    """
    return save_progress_state(_get_default_state())


def get_progress_state() -> Dict[str, Any]:
    """
    Возвращает текущее состояние прогресса в формате для API.

    Returns:
        Dict с форматированными данными для API ответа
    """
    state = load_progress_state()

    # Сортируем топ источников по количеству новостей
    top_sources_list = [
        {"name": name, "count": data["count"], "avg_time": data["avg_time"]}
        for name, data in sorted(state["top_sources"].items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    ]

    # Подготавливаем категории
    category_stats = [
        {"name": cat, "count": count}
        for cat, count in sorted(state["categories_stats"].items(), key=lambda x: x[1], reverse=True)
    ]

    # Вычисляем процент прогресса
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

    # AI статистика
    ai_stats = state["ai_stats"]
    total_ai_calls = ai_stats.get("local", 0) + ai_stats.get("openai", 0)
    local_percent = (ai_stats.get("local", 0) / total_ai_calls * 100) if total_ai_calls > 0 else 0

    return {
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
        "top_sources": top_sources_list,
        "recent_errors": state["recent_errors"][-10:],  # Последние 10 ошибок
        "category_stats": category_stats,
        "ai_stats": {
            "local_predictions": ai_stats.get("local", 0),
            "openai_calls": ai_stats.get("openai", 0),
            "local_percent": round(local_percent, 1),
            "tokens_saved": ai_stats.get("tokens_saved", 0),
            "estimated_cost": round(ai_stats.get("openai", 0) * 0.0005, 4),  # Примерная стоимость
            "cost_saved": round(ai_stats.get("tokens_saved", 0) * 0.00015 / 1000, 4),  # Экономия
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
