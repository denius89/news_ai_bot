"""
Admin API Routes для PulseAI Admin Panel.

Предоставляет REST API endpoints для админ-панели:
- Статистика системы
- AI метрики
- Просмотр логов
- Управление конфигурацией
- Real-time SSE для метрик
"""

from flask import Blueprint, jsonify, request, Response, stream_with_context, g
from utils.auth.admin_check import require_admin, get_admin_info
from database.service import get_sync_service
from datetime import datetime, timedelta
import logging
import json
import time
import os
from pathlib import Path
import threading
from functools import wraps
import subprocess
import glob
import psutil
import sys

admin_bp = Blueprint("admin_api", __name__, url_prefix="/admin/api")
logger = logging.getLogger(__name__)

# Simple in-memory cache for API responses
_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 60  # 60 seconds cache TTL


def cached(ttl=CACHE_TTL):
    """Simple cache decorator for API endpoints"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{f.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"

            with _cache_lock:
                # Check if cached and not expired
                if cache_key in _cache:
                    cached_data, timestamp = _cache[cache_key]
                    if time.time() - timestamp < ttl:
                        logger.debug(f"Cache hit for {f.__name__}")
                        return cached_data
                    else:
                        # Remove expired cache
                        del _cache[cache_key]

            # Execute function and cache result
            result = f(*args, **kwargs)

            with _cache_lock:
                _cache[cache_key] = (result, time.time())
                logger.debug(f"Cached result for {f.__name__}")

            return result

        return wrapper

    return decorator


# ==================== Auth & User Info ====================


@admin_bp.route("/me", methods=["GET"])
@require_admin
def get_current_admin():
    """
    Получить информацию о текущем админе.

    Returns:
        JSON с данными админа: { telegram_id, username, is_admin, last_login }
    """
    try:
        telegram_id = g.admin_id
        admin_info = get_admin_info(telegram_id)

        if not admin_info:
            return jsonify({"error": "Admin info not found"}), 404

        return jsonify(
            {
                "telegram_id": admin_info.get("telegram_id"),
                "username": admin_info.get("username"),
                "is_admin": True,
                "is_active": admin_info.get("is_active"),
                "last_login": admin_info.get("last_login"),
                "created_at": admin_info.get("created_at"),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get admin info: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==================== Statistics ====================


@admin_bp.route("/stats", methods=["GET"])
@require_admin
@cached(ttl=30)  # Cache stats for 30 seconds
def get_stats():
    """
    Общая статистика системы за сегодня.

    Returns:
        JSON: { users_today, news_today, digests_today, total_users }
    """
    try:
        logger.info("Getting admin stats...")
        db = get_sync_service()

        # Общее количество пользователей
        try:
            users_result = db.safe_execute(db.sync_client.table("users").select("id", count="exact"))
            total_users = users_result.count if users_result else 0
        except Exception as e:
            logger.warning(f"Error getting users count: {e}")
            total_users = 0

        # Новости за сегодня
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            news_result = db.safe_execute(
                db.sync_client.table("news").select("id", count="exact").gte("published_at", today)
            )
            news_today = news_result.count if news_result else 0
        except Exception as e:
            logger.warning(f"Error getting news count: {e}")
            news_today = 0

        # Дайджесты за сегодня
        try:
            digests_result = db.safe_execute(
                db.sync_client.table("digests").select("id", count="exact").gte("created_at", today)
            )
            digests_today = digests_result.count if digests_result else 0
        except Exception as e:
            logger.warning(f"Error getting digests count: {e}")
            digests_today = 0

        # AI метрики из новостей (средние за 7 дней)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        avg_importance = 0.0
        avg_credibility = 0.0

        try:
            ai_result = db.safe_execute(
                db.sync_client.table("news")
                .select("importance, credibility")
                .gte("published_at", week_ago)
                .not_.is_("importance", "null")
                .not_.is_("credibility", "null")
                .limit(100)
            )

            if ai_result.data:
                importance_values = [
                    float(item["importance"]) for item in ai_result.data if item.get("importance") is not None
                ]
                credibility_values = [
                    float(item["credibility"]) for item in ai_result.data if item.get("credibility") is not None
                ]

                if importance_values:
                    avg_importance = sum(importance_values) / len(importance_values)
                if credibility_values:
                    avg_credibility = sum(credibility_values) / len(credibility_values)
        except Exception as e:
            logger.warning(f"Error getting AI metrics from news: {e}")

        result = {
            "news_today": news_today,
            "digests_today": digests_today,
            "total_users": total_users,
            "avg_importance": round(avg_importance, 2),
            "avg_credibility": round(avg_credibility, 2),
        }

        logger.info(f"Stats result: {result}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({"error": "Failed to fetch statistics"}), 500


# ==================== AI Metrics ====================


@admin_bp.route("/metrics/ai", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache AI metrics for 1 minute
def get_ai_metrics():
    """
    AI метрики: распределение importance и credibility.

    Query params:
        days: int - количество дней для анализа (default: 7)

    Returns:
        JSON: { importance_distribution, credibility_distribution, avg_importance, avg_credibility }
    """
    try:
        logger.info("Getting AI metrics...")
        db = get_sync_service()
        days = int(request.args.get("days", 7))  # Вернуть с 30 на 7 дней по умолчанию
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Получаем новости с AI метриками (importance, credibility)
        try:
            logger.info(f"Fetching news with AI metrics since {since_date}...")
            result = db.safe_execute(
                db.sync_client.table("news")
                .select("importance, credibility, published_at")
                .gte("published_at", since_date)
                .not_.is_("importance", "null")  # Только новости с оценками
                .not_.is_("credibility", "null")
                .limit(1000)
            )
            data = result.data or []
            logger.info(f"Found {len(data)} news items with AI metrics")
        except Exception as e:
            logger.warning(f"Error fetching news with AI metrics: {e}")
            data = []

        if not data:
            # Нет данных - возвращаем пустые распределения
            return jsonify(
                {
                    "importance_distribution": [],
                    "credibility_distribution": [],
                    "avg_importance": 0.0,
                    "avg_credibility": 0.0,
                    "total_items": 0,
                    "days_analyzed": days,
                }
            )

        # Вычисляем распределение и средние
        importance_values = [float(item["importance"]) for item in data if item.get("importance") is not None]
        credibility_values = [float(item["credibility"]) for item in data if item.get("credibility") is not None]

        # Группируем в bins для графиков
        def create_distribution(values, bins=10):
            if not values:
                return []

            min_val, max_val = 0.0, 1.0  # Фиксированный диапазон 0-1
            step = (max_val - min_val) / bins

            distribution = []
            for i in range(bins):
                bin_start = min_val + i * step
                bin_end = bin_start + step
                count = sum(1 for v in values if bin_start <= v < bin_end)
                distribution.append({"range": f"{bin_start:.1f}-{bin_end:.1f}", "count": count})
            return distribution

        return jsonify(
            {
                "importance_distribution": create_distribution(importance_values),
                "credibility_distribution": create_distribution(credibility_values),
                "avg_importance": (
                    round(sum(importance_values) / len(importance_values), 2) if importance_values else 0.0
                ),
                "avg_credibility": (
                    round(sum(credibility_values) / len(credibility_values), 2) if credibility_values else 0.0
                ),
                "total_items": len(data),
                "days_analyzed": days,
            }
        )

    except Exception as e:
        logger.error(f"Failed to get AI metrics: {e}")
        return jsonify({"error": "Failed to fetch AI metrics"}), 500


# ==================== User Metrics ====================


@admin_bp.route("/metrics/users", methods=["GET"])
@require_admin
def get_user_metrics():
    """
    Метрики пользователей: активность, подписки.

    Returns:
        JSON: { total_users, active_users, subscriptions_stats }
    """
    try:
        db = get_sync_service()

        # Всего пользователей
        users_result = db.safe_execute(db.sync_client.table("users").select("id", count="exact"))
        total_users = users_result.count or 0

        # Подписки
        subscriptions_result = db.safe_execute(
            db.sync_client.table("subscriptions").select("category, user_id").limit(1000)
        )
        subscriptions = subscriptions_result.data or []

        # Группируем по категориям
        category_counts = {}
        for sub in subscriptions:
            cat = sub.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return jsonify(
            {
                "total_users": total_users,
                "total_subscriptions": len(subscriptions),
                "category_distribution": [
                    {"category": k, "count": v}
                    for k, v in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
                ],
            }
        )

    except Exception as e:
        logger.error(f"Failed to get user metrics: {e}")
        return jsonify({"error": "Failed to fetch user metrics"}), 500


# ==================== Real-time SSE ====================


@admin_bp.route("/metrics/stream", methods=["GET"])
@require_admin
def metrics_stream():
    """
    Server-Sent Events для real-time метрик.

    Отправляет обновления статистики каждые 5 секунд.
    """

    def generate():
        db = get_sync_service()

        while True:
            try:
                # Получаем свежую статистику
                today = datetime.now().date()

                news_result = db.safe_execute(
                    db.sync_client.table("news").select("id", count="exact").gte("created_at", today.isoformat())
                )

                data = {
                    "timestamp": datetime.now().isoformat(),
                    "news_today": news_result.count or 0,
                    "server_time": datetime.now().strftime("%H:%M:%S"),
                }

                yield f"data: {json.dumps(data)}\n\n"

            except Exception as e:
                logger.error(f"SSE error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            time.sleep(5)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # Для Nginx
    )


# ==================== Logs ====================


@admin_bp.route("/logs/tail", methods=["GET"])
@require_admin
def get_logs():
    """
    Получить последние строки из лог-файла.

    Query params:
        file: str - имя файла (app.log, telegram_bot.log, reactor.log)
        lines: int - количество строк (default: 100)

    Returns:
        JSON: { logs: [...], file: str, total_lines: int }
    """
    try:
        log_file = request.args.get("file", "app.log")
        lines = int(request.args.get("lines", 100))

        # Безопасность: только разрешенные файлы
        allowed_files = ["app.log", "telegram_bot.log", "reactor.log", "flask.log", "bot.log"]
        if log_file not in allowed_files:
            return jsonify({"error": "Invalid log file"}), 400

        # Путь к логам
        log_path = Path(__file__).parent.parent / "logs" / log_file

        if not log_path.exists():
            return jsonify(
                {"logs": [], "file": log_file, "total_lines": 0, "message": f"Log file {log_file} not found"}
            )

        # Читаем последние N строк
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        # Парсим строки (формат: timestamp | level | message)
        parsed_logs = []
        for line in last_lines:
            parsed_logs.append(
                {"text": line.strip(), "timestamp": datetime.now().isoformat()}  # TODO: парсить реальный timestamp
            )

        return jsonify(
            {"logs": parsed_logs, "file": log_file, "total_lines": len(all_lines), "returned_lines": len(parsed_logs)}
        )

    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return jsonify({"error": f"Failed to read log file: {str(e)}"}), 500


@admin_bp.route("/logs/files", methods=["GET"])
@require_admin
def list_log_files():
    """
    Получить список доступных лог-файлов.

    Returns:
        JSON: { files: [...] }
    """
    try:
        log_dir = Path(__file__).parent.parent / "logs"

        if not log_dir.exists():
            return jsonify({"files": []})

        log_files = []
        for file_path in log_dir.glob("*.log"):
            stat = file_path.stat()
            log_files.append(
                {
                    "name": file_path.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return jsonify({"files": sorted(log_files, key=lambda x: x["modified"], reverse=True)})

    except Exception as e:
        logger.error(f"Failed to list log files: {e}")
        return jsonify({"error": "Failed to list log files"}), 500


# ==================== Debug ====================


@admin_bp.route("/debug/news", methods=["GET"])
@require_admin
def debug_news():
    """Debug endpoint для проверки новостей в БД"""
    try:
        logger.info("Debug: checking all news in database...")
        db = get_sync_service()

        # Все новости (без поля created_at)
        all_news = db.safe_execute(db.sync_client.table("news").select("*").limit(5))

        # Новости с AI оценками
        news_with_ai = db.safe_execute(
            db.sync_client.table("news")
            .select("*")
            .not_.is_("importance", "null")
            .not_.is_("credibility", "null")
            .limit(5)
        )

        return jsonify(
            {
                "total_news": len(all_news.data) if all_news.data else 0,
                "news_with_ai_scores": len(news_with_ai.data) if news_with_ai.data else 0,
                "sample_all_news": all_news.data[:2] if all_news.data else [],
                "sample_ai_news": news_with_ai.data[:2] if news_with_ai.data else [],
                "all_news_fields": list(all_news.data[0].keys()) if all_news.data else [],
            }
        )

    except Exception as e:
        logger.error(f"Debug news failed: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Configuration ====================


@admin_bp.route("/config/all", methods=["GET"])
@require_admin
def get_all_config():
    """
    Получить все настройки из БД, сгруппированные по категориям.

    Returns:
        JSON: { ai: {...}, system: {...}, sources: {...}, users: {...} }
    """
    try:
        logger.info("Getting all config from database...")
        db = get_sync_service()

        result = db.safe_execute(db.sync_client.table("system_config").select("*").order("category, key"))

        if not result.data:
            logger.warning("No config found in database")
            return jsonify({})

        # Группируем по категориям
        config = {}
        for item in result.data:
            category = item["category"]
            if category not in config:
                config[category] = {}

            # Извлекаем короткое имя ключа (без префикса категории)
            key_parts = item["key"].split(".")
            short_key = key_parts[-1] if len(key_parts) > 1 else item["key"]

            config[category][short_key] = {
                "value": item["value"],
                "description": item.get("description", ""),
                "updated_at": item.get("updated_at", ""),
                "full_key": item["key"],
            }

        logger.info(f"Loaded config for {len(config)} categories")
        return jsonify(config)

    except Exception as e:
        logger.error(f"Failed to get all config: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/config/<category>/<key>", methods=["PUT"])
@require_admin
def update_config_value(category, key):
    """
    Обновить конкретную настройку в БД.

    Args:
        category: Категория настройки (ai, system, sources, users)
        key: Ключ настройки (без префикса категории)

    Request body:
        JSON: { value: ... }

    Returns:
        JSON: { success: True, key: '...', value: ... }
    """
    try:
        data = request.get_json()
        new_value = data.get("value")

        if new_value is None:
            return jsonify({"error": "Missing value"}), 400

        full_key = f"{category}.{key}"
        logger.info(f"Updating config {full_key} = {new_value}")

        db = get_sync_service()
        result = db.safe_execute(
            db.sync_client.table("system_config")
            .update(
                {
                    "value": new_value,
                    "updated_at": datetime.now().isoformat(),
                    "updated_by": g.admin_id if hasattr(g, "admin_id") else None,
                }
            )
            .eq("key", full_key)
        )

        if not result.data:
            return jsonify({"error": f"Config key {full_key} not found"}), 404

        logger.info(f"Config {full_key} updated successfully")
        return jsonify({"success": True, "key": full_key, "value": new_value})

    except Exception as e:
        logger.error(f"Failed to update config {category}.{key}: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/config", methods=["GET"])
@require_admin
def get_config():
    """
    Получить текущую конфигурацию системы (безопасно, без секретов).

    Returns:
        JSON: { ai_settings, system_settings }
    """
    try:
        from config.core.settings import (
            AI_MODEL_SUMMARY,
            AI_MODEL_SCORING,
            AI_MAX_TOKENS,
            REACTOR_ENABLED,
            DEBUG,
            APP_ENV,
        )

        return jsonify(
            {
                "ai_settings": {
                    "model_summary": AI_MODEL_SUMMARY,
                    "model_scoring": AI_MODEL_SCORING,
                    "max_tokens": AI_MAX_TOKENS,
                },
                "system_settings": {"reactor_enabled": REACTOR_ENABLED, "debug_mode": DEBUG, "environment": APP_ENV},
                "api_keys": {
                    "openai": (
                        "****" + os.getenv("OPENAI_API_KEY", "")[-4:] if os.getenv("OPENAI_API_KEY") else "not set"
                    ),
                    "telegram_bot": (
                        "****" + os.getenv("TELEGRAM_BOT_TOKEN", "")[-4:]
                        if os.getenv("TELEGRAM_BOT_TOKEN")
                        else "not set"
                    ),
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        return jsonify({"error": "Failed to fetch configuration"}), 500


# ==================== Prompts Management ====================


@admin_bp.route("/prompts", methods=["GET"])
@require_admin
def get_prompts():
    """
    Получить все промпты из digests/prompts_v2.py для просмотра.

    Returns:
        JSON: { styles: {...}, tones: {...}, editable: False }
    """
    try:
        logger.info("Getting prompts from prompts_v2...")
        from digests.prompts_v2 import STYLE_CARDS, TONE_CARDS

        return jsonify({"styles": STYLE_CARDS, "tones": TONE_CARDS, "editable": False})  # v1: только просмотр

    except Exception as e:
        logger.error(f"Failed to get prompts: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Sources Management ====================


@admin_bp.route("/sources", methods=["GET"])
@require_admin
def get_sources_config():
    """
    Получить структуру источников новостей из services/categories.py.

    Returns:
        JSON: { structure: {...}, statistics: {...} }
    """
    try:
        logger.info("Getting sources configuration...")
        from services.categories import get_category_structure, get_statistics

        structure = get_category_structure()
        statistics = get_statistics()

        return jsonify({"structure": structure, "statistics": statistics})

    except Exception as e:
        logger.error(f"Failed to get sources config: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/sources/test", methods=["POST"])
@require_admin
def test_source_parser():
    """
    Протестировать парсер RSS источника.

    Request body:
        JSON: { url: 'https://...' }

    Returns:
        JSON: { success: True, items_count: N, sample: [...] }
    """
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "Missing url"}), 400

        logger.info(f"Testing parser for URL: {url}")

        from parsers.unified_parser import get_sync_parser

        parser = get_sync_parser()

        # Пробуем спарсить
        content = parser._fetch_url_sync(url)
        if not content:
            return jsonify({"success": False, "error": "Failed to fetch URL"}), 400

        items = parser.parse_rss_feed(content, "Test Source")

        return jsonify({"success": True, "items_count": len(items), "sample": items[:3] if items else []})

    except Exception as e:
        logger.error(f"Failed to test source parser: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== System Monitoring ====================

# ==================== Enhanced Metrics APIs ====================


@admin_bp.route("/metrics/news", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache news metrics for 1 minute
def get_news_metrics():
    """
    Аналитика по новостям: timeline, по категориям, по источникам.

    Query params:
        days: int - период анализа (default: 7)

    Returns:
        JSON: {
            timeline: [{date, count}],
            by_category: [{category, count, avg_importance, avg_credibility}],
            by_source: [{source, count, avg_credibility}],
            total_news: int
        }
    """
    try:
        days = int(request.args.get("days", 7))
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        logger.info(f"Getting news metrics for last {days} days...")
        db = get_sync_service()

        # Все новости за период
        news_result = db.safe_execute(
            db.sync_client.table("news").select("*").gte("published_at", since_date).limit(5000)
        )

        news_data = news_result.data or []
        logger.info(f"Found {len(news_data)} news items")

        # Timeline - группировка по дням
        from collections import defaultdict

        timeline_dict = defaultdict(int)
        category_stats = defaultdict(lambda: {"count": 0, "importance": [], "credibility": []})
        source_stats = defaultdict(lambda: {"count": 0, "credibility": []})

        for item in news_data:
            # Timeline
            date_str = item.get("published_at", "")[:10]  # YYYY-MM-DD
            timeline_dict[date_str] += 1

            # By category
            category = item.get("category", "unknown")
            category_stats[category]["count"] += 1
            if item.get("importance") is not None:
                category_stats[category]["importance"].append(float(item["importance"]))
            if item.get("credibility") is not None:
                category_stats[category]["credibility"].append(float(item["credibility"]))

            # By source
            source = item.get("source", "unknown")
            source_stats[source]["count"] += 1
            if item.get("credibility") is not None:
                source_stats[source]["credibility"].append(float(item["credibility"]))

        # Format timeline
        timeline = [{"date": date, "count": count} for date, count in sorted(timeline_dict.items())]

        # Format by_category
        by_category = [
            {
                "category": cat,
                "count": stats["count"],
                "avg_importance": (
                    round(sum(stats["importance"]) / len(stats["importance"]), 2) if stats["importance"] else 0
                ),
                "avg_credibility": (
                    round(sum(stats["credibility"]) / len(stats["credibility"]), 2) if stats["credibility"] else 0
                ),
            }
            for cat, stats in category_stats.items()
        ]
        by_category.sort(key=lambda x: x["count"], reverse=True)

        # Format by_source (top 10)
        by_source = [
            {
                "source": src,
                "count": stats["count"],
                "avg_credibility": (
                    round(sum(stats["credibility"]) / len(stats["credibility"]), 2) if stats["credibility"] else 0
                ),
            }
            for src, stats in source_stats.items()
        ]
        by_source.sort(key=lambda x: x["count"], reverse=True)
        by_source = by_source[:10]

        return jsonify(
            {"timeline": timeline, "by_category": by_category, "by_source": by_source, "total_news": len(news_data)}
        )

    except Exception as e:
        logger.error(f"Failed to get news metrics: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/metrics/events", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache events metrics for 1 minute
def get_events_metrics():
    """
    Аналитика по событиям: предстоящие, по priority, по категориям.

    Query params:
        days: int - период для анализа прошлых (default: 7)
        upcoming_days: int - период для предстоящих (default: 7)

    Returns:
        JSON: {
            upcoming: [{event_time, title, priority, category}],
            by_priority: [{priority, count}],
            by_category: [{category, count}],
            total_upcoming: int
        }
    """
    try:
        days = int(request.args.get("days", 7))
        upcoming_days = int(request.args.get("upcoming_days", 7))

        logger.info("Getting events metrics...")
        db = get_sync_service()

        now = datetime.now()
        future_date = (now + timedelta(days=upcoming_days)).isoformat()

        # Upcoming events
        upcoming_result = db.safe_execute(
            db.sync_client.table("events")
            .select("event_time, title, priority, category, importance, country")
            .gte("event_time", now.isoformat())
            .lte("event_time", future_date)
            .order("event_time")
            .limit(50)
        )

        upcoming = upcoming_result.data or []
        logger.info(f"Found {len(upcoming)} upcoming events")

        # All events для статистики
        past_date = (now - timedelta(days=days)).isoformat()
        all_events_result = db.safe_execute(
            db.sync_client.table("events")
            .select("priority, category, importance")
            .gte("event_time", past_date)
            .limit(2000)
        )

        all_events = all_events_result.data or []

        # By priority
        from collections import defaultdict

        priority_stats = defaultdict(int)
        category_stats = defaultdict(int)

        for event in all_events:
            priority = event.get("priority", "unknown")
            priority_stats[priority] += 1

            category = event.get("category", "unknown")
            category_stats[category] += 1

        by_priority = [{"priority": p, "count": count} for p, count in priority_stats.items()]
        by_priority.sort(key=lambda x: x["count"], reverse=True)

        by_category = [{"category": c, "count": count} for c, count in category_stats.items()]
        by_category.sort(key=lambda x: x["count"], reverse=True)

        return jsonify(
            {
                "upcoming": upcoming,
                "by_priority": by_priority,
                "by_category": by_category,
                "total_upcoming": len(upcoming),
                "total_analyzed": len(all_events),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get events metrics: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/metrics/user-engagement", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache user engagement for 1 minute
def get_user_engagement_metrics():
    """
    Метрики вовлечённости пользователей.

    Returns:
        JSON: {
            active_users: {daily, weekly, monthly},
            growth_timeline: [{date, count}],
            subscriptions_dist: [{category, count}],
            total_users: int
        }
    """
    try:
        logger.info("Getting user engagement metrics...")
        db = get_sync_service()

        now = datetime.now()
        day_ago = (now - timedelta(days=1)).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()
        month_ago = (now - timedelta(days=30)).isoformat()

        # Total users
        total_result = db.safe_execute(db.sync_client.table("users").select("id", count="exact"))
        total_users = total_result.count if total_result else 0

        # Active users (по created_at как proxy)
        # Note: в будущем нужна таблица user_activity

        # New users timeline (last 30 days)
        users_month = db.safe_execute(db.sync_client.table("users").select("created_at").gte("created_at", month_ago))

        users_data = users_month.data or []

        # Group by date
        from collections import defaultdict

        growth_dict = defaultdict(int)
        for user in users_data:
            date_str = user.get("created_at", "")[:10]
            growth_dict[date_str] += 1

        growth_timeline = [{"date": date, "count": count} for date, count in sorted(growth_dict.items())]

        # Subscriptions distribution
        subs_result = db.safe_execute(db.sync_client.table("subscriptions").select("category").limit(5000))

        subs_data = subs_result.data or []
        category_count = defaultdict(int)
        for sub in subs_data:
            category_count[sub.get("category", "unknown")] += 1

        subscriptions_dist = [{"category": cat, "count": count} for cat, count in category_count.items()]
        subscriptions_dist.sort(key=lambda x: x["count"], reverse=True)

        return jsonify(
            {
                "active_users": {
                    "daily": len([u for u in users_data if u.get("created_at", "") >= day_ago]),
                    "weekly": len([u for u in users_data if u.get("created_at", "") >= week_ago]),
                    "monthly": len(users_data),
                },
                "growth_timeline": growth_timeline,
                "subscriptions_dist": subscriptions_dist,
                "total_users": total_users,
                "total_subscriptions": len(subs_data),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get user engagement metrics: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Phase 2: Enhanced Metrics ====================


@admin_bp.route("/metrics/digests", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache digest metrics for 1 minute
def get_digest_metrics():
    """
    Аналитика дайджестов (Phase 2)

    Query params:
        days: int - период анализа (default: 30)

    Returns:
        JSON: {
            total_digests: int,
            timeline: [{date, count}],
            avg_length_words: int,
            feedback_stats: {avg_score, total_feedback}
        }
    """
    try:
        days = int(request.args.get("days", 30))
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        logger.info(f"Getting digest metrics for last {days} days...")
        db = get_sync_service()

        # Все дайджесты за период
        digests_result = db.safe_execute(
            db.sync_client.table("digests").select("*").gte("created_at", since_date).limit(5000)
        )

        digests_data = digests_result.data or []
        logger.info(f"Found {len(digests_data)} digests")

        # Timeline
        from collections import defaultdict

        timeline_dict = defaultdict(int)
        total_words = 0
        feedback_scores = []

        for digest in digests_data:
            # Timeline
            date_str = digest.get("created_at", "")[:10]
            timeline_dict[date_str] += 1

            # Word count
            summary = digest.get("summary", "")
            if summary:
                words = len(summary.split())
                total_words += words

            # Feedback
            if digest.get("feedback_score") is not None:
                feedback_scores.append(float(digest["feedback_score"]))

        timeline = [{"date": date, "count": count} for date, count in sorted(timeline_dict.items())]

        avg_length = int(total_words / len(digests_data)) if digests_data else 0
        avg_feedback = round(sum(feedback_scores) / len(feedback_scores), 2) if feedback_scores else 0.0

        return jsonify(
            {
                "total_digests": len(digests_data),
                "timeline": timeline,
                "avg_length_words": avg_length,
                "feedback_stats": {"avg_score": avg_feedback, "total_feedback": len(feedback_scores)},
            }
        )

    except Exception as e:
        logger.error(f"Failed to get digest metrics: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/metrics/ai-performance", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache AI performance for 1 minute
def get_ai_performance_detailed():
    """
    Детальная производительность AI (Phase 2)

    Query params:
        days: int - период анализа (default: 7)

    Returns:
        JSON: {
            total_ai_calls: int,
            avg_quality_score: float,
            estimated_tokens: int,
            estimated_cost_usd: float,
            timeline: [{date, calls, tokens, cost}]
        }
    """
    try:
        days = int(request.args.get("days", 7))
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        logger.info(f"Getting AI performance metrics for last {days} days...")
        db = get_sync_service()

        # Новости с AI-оценками как proxy для AI calls
        news_result = db.safe_execute(
            db.sync_client.table("news")
            .select("published_at, importance, credibility")
            .gte("published_at", since_date)
            .not_.is_("importance", "null")
            .not_.is_("credibility", "null")
            .limit(5000)
        )

        news_data = news_result.data or []
        logger.info(f"Found {len(news_data)} AI-processed news items")

        # Рассчитываем метрики
        total_calls = len(news_data)
        quality_scores = [
            (float(item["importance"]) + float(item["credibility"])) / 2
            for item in news_data
            if item.get("importance") is not None and item.get("credibility") is not None
        ]
        avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0

        # Оцениваем токены (~500 на новость: title + summary + system prompt)
        estimated_tokens = total_calls * 500

        # Стоимость (gpt-4o-mini: $0.15 / 1M input tokens)
        estimated_cost = round((estimated_tokens / 1_000_000) * 0.15, 4)

        # Timeline
        from collections import defaultdict

        timeline_dict = defaultdict(int)
        for item in news_data:
            date_str = item.get("published_at", "")[:10]
            timeline_dict[date_str] += 1

        timeline = [
            {"date": date, "calls": count, "tokens": count * 500, "cost": round((count * 500 / 1_000_000) * 0.15, 4)}
            for date, count in sorted(timeline_dict.items())
        ]

        return jsonify(
            {
                "total_ai_calls": total_calls,
                "avg_quality_score": avg_quality,
                "estimated_tokens": estimated_tokens,
                "estimated_cost_usd": estimated_cost,
                "timeline": timeline,
            }
        )

    except Exception as e:
        logger.error(f"Failed to get AI performance metrics: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Events Providers ====================


@admin_bp.route("/events/providers", methods=["GET"])
@require_admin
@cached(ttl=60)
def get_events_providers():
    """
    Получить список провайдеров событий и их статистику.

    Returns:
        JSON: {
            providers: [...],
            total_events: int,
            categories: {sports: int, crypto: int, tech: int}
        }
    """
    try:
        logger.info("Getting events providers from config...")

        # Загружаем конфигурацию событий
        import yaml
        from pathlib import Path

        config_path = Path(__file__).parent.parent / "config" / "data" / "sources_events.yaml"

        if not config_path.exists():
            logger.error(f"Events config not found: {config_path}")
            return jsonify({"error": "Events config not found"}), 404

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Формируем список провайдеров из конфигурации
        providers = []
        category_counts = {}

        for category, providers_config in config.items():
            category_counts[category] = 0

            for provider_name, provider_config in providers_config.items():
                if provider_config.get("enabled", False):
                    # Проверяем есть ли API ключ если требуется
                    api_key_required = provider_config.get("api_key_required", False)
                    status = "active"

                    if api_key_required:
                        env_var = provider_config.get("env_var")
                        if env_var and not os.getenv(env_var):
                            status = "no_api_key"

                    providers.append(
                        {
                            "name": provider_name,
                            "category": category,
                            "status": status,
                            "events_count": 0,  # Будем получать из базы если нужно
                            "description": provider_config.get("description", ""),
                            "api_key_required": api_key_required,
                        }
                    )

                    category_counts[category] += 1

        # Получаем статистику событий из базы для отображения
        db = get_sync_service()
        result = db.safe_execute(db.sync_client.table("events").select("source, category").limit(10000))
        events_data = result.data or []

        # Обновляем счетчики событий для провайдеров
        from collections import defaultdict

        source_counts = defaultdict(int)

        for event in events_data:
            source = event.get("source", "Unknown")
            source_counts[source] += 1

        # Обновляем events_count для провайдеров
        for provider in providers:
            provider["events_count"] = source_counts.get(provider["name"], 0)

        return jsonify(
            {
                "providers": sorted(providers, key=lambda x: x["events_count"], reverse=True),
                "total_events": len(events_data),
                "categories": category_counts,
            }
        )

    except Exception as e:
        logger.error(f"Failed to get events providers: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/events/test", methods=["POST"])
@require_admin
def test_events_provider():
    """
    Протестировать провайдер событий реальным запросом.

    Body: { provider: str }

    Returns:
        JSON: {success: bool, events_found: int, sample_events: [...], error: str}
    """
    try:
        data = request.get_json()
        provider_name = data.get("provider")

        if not provider_name:
            return jsonify({"error": "Provider name is required"}), 400

        logger.info(f"Testing events provider: {provider_name}")

        # Загружаем конфигурацию событий
        import yaml
        from pathlib import Path

        config_path = Path(__file__).parent.parent / "config" / "data" / "sources_events.yaml"

        if not config_path.exists():
            return jsonify({"success": False, "error": "Events config not found"}), 404

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Находим провайдер в конфигурации
        provider_config = None
        provider_category = None

        for category, providers_config in config.items():
            if provider_name in providers_config:
                provider_config = providers_config[provider_name]
                provider_category = category
                break

        if not provider_config:
            return jsonify({"success": False, "error": f"Provider {provider_name} not found in config"}), 404

        if not provider_config.get("enabled", False):
            return jsonify({"success": False, "error": f"Provider {provider_name} is disabled"}), 400

        # Проверяем API ключ если требуется
        if provider_config.get("api_key_required", False):
            env_var = provider_config.get("env_var")
            if env_var and not os.getenv(env_var):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"API key required for {provider_name}. Set {env_var} environment variable.",
                        }
                    ),
                    400,
                )

        # Пытаемся импортировать и протестировать провайдер
        try:
            from events.events_parser import EventsParser

            parser = EventsParser()

            # Ищем провайдер в загруженных провайдерах
            provider_key = f"{provider_category}_{provider_name}"

            if provider_key not in parser.providers:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Provider {provider_name} is not loaded. Check if provider file exists.",
                        }
                    ),
                    400,
                )

            # Тестируем провайдер на ближайшие 7 дней
            from datetime import datetime, timedelta

            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)

            import asyncio

            # Запускаем асинхронный тест
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                events = loop.run_until_complete(parser.providers[provider_key].fetch_events(start_date, end_date))

                # Берем первые 3 события как примеры
                sample_events = []
                for event in events[:3]:
                    sample_events.append(
                        {
                            "title": event.title,
                            "date": event.date.isoformat() if event.date else None,
                            "category": event.category,
                            "description": (
                                event.description[:100] + "..."
                                if event.description and len(event.description) > 100
                                else event.description
                            ),
                        }
                    )

                return jsonify(
                    {
                        "success": True,
                        "events_found": len(events),
                        "sample_events": sample_events,
                        "message": f"Successfully fetched {len(events)} events from {provider_name}",
                        "provider_info": {
                            "name": provider_name,
                            "category": provider_category,
                            "description": provider_config.get("description", ""),
                            "api_key_required": provider_config.get("api_key_required", False),
                        },
                    }
                )

            finally:
                loop.close()

        except Exception as provider_error:
            logger.error(f"Error testing provider {provider_name}: {provider_error}")
            return jsonify({"success": False, "error": f"Provider test failed: {str(provider_error)}"}), 500

    except Exception as e:
        logger.error(f"Failed to test provider: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== System Health ====================


@admin_bp.route("/system/health", methods=["GET"])
@require_admin
@cached(ttl=10)  # Cache system health for 10 seconds
def get_system_health():
    """
    Комплексное здоровье системы (Phase 2)

    Returns:
        JSON: {
            processes: {flask, bot, cloudflare},
            resources: {cpu, memory, disk},
            api_health: {database_latency_ms},
            uptime: {flask_uptime_seconds}
        }
    """
    try:
        import psutil
        import time

        logger.info("Getting system health...")

        # 1. Process Monitoring - ищем по команде
        def check_process_by_command(command_contains):
            try:
                for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                    try:
                        if proc.info["cmdline"] and any(command_contains in cmd for cmd in proc.info["cmdline"]):
                            return {
                                "status": "running",
                                "pid": proc.info["pid"],
                                "uptime_seconds": int(time.time() - proc.info["create_time"]),
                            }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                logger.warning(f"Error checking process by command: {e}")
            return {"status": "stopped", "pid": None, "uptime_seconds": 0}

        flask_status = check_process_by_command("src/webapp.py")
        bot_status = check_process_by_command("telegram_bot")

        # Cloudflare status (check logfile)
        cloudflare_status = {"status": "unknown"}
        try:
            if os.path.exists("logs/cloudflare.log"):
                with open("logs/cloudflare.log", "r") as f:
                    lines = f.readlines()[-10:]
                    if any("https://" in line for line in lines):
                        cloudflare_status = {"status": "running"}
        except Exception as e:
            logger.warning(f"Error reading cloudflare log: {e}")

        # 2. Resource Monitoring
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        resources = {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1),
            "memory_mb": int(memory.used / 1024 / 1024),
            "disk_percent": round(disk.percent, 1),
        }

        # 3. Database Health
        db = get_sync_service()
        start = time.time()
        try:
            db.safe_execute(db.sync_client.table("users").select("id").limit(1))
            db_latency_ms = round((time.time() - start) * 1000, 2)
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            db_latency_ms = -1

        return jsonify(
            {
                "processes": {"flask": flask_status, "bot": bot_status, "cloudflare": cloudflare_status},
                "resources": resources,
                "api_health": {"database_latency_ms": db_latency_ms},
                "uptime": {"flask_uptime_seconds": flask_status["uptime_seconds"]},
            }
        )

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/system/status", methods=["GET"])
@require_admin
def get_system_status():
    """
    Мониторинг статуса сервисов и системных ресурсов.

    Returns:
        JSON: { services: {...}, resources: {...}, uptime: ... }
    """
    try:
        logger.info("Getting system status...")
        import psutil
        import os
        from datetime import datetime, timedelta

        # Проверяем процессы
        flask_pid_file = ".flask.pid"
        bot_pid_file = ".bot.pid"

        flask_running = os.path.exists(flask_pid_file)
        bot_running = os.path.exists(bot_pid_file)

        # Проверяем БД через ping
        db_status = "ok"
        try:
            db = get_sync_service()
            db.safe_execute(db.sync_client.table("users").select("id").limit(1))
        except Exception as e:
            logger.warning(f"DB health check failed: {e}")
            db_status = "error"

        # Системные ресурсы
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Uptime (время работы процесса Python)
        process = psutil.Process(os.getpid())
        create_time = datetime.fromtimestamp(process.create_time())
        uptime_seconds = (datetime.now() - create_time).total_seconds()
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))

        return jsonify(
            {
                "services": {
                    "flask": {
                        "running": flask_running,
                        "status": "ok" if flask_running else "down",
                        "pid_file": flask_pid_file,
                    },
                    "bot": {
                        "running": bot_running,
                        "status": "ok" if bot_running else "down",
                        "pid_file": bot_pid_file,
                    },
                    "database": {"running": True, "status": db_status},
                },
                "resources": {
                    "cpu_percent": round(cpu, 1),
                    "memory_percent": round(memory.percent, 1),
                    "memory_used_mb": round(memory.used / 1024 / 1024, 0),
                    "memory_available_mb": round(memory.available / 1024 / 1024, 0),
                    "disk_percent": round(disk.percent, 1),
                    "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 1),
                },
                "uptime": uptime_str,
                "uptime_seconds": int(uptime_seconds),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/config", methods=["POST"])
@require_admin
def update_config():
    """
    Обновить конфигурацию системы.

    Request body:
        JSON: { ai_settings: {...}, system_settings: {...} }

    Returns:
        JSON: { status: 'success', message: '...' }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # TODO: Реализовать сохранение конфигурации
        # Для MVP возвращаем success
        logger.info(f"Config update requested by admin {g.admin_id}: {data}")

        return jsonify(
            {
                "status": "success",
                "message": "Configuration update received (not implemented yet)",
                "updated_by": g.admin_id,
            }
        )

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return jsonify({"error": "Failed to update configuration"}), 500


# ==================== RSS Parser Metrics ====================


@admin_bp.route("/metrics/rss-parser", methods=["GET"])
@require_admin
@cached(ttl=60)  # Cache RSS parser metrics for 1 minute
def get_rss_parser_metrics():
    """
    RSS парсер метрики: производительность, источники, AI экономия.

    Query params:
        hours: int - период анализа в часах (default: 24)

    Returns:
        JSON: {
            sources_status: [{source, success_rate, avg_duration, last_success}],
            performance: {total_requests, avg_duration_ms, success_rate},
            ai_optimization: {token_savings, cost_savings_usd, local_predictions},
            errors: [{error_type, count, last_occurrence}],
            cache_stats: {hit_rate, size_mb}
        }
    """
    try:
        hours = int(request.args.get("hours", 24))
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        logger.info(f"Getting RSS parser metrics for last {hours} hours...")
        db = get_sync_service()

        # Получаем новости за период как proxy для RSS активности
        news_result = db.safe_execute(
            db.sync_client.table("news")
            .select("source, published_at, importance, credibility")
            .gte("published_at", since_time)
            .limit(10000)
        )

        news_data = news_result.data or []

        # Анализируем источники
        from collections import defaultdict

        source_stats = defaultdict(
            lambda: {"total": 0, "success": 0, "errors": 0, "total_importance": 0, "total_credibility": 0}
        )

        for item in news_data:
            source = item.get("source", "unknown")
            source_stats[source]["total"] += 1
            source_stats[source]["success"] += 1

            # AI оценки как индикатор успешной обработки
            if item.get("importance") is not None:
                source_stats[source]["total_importance"] += float(item["importance"])
            if item.get("credibility") is not None:
                source_stats[source]["total_credibility"] += float(item["credibility"])

        # Формируем статус источников
        sources_status = []
        for source, stats in source_stats.items():
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                avg_importance = stats["total_importance"] / stats["success"] if stats["success"] > 0 else 0
                avg_credibility = stats["total_credibility"] / stats["success"] if stats["success"] > 0 else 0

                sources_status.append(
                    {
                        "source": source,
                        "success_rate": round(success_rate, 1),
                        "items_processed": stats["success"],
                        "avg_importance": round(avg_importance, 2),
                        "avg_credibility": round(avg_credibility, 2),
                        "status": "healthy" if success_rate > 80 else "degraded" if success_rate > 50 else "error",
                    }
                )

        sources_status.sort(key=lambda x: x["items_processed"], reverse=True)

        # Общая производительность
        total_processed = len(news_data)
        success_rate = 100.0  # Предполагаем, что сохраненные новости = успешно обработанные

        # AI оптимизация (примерные расчеты)
        total_with_ai = len([n for n in news_data if n.get("importance") is not None])

        # Оценка экономии (60-70% запросов обрабатывается локально)
        estimated_total_requests = total_with_ai / 0.35  # 35% идет в OpenAI
        estimated_saved_requests = estimated_total_requests - total_with_ai
        estimated_tokens_saved = estimated_saved_requests * 500  # ~500 токенов на запрос
        estimated_cost_savings = (estimated_tokens_saved / 1_000_000) * 0.15  # $0.15/1M tokens

        performance = {
            "total_processed": total_processed,
            "success_rate": success_rate,
            "avg_processing_time_ms": 2000,  # Примерное значение
            "period_hours": hours,
        }

        ai_optimization = {
            "total_ai_requests": total_with_ai,
            "estimated_saved_requests": int(estimated_saved_requests),
            "estimated_tokens_saved": int(estimated_tokens_saved),
            "estimated_cost_savings_usd": round(estimated_cost_savings, 4),
            "local_prediction_rate": (
                round((estimated_saved_requests / estimated_total_requests) * 100, 1)
                if estimated_total_requests > 0
                else 0
            ),
        }

        # Ошибки (пока заглушка, в будущем можно парсить логи)
        errors = [
            {"error_type": "HTTP timeout", "count": 0, "last_occurrence": None},
            {"error_type": "Connection error", "count": 0, "last_occurrence": None},
            {"error_type": "Parse error", "count": 0, "last_occurrence": None},
        ]

        # Cache статистика (заглушка)
        cache_stats = {
            "hit_rate": 65.0,  # В будущем реальные данные
            "size_mb": 128.5,
            "total_requests": int(estimated_total_requests),
        }

        return jsonify(
            {
                "sources_status": sources_status[:20],  # Top 20 источников
                "performance": performance,
                "ai_optimization": ai_optimization,
                "errors": errors,
                "cache_stats": cache_stats,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get RSS parser metrics: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/metrics/rss-parser/live", methods=["GET"])
@require_admin
def get_rss_parser_live_metrics():
    """
    Live метрики RSS парсера для real-time мониторинга.

    Returns:
        JSON: {
            current_sources_processing: int,
            last_successful_fetch: timestamp,
            errors_last_hour: int,
            ai_requests_last_hour: int
        }
    """
    try:
        db = get_sync_service()

        # Последний час активности
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

        # Новости за последний час
        recent_news = db.safe_execute(
            db.sync_client.table("news").select("source, published_at").gte("published_at", hour_ago).limit(1000)
        )

        news_count = len(recent_news.data) if recent_news.data else 0

        # Уникальные источники за последний час
        active_sources = set()
        if recent_news.data:
            for item in recent_news.data:
                active_sources.add(item.get("source", "unknown"))

        # Последняя успешная обработка (последняя запись в базе)
        last_success = None
        if recent_news.data:
            last_item = max(recent_news.data, key=lambda x: x.get("published_at", ""))
            last_success = last_item.get("published_at")

        return jsonify(
            {
                "current_sources_processing": len(active_sources),
                "news_last_hour": news_count,
                "last_successful_fetch": last_success,
                "status": "active" if news_count > 0 else "idle",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get live RSS metrics: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== News Fetching Control ====================


@admin_bp.route("/news/start-fetch", methods=["POST"])
@require_admin
def start_news_fetch():
    """
    Запустить загрузку новостей с настройками.

    Request body:
        JSON: {
            max_concurrent: int,
            min_importance: float,
            per_subcategory: int,
            force_train: bool,
            skip_train: bool,
            categories: [str],
            subcategories: [str]
        }

    Returns:
        JSON: { success: bool, process_id: str, message: str }
    """
    try:
        data = request.get_json() or {}

        # Параметры по умолчанию
        max_concurrent = data.get("max_concurrent", 10)
        force_train = data.get("force_train", False)
        skip_train = data.get("skip_train", False)
        categories = data.get("categories", [])
        subcategories = data.get("subcategories", [])

        logger.info(f"Starting news fetch with params: {data}")

        # Формируем команду
        import subprocess
        import os
        import time

        cmd = [
            "python3",
            "tools/news/fetch_and_train.py",
            "--max-concurrent",
            str(max_concurrent),
        ]

        if force_train:
            cmd.append("--force-train")
        if skip_train:
            cmd.append("--skip-train")

        # Добавляем фильтры категорий если указаны
        if categories:
            cmd.extend(["--categories", ",".join(categories)])
        if subcategories:
            cmd.extend(["--subcategories", ",".join(subcategories)])

        # Запускаем в фоне
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Сохраняем PID процесса
            pid_file = f"logs/fetch_{int(time.time())}.pid"
            os.makedirs("logs", exist_ok=True)
            with open(pid_file, "w") as f:
                f.write(str(process.pid))

            logger.info(f"News fetch started with PID: {process.pid}")

            return jsonify(
                {
                    "success": True,
                    "process_id": str(process.pid),
                    "message": f"Загрузка новостей запущена (PID: {process.pid})",
                    "pid_file": pid_file,
                }
            )

        except Exception as e:
            logger.error(f"Failed to start news fetch: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    except Exception as e:
        logger.error(f"Error in start_news_fetch: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/stop-fetch", methods=["POST"])
@require_admin
def stop_news_fetch():
    """
    Остановить загрузку новостей.

    Returns:
        JSON: { success: bool, message: str }
    """
    try:
        import subprocess
        import glob
        import os

        # Ищем процессы fetch_and_train
        try:
            subprocess.run(["pkill", "-f", "fetch_and_train.py"], capture_output=True, text=True, check=False)

            # Удаляем PID файлы
            pid_files = glob.glob("logs/fetch_*.pid")
            for pid_file in pid_files:
                try:
                    os.remove(pid_file)
                except Exception:
                    pass

            logger.info("News fetch processes stopped")

            return jsonify({"success": True, "message": "Процессы загрузки новостей остановлены"})

        except Exception as e:
            logger.error(f"Failed to stop news fetch: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    except Exception as e:
        logger.error(f"Error in stop_news_fetch: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/status", methods=["GET"])
@require_admin
def get_news_fetch_status():
    """
    Получить статус процессов загрузки новостей.

    Returns:
        JSON: {
            running: bool,
            processes: [{pid, command, start_time}],
            last_run: timestamp,
            processed_stats: {
                total_processed: int,
                last_hour: int,
                current_session: int
            }
        }
    """
    try:
        import glob
        import os
        import psutil

        # Ищем процессы fetch_and_train
        processes = []
        running = False

        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                try:
                    if proc.info["cmdline"] and any("fetch_and_train.py" in str(cmd) for cmd in proc.info["cmdline"]):
                        processes.append(
                            {
                                "pid": proc.info["pid"],
                                "command": " ".join(str(cmd) for cmd in proc.info["cmdline"]),
                                "start_time": proc.info["create_time"],
                            }
                        )
                        running = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.warning(f"Error checking processes: {e}")

        # Последний запуск из логов
        last_run = None
        try:
            log_files = glob.glob("logs/fetch_and_train.log")
            if log_files:
                latest_log = max(log_files, key=os.path.getmtime)
                if os.path.exists(latest_log):
                    stat = os.stat(latest_log)
                    last_run = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            logger.debug(f"Error getting last run time: {e}")

        # Статистика обработанных новостей
        processed_stats = {"total_processed": 0, "last_hour": 0, "current_session": 0}
        try:
            from database.service import get_sync_service

            db = get_sync_service()

            # Общее количество новостей
            total_result = db.safe_execute(db.sync_client.table("news").select("id", count="exact"))
            processed_stats["total_processed"] = total_result.count if total_result else 0

            # Пытаемся использовать created_at (время добавления в БД), fallback на published_at
            hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

            try:
                # Пробуем использовать created_at
                recent_result = db.safe_execute(
                    db.sync_client.table("news").select("id", count="exact").gte("created_at", hour_ago)
                )
                processed_stats["last_hour"] = recent_result.count if recent_result else 0
            except Exception:
                # Fallback на published_at если created_at недоступен
                recent_result = db.safe_execute(
                    db.sync_client.table("news").select("id", count="exact").gte("published_at", hour_ago)
                )
                processed_stats["last_hour"] = recent_result.count if recent_result else 0

            # За последние 10 минут
            ten_minutes_ago = (datetime.now() - timedelta(minutes=10)).isoformat()
            try:
                session_result = db.safe_execute(
                    db.sync_client.table("news").select("id", count="exact").gte("created_at", ten_minutes_ago)
                )
                processed_stats["current_session"] = session_result.count if session_result else 0
            except Exception:
                # Fallback на published_at
                session_result = db.safe_execute(
                    db.sync_client.table("news").select("id", count="exact").gte("published_at", ten_minutes_ago)
                )
                processed_stats["current_session"] = session_result.count if session_result else 0

            # Логируем для отладки
            logger.info(
                f"News stats: total={processed_stats['total_processed']}, "
                f"last_hour={processed_stats['last_hour']}, "
                f"session={processed_stats['current_session']}"
            )

        except Exception as e:
            logger.error(f"Error getting processed stats: {e}")
            # Fallback to basic stats if database query fails
            processed_stats = {"total_processed": 0, "last_hour": 0, "current_session": 0}

        return jsonify(
            {"running": running, "processes": processes, "last_run": last_run, "processed_stats": processed_stats}
        )

    except Exception as e:
        logger.error(f"Error in get_news_fetch_status: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/config", methods=["GET"])
@require_admin
def get_news_fetch_config():
    """
    Получить текущие настройки загрузки новостей.

    Returns:
        JSON: { settings: {...}, available_options: {...} }
    """
    try:
        from config.core.settings import AI_MODEL_SUMMARY

        # Читаем конфигурацию из файлов
        config = {
            "default_max_concurrent": 10,
            "default_min_importance": 0.1,
            "default_per_subcategory": 50,
            "ai_model": AI_MODEL_SUMMARY,
            "available_categories": [],
            "available_subcategories": [],
        }

        # Получаем доступные категории и субкатегории
        try:
            from services.categories import get_category_structure

            structure = get_category_structure()

            categories = list(structure.keys())
            subcategories = []
            category_structure = {}

            for category, cat_data in structure.items():
                if isinstance(cat_data, dict):
                    cat_subcats = []
                    for subcat_name, subcat_data in cat_data.items():
                        if isinstance(subcat_data, dict) and "sources" in subcat_data:
                            cat_subcats.append(subcat_name)
                            subcategories.append(subcat_name)
                    category_structure[category] = cat_subcats

            config["available_categories"] = categories
            config["available_subcategories"] = subcategories
            config["category_structure"] = category_structure

        except Exception as e:
            logger.warning(f"Error getting category structure: {e}")

        return jsonify(
            {
                "settings": config,
                "available_options": {
                    "max_concurrent": {"min": 1, "max": 50, "default": 10},
                    "min_importance": {"min": 0.0, "max": 1.0, "default": 0.1, "step": 0.1},
                    "per_subcategory": {"min": 1, "max": 500, "default": 50},
                },
            }
        )

    except Exception as e:
        logger.error(f"Error in get_news_fetch_config: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/live-stats", methods=["GET"])
@require_admin
def get_news_live_stats():
    """
    Real-time статистика парсинга из состояния прогресса.

    Returns:
        JSON: {
            "sources_total": 255,
            "sources_processed": 45,
            "progress_percent": 17.6,
            "news_found": 1234,
            "news_saved": 890,
            "news_filtered": 344,
            "errors_count": 3,
            "current_source": "bitcoinmagazine.com",
            "eta_seconds": 480,
            "top_sources": [...],
            "recent_errors": [...],
            "category_stats": [...],
            "ai_stats": {...},
            "timestamp": "2025-10-21T12:42:24Z"
        }
    """
    try:
        # Импортируем функцию состояния прогресса
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

        try:
            from tools.news.progress_state import get_progress_state

            # Получаем состояние из JSON файла
            stats = get_progress_state()
            logger.info(f"Debug: sources_total = {stats.get('sources_total')}")
            return jsonify(stats)
        except ImportError as e:
            logger.error(f"Error importing progress_state module: {e}")
            # Fallback: парсим из логов если модуль недоступен
            return get_news_live_stats_from_logs()

    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        return jsonify({"error": str(e)}), 500


def _complete_stats_from_logs(log_data):
    """Дополняет данные из логов недостающими полями для полной структуры API"""
    # Базовые значения по умолчанию
    default_stats = {
        "news_found": 0,
        "news_saved": 0,
        "news_filtered": 0,
        "errors_count": 0,
        "current_source": "",
        "eta_seconds": 0,
        "top_sources": [],
        "recent_errors": [],
        "category_stats": [],
        "ai_stats": {
            "local_predictions": 0,
            "openai_calls": 0,
            "local_percent": 0,
            "tokens_saved": 0,
            "estimated_cost": 0,
            "cost_saved": 0,
        },
    }

    # Вычисляем недостающие поля если их нет
    if "sources_remaining" not in log_data and "sources_total" in log_data and "sources_processed" in log_data:
        log_data["sources_remaining"] = log_data["sources_total"] - log_data["sources_processed"]

    if "progress_percent" not in log_data and "sources_total" in log_data and "sources_processed" in log_data:
        if log_data["sources_total"] > 0:
            log_data["progress_percent"] = round((log_data["sources_processed"] / log_data["sources_total"]) * 100, 1)
        else:
            log_data["progress_percent"] = 0

    # Добавляем недостающие поля
    for key, default_value in default_stats.items():
        if key not in log_data:
            log_data[key] = default_value

    # Убеждаемся что timestamp есть
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now().isoformat()

    return log_data


def get_news_live_stats_from_logs():
    """Fallback: получает статистику из последних JSON логов"""
    try:
        log_file = "logs/fetch_and_train.log"
        if not os.path.exists(log_file):
            return jsonify(
                {
                    "sources_total": 0,
                    "sources_processed": 0,
                    "progress_percent": 0,
                    "news_found": 0,
                    "news_saved": 0,
                    "news_filtered": 0,
                    "errors_count": 0,
                    "current_source": "",
                    "eta_seconds": 0,
                    "top_sources": [],
                    "recent_errors": [],
                    "category_stats": [],
                    "ai_stats": {
                        "local_predictions": 0,
                        "openai_calls": 0,
                        "local_percent": 0,
                        "tokens_saved": 0,
                        "estimated_cost": 0,
                        "cost_saved": 0,
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Читаем последние 500 строк для поиска JSON логов
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Ищем последний JSON лог с различными событиями
        latest_progress = None
        logger.info(f"Debug fallback: Ищем в {len(lines)} строках лога")

        for line in reversed(lines[-500:]):
            # Ищем parsing_progress, fetch_started, sources_initialized или fetch_completed
            if any(
                event in line
                for event in [
                    '"event": "parsing_progress"',
                    '"event": "sources_initialized"',
                    '"event": "fetch_started"',
                    '"event": "fetch_completed"',
                ]
            ):
                try:
                    # Извлекаем JSON из строки лога
                    json_start = line.find("{")
                    if json_start != -1:
                        json_part = line[json_start:]
                        latest_progress = json.loads(json_part)
                        logger.info(
                            f"Debug fallback: Найден {latest_progress.get('event')} с sources_total={latest_progress.get('sources_total')}"
                        )
                        # Приоритет: parsing_progress > sources_initialized > fetch_completed > fetch_started
                        if latest_progress.get("event") == "parsing_progress":
                            logger.info("Debug fallback: Найден parsing_progress, используем его")
                            break
                        elif (
                            latest_progress.get("event") == "sources_initialized"
                            and latest_progress.get("sources_total", 0) > 0
                        ):
                            logger.info(
                                "Debug fallback: Найден sources_initialized с sources_total > 0, используем его"
                            )
                            break
                        elif (
                            latest_progress.get("event") == "fetch_completed"
                            and latest_progress.get("sources_total", 0) > 0
                        ):
                            logger.info("Debug fallback: Найден fetch_completed с sources_total > 0, используем его")
                            break
                        elif (
                            latest_progress.get("event") == "fetch_started"
                            and latest_progress.get("sources_total", 0) > 0
                        ):
                            logger.info("Debug fallback: Найден fetch_started с sources_total > 0, используем его")
                            break
                except json.JSONDecodeError:
                    continue

        if latest_progress and latest_progress.get("sources_total", 0) > 0:
            logger.info(
                f"Debug fallback: Возвращаем данные из логов: {latest_progress.get('sources_total')} источников"
            )
            # Дополняем недостающие поля
            complete_data = _complete_stats_from_logs(latest_progress.copy())
            return jsonify(complete_data)
        elif latest_progress:
            logger.info(f"Debug fallback: Найден лог, но sources_total={latest_progress.get('sources_total')}")
            # Дополняем недостающие поля даже для источников с 0
            complete_data = _complete_stats_from_logs(latest_progress.copy())
            return jsonify(complete_data)
        else:
            # Возвращаем пустую статистику
            return jsonify(
                {
                    "sources_total": 0,
                    "sources_processed": 0,
                    "progress_percent": 0,
                    "news_found": 0,
                    "news_saved": 0,
                    "news_filtered": 0,
                    "errors_count": 0,
                    "current_source": "",
                    "eta_seconds": 0,
                    "top_sources": [],
                    "recent_errors": [],
                    "category_stats": [],
                    "ai_stats": {
                        "local_predictions": 0,
                        "openai_calls": 0,
                        "local_percent": 0,
                        "tokens_saved": 0,
                        "estimated_cost": 0,
                        "cost_saved": 0,
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

    except Exception as e:
        logger.error(f"Error parsing logs for live stats: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/logs", methods=["GET"])
@require_admin
def get_news_fetch_logs():
    """
    Получить логи загрузки новостей.

    Query params:
        lines: int - количество последних строк (default: 100)

    Returns:
        JSON: { logs: [...], file: str }
    """
    try:
        lines = int(request.args.get("lines", 100))

        # Ищем лог файлы
        import glob

        log_files = glob.glob("logs/fetch_and_train.log") + glob.glob("logs/fetch_*.log")

        if not log_files:
            return jsonify({"logs": [], "file": "none", "message": "Лог файлы не найдены"})

        # Берем самый свежий
        latest_log = max(log_files, key=lambda f: os.path.getmtime(f))

        try:
            with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            logs = []
            for line in last_lines:
                logs.append(
                    {"text": line.strip(), "timestamp": datetime.now().isoformat()}  # TODO: парсить реальный timestamp
                )

            return jsonify({"logs": logs, "file": os.path.basename(latest_log), "total_lines": len(all_lines)})

        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return jsonify({"error": str(e)}), 500

    except Exception as e:
        logger.error(f"Error in get_news_fetch_logs: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/pause", methods=["POST"])
@require_admin
def pause_news_fetch():
    """
    Пауза/возобновление загрузки новостей.

    Request body:
        JSON: { "action": "pause" | "resume" }

    Returns:
        JSON: { success: bool, message: str }
    """
    try:
        data = request.get_json() or {}
        action = data.get("action")

        if action not in ["pause", "resume"]:
            return jsonify({"error": "Action must be 'pause' or 'resume'"}), 400

        # TODO: Реализовать паузу через сигналы или файл-флаг
        # Пока возвращаем success для UI
        message = "Пауза" if action == "pause" else "Возобновление"
        return jsonify({"success": True, "message": f"{message} парсинга новостей", "action": action})

    except Exception as e:
        logger.error(f"Error in pause_news_fetch: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/skip-source", methods=["POST"])
@require_admin
def skip_current_source():
    """
    Пропустить текущий источник.

    Returns:
        JSON: { success: bool, message: str }
    """
    try:
        # TODO: Реализовать пропуск через сигналы
        return jsonify({"success": True, "message": "Пропуск текущего источника"})

    except Exception as e:
        logger.error(f"Error in skip_current_source: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/export-stats", methods=["GET"])
@require_admin
def export_news_stats():
    """
    Экспорт статистики парсинга в JSON.

    Returns:
        JSON файл с полной статистикой
    """
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

        try:
            from tools.news.fetch_and_train import get_progress_state

            stats = get_progress_state()

            # Добавляем дополнительную информацию
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "live_stats": stats,
                "system_info": {"python_version": sys.version, "platform": os.name},
            }

            return jsonify(export_data)

        except ImportError:
            return jsonify({"error": "Statistics not available", "message": "Unable to load current statistics"}), 500

    except Exception as e:
        logger.error(f"Error exporting stats: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/news/recent-runs", methods=["GET"])
@require_admin
def get_recent_runs():
    """
    Получить историю последних запусков парсинга.

    Returns:
        JSON: { runs: [...] }
    """
    try:
        # Парсим логи для поиска запусков
        log_file = "logs/fetch_and_train.log"
        runs = []

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # Ищем начала и концы сессий
            current_run = None
            for line in lines:
                if "fetch_started" in line or "Запуск умного парсинга" in line:
                    if current_run:
                        runs.append(current_run)

                    # Парсим время начала
                    try:
                        timestamp_part = line.split(" - ")[0]
                        current_run = {
                            "id": len(runs) + 1,
                            "started_at": timestamp_part,
                            "status": "running",
                            "sources_total": 0,
                            "sources_processed": 0,
                            "news_saved": 0,
                            "duration": 0,
                        }
                    except Exception:
                        current_run = {
                            "id": len(runs) + 1,
                            "started_at": datetime.now().isoformat(),
                            "status": "running",
                            "sources_total": 0,
                            "sources_processed": 0,
                            "news_saved": 0,
                            "duration": 0,
                        }

                elif current_run and ("fetch_completed" in line or "Парсинг завершен" in line):
                    current_run["status"] = "completed"
                    try:
                        timestamp_part = line.split(" - ")[0]
                        # Вычисляем длительность
                        start_time = datetime.fromisoformat(current_run["started_at"].replace("Z", "+00:00"))
                        end_time = datetime.fromisoformat(timestamp_part.replace("Z", "+00:00"))
                        current_run["duration"] = int((end_time - start_time).total_seconds())
                    except Exception:
                        current_run["duration"] = 0

                elif current_run and '"event": "parsing_progress"' in line:
                    try:
                        json_start = line.find("{")
                        if json_start != -1:
                            json_part = line[json_start:]
                            progress_data = json.loads(json_part)
                            current_run.update(
                                {
                                    "sources_total": progress_data.get("sources_total", current_run["sources_total"]),
                                    "sources_processed": progress_data.get(
                                        "sources_processed", current_run["sources_processed"]
                                    ),
                                    "news_saved": progress_data.get("news_saved", current_run["news_saved"]),
                                }
                            )
                    except Exception:
                        pass

            if current_run:
                runs.append(current_run)

        # Возвращаем последние 10 запусков
        return jsonify({"runs": runs[-10:] if runs else []})

    except Exception as e:
        logger.error(f"Error getting recent runs: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Events Control ====================


@admin_bp.route("/events/start-fetch", methods=["POST"])
@require_admin
def start_events_fetch():
    """
    Запустить загрузку событий с настройками.

    Request body:
        JSON: {
            days_ahead: int,
            categories: [str],
            providers: [str],
            dry_run: bool
        }

    Returns:
        JSON: { success: bool, process_id: str, message: str }
    """
    try:
        data = request.get_json() or {}

        # Параметры по умолчанию
        days_ahead = data.get("days_ahead", 7)
        dry_run = data.get("dry_run", False)
        categories = data.get("categories", [])
        providers = data.get("providers", [])

        # Валидация параметров
        if not isinstance(days_ahead, int) or days_ahead < 1 or days_ahead > 30:
            return jsonify({"success": False, "error": "days_ahead должно быть от 1 до 30"}), 400

        # Проверяем, не запущен ли уже процесс
        running_processes = []
        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] == "python3" and proc.info["cmdline"]:
                        cmdline = " ".join(proc.info["cmdline"])
                        if "tools/events/fetch_events.py" in cmdline:
                            running_processes.append(proc.info["pid"])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception:
            pass

        if running_processes:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Процесс загрузки событий уже запущен (PID: {', '.join(map(str, running_processes))})",
                    }
                ),
                409,
            )

        # Строим команду
        cmd = [sys.executable, "tools/events/fetch_events.py"]

        if days_ahead != 7:
            cmd.extend(["--days", str(days_ahead)])

        if dry_run:
            cmd.append("--dry-run")

        if categories:
            cmd.extend(["--categories"] + categories)

        if providers:
            cmd.extend(["--providers"] + providers)

        # Запускаем процесс с переменными окружения
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        logger.info(f"Starting events fetch with command: {' '.join(cmd)}")
        logger.info(f"Working directory: {os.getcwd()}")

        # Перенаправляем stdout/stderr в лог файлы для отладки
        stdout_file = open("logs/fetch_events_stdout.log", "w")
        stderr_file = open("logs/fetch_events_stderr.log", "w")
        try:
            process = subprocess.Popen(cmd, stdout=stdout_file, stderr=stderr_file, cwd=os.getcwd(), env=env)
        finally:
            # Закрываем файлы после запуска процесса
            stdout_file.close()
            stderr_file.close()

        # Сохраняем PID
        pid_file = "logs/fetch_events.pid"
        os.makedirs("logs", exist_ok=True)
        with open(pid_file, "w") as f:
            f.write(str(process.pid))

        logger.info(f"Started events fetch process: PID {process.pid}, command: {' '.join(cmd)}")

        return jsonify(
            {
                "success": True,
                "process_id": str(process.pid),
                "message": f"Загрузка событий запущена (PID: {process.pid})",
            }
        )

    except Exception as e:
        logger.error(f"Error starting events fetch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/events/stop-fetch", methods=["POST"])
@require_admin
def stop_events_fetch():
    """
    Остановить загрузку событий.

    Returns:
        JSON: { success: bool, message: str }
    """
    try:
        # Ищем и останавливаем процессы fetch_events.py
        result = subprocess.run(["pkill", "-f", "fetch_events.py"], capture_output=True, text=True, check=False)
        logger.info(f"pkill command result: returncode={result.returncode}, stderr={result.stderr}")

        # Удаляем PID файлы
        pid_files = glob.glob("logs/fetch_events.pid")
        for pid_file in pid_files:
            try:
                os.remove(pid_file)
                logger.info(f"Removed PID file: {pid_file}")
            except Exception as e:
                logger.warning(f"Could not remove PID file {pid_file}: {e}")

        logger.info("Events fetch processes stopped")
        return jsonify({"success": True, "message": "Процессы загрузки событий остановлены"})

    except Exception as e:
        logger.error(f"Error stopping events fetch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/events/status", methods=["GET"])
@require_admin
def get_events_fetch_status():
    """
    Получить статус загрузки событий.

    Returns:
        JSON: { running: bool, processes: [...], last_run: str, events_stats: {...} }
    """
    try:
        processes = []

        # Сначала проверим PID файл для быстрого определения статуса
        pid_file = "logs/fetch_events.pid"
        pid_from_file = None
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid_from_file = int(f.read().strip())
            except (ValueError, OSError):
                pass

        # Поиск запущенных процессов fetch_events.py
        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                if proc.info["name"] == "python3" and proc.info["cmdline"]:
                    cmdline = " ".join(proc.info["cmdline"])
                    if "tools/events/fetch_events.py" in cmdline:
                        processes.append(
                            {"pid": proc.info["pid"], "command": cmdline, "start_time": proc.info["create_time"]}
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Если нет процессов в psutil, но есть PID файл, попробуем проверить процесс
        if not processes and pid_from_file:
            try:
                proc = psutil.Process(pid_from_file)
                if proc.is_running():
                    proc_info = proc.as_dict(["name", "cmdline", "create_time"])
                    if proc_info.get("name") == "python3":
                        cmdline = " ".join(proc_info.get("cmdline", []))
                        if "tools/events/fetch_events.py" in cmdline:
                            processes.append(
                                {"pid": pid_from_file, "command": cmdline, "start_time": proc_info["create_time"]}
                            )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        running = len(processes) > 0

        # Время последнего запуска из логов
        last_run = None
        try:
            log_file = "logs/events_fetch.log"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    for line in reversed(lines[-100:]):  # Последние 100 строк
                        if "Starting event fetch:" in line:
                            # Извлечь timestamp из строки лога
                            try:
                                timestamp_part = line.split(" - ")[0]
                                last_run = timestamp_part
                                break
                            except Exception:
                                pass
        except Exception as e:
            logger.warning(f"Could not read events log: {e}")

        # Статистика событий из базы данных
        events_stats = {"total_events": 0, "last_hour": 0, "upcoming_count": 0}
        try:
            from database.db_models import supabase

            if supabase:
                # Общее количество событий
                total_response = supabase.table("events_new").select("id", count="exact").execute()
                events_stats["total_events"] = total_response.count or 0

                # События за последний час - используем created_at с fallback на starts_at
                from datetime import datetime, timezone, timedelta

                one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
                try:
                    # Пробуем использовать created_at
                    hour_response = (
                        supabase.table("events_new")
                        .select("id", count="exact")
                        .gte("created_at", one_hour_ago.isoformat())
                        .execute()
                    )
                    events_stats["last_hour"] = hour_response.count or 0
                except Exception:
                    # Fallback на starts_at если created_at недоступен
                    hour_response = (
                        supabase.table("events_new")
                        .select("id", count="exact")
                        .gte("starts_at", one_hour_ago.isoformat())
                        .execute()
                    )
                    events_stats["last_hour"] = hour_response.count or 0

                # Предстоящие события (следующие 24 часа)
                now = datetime.now(timezone.utc)
                tomorrow = now + timedelta(days=1)
                upcoming_response = (
                    supabase.table("events_new")
                    .select("id", count="exact")
                    .gte("starts_at", now.isoformat())
                    .lte("starts_at", tomorrow.isoformat())
                    .execute()
                )
                events_stats["upcoming_count"] = upcoming_response.count or 0

        except Exception as e:
            logger.warning(f"Could not fetch events stats: {e}")

        return jsonify({"running": running, "processes": processes, "last_run": last_run, "events_stats": events_stats})

    except Exception as e:
        logger.error(f"Error getting events fetch status: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/events/config", methods=["GET"])
@require_admin
def get_events_fetch_config():
    """
    Получить конфигурацию для загрузки событий.

    Returns:
        JSON: { settings: {...}, available_options: {...} }
    """
    try:
        import yaml
        from pathlib import Path

        # Загрузка конфигурации событий
        config_path = Path("config/data/sources_events.yaml")
        available_categories = []
        available_providers = {}

        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            for category, providers in config.items():
                available_categories.append(category)
                provider_list = []
                for provider_name, provider_config in providers.items():
                    provider_list.append({"name": provider_name, "enabled": provider_config.get("enabled", False)})
                available_providers[category] = provider_list

        return jsonify(
            {
                "settings": {
                    "default_days_ahead": 7,
                    "available_categories": available_categories,
                    "available_providers": available_providers,
                },
                "available_options": {"days_ahead": {"min": 1, "max": 30, "default": 7}},
            }
        )

    except Exception as e:
        logger.error(f"Error getting events fetch config: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/events/statistics", methods=["GET"])
@require_admin
def get_events_statistics():
    """
    Получить статистику событий.

    Returns:
        JSON: { total: int, by_category: [...], by_provider: [...], upcoming_7days: int, last_24hours: int }
    """
    try:
        from database.db_models import supabase

        if not supabase:
            return jsonify({"error": "Database not available"}), 500

        # Общее количество событий
        total_response = supabase.table("events_new").select("id", count="exact").execute()
        total = total_response.count or 0

        # Статистика по категориям
        by_category = []
        try:
            category_response = supabase.rpc("get_provider_stats", {"table_name": "events_new"}).execute()
            if category_response.data:
                # Группируем по категориям
                from collections import defaultdict

                category_stats = defaultdict(lambda: {"count": 0, "total_importance": 0.0})

                for row in category_response.data:
                    if row.get("category"):
                        category_stats[row["category"]]["count"] += row.get("count", 0)
                        category_stats[row["category"]]["total_importance"] += row.get("avg_importance", 0.0) * row.get(
                            "count", 0
                        )

                for category, stats in category_stats.items():
                    avg_importance = stats["total_importance"] / stats["count"] if stats["count"] > 0 else 0.0
                    by_category.append(
                        {"category": category, "count": stats["count"], "avg_importance": round(avg_importance, 2)}
                    )
        except Exception as e:
            logger.warning(f"Could not fetch category stats: {e}")

        # Статистика по провайдерам
        by_provider = []
        try:
            provider_response = supabase.rpc("get_provider_stats", {"table_name": "events_new"}).execute()
            if provider_response.data:
                from collections import defaultdict

                provider_stats = defaultdict(lambda: {"count": 0, "total_importance": 0.0})

                for row in provider_response.data:
                    if row.get("source"):
                        provider_stats[row["source"]]["count"] += row.get("count", 0)
                        provider_stats[row["source"]]["total_importance"] += row.get("avg_importance", 0.0) * row.get(
                            "count", 0
                        )

                for provider, stats in provider_stats.items():
                    avg_importance = stats["total_importance"] / stats["count"] if stats["count"] > 0 else 0.0
                    by_provider.append(
                        {"provider": provider, "count": stats["count"], "avg_importance": round(avg_importance, 2)}
                    )
        except Exception as e:
            logger.warning(f"Could not fetch provider stats: {e}")

        # События на следующие 7 дней
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        week_later = now + timedelta(days=7)
        upcoming_response = (
            supabase.table("events_new")
            .select("id", count="exact")
            .gte("starts_at", now.isoformat())
            .lte("starts_at", week_later.isoformat())
            .execute()
        )
        upcoming_7days = upcoming_response.count or 0

        # События за последние 24 часа
        day_ago = now - timedelta(days=1)
        last_24h_response = (
            supabase.table("events_new").select("id", count="exact").gte("created_at", day_ago.isoformat()).execute()
        )
        last_24hours = last_24h_response.count or 0

        return jsonify(
            {
                "total": total,
                "by_category": by_category,
                "by_provider": by_provider,
                "upcoming_7days": upcoming_7days,
                "last_24hours": last_24hours,
            }
        )

    except Exception as e:
        logger.error(f"Error getting events statistics: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/events/logs", methods=["GET"])
@require_admin
def get_events_fetch_logs():
    """
    Получить логи загрузки событий.

    Query params:
        lines: количество строк (по умолчанию 100)

    Returns:
        JSON: { logs: [str] }
    """
    try:
        from datetime import datetime

        lines = request.args.get("lines", 100, type=int)
        lines = min(max(lines, 1), 1000)  # Ограничиваем от 1 до 1000

        log_file = "logs/events_fetch.log"
        if not os.path.exists(log_file):
            return jsonify({"logs": []})

        # Читаем последние N строк
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]

        # Формируем logs в правильном формате
        logs = []
        for line in recent_lines:
            logs.append(
                {"text": line.strip(), "timestamp": datetime.now().isoformat()}  # TODO: парсить реальный timestamp
            )

        return jsonify({"logs": logs, "file": os.path.basename(log_file), "total_lines": len(all_lines)})

    except Exception as e:
        logger.error(f"Error reading events log file: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Health Check ====================


@admin_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint (без авторизации для мониторинга).

    Returns:
        JSON: { status: 'ok', timestamp: '...' }
    """
    return jsonify({"status": "ok", "service": "admin-api", "timestamp": datetime.now().isoformat()})


# ==================== Error Handlers ====================


@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@admin_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500
