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

        logger.info(f"Getting events metrics...")
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
        logger.info("Getting events providers...")
        db = get_sync_service()

        # Получаем статистику по источникам событий
        result = db.safe_execute(db.sync_client.table("events").select("source, category").limit(10000))

        events_data = result.data or []

        # Группируем по source
        from collections import defaultdict

        providers_map = defaultdict(lambda: {"count": 0, "categories": set()})
        category_counts = defaultdict(int)

        for event in events_data:
            source = event.get("source", "Unknown")
            category = event.get("category", "other")
            providers_map[source]["count"] += 1
            providers_map[source]["categories"].add(category)
            category_counts[category] += 1

        # Формируем список провайдеров
        providers = []
        for source, data in providers_map.items():
            providers.append(
                {
                    "name": source,
                    "category": list(data["categories"])[0] if data["categories"] else "other",
                    "status": "active",
                    "events_count": data["count"],
                    "last_updated": None,  # TODO: добавить timestamp из таблицы
                }
            )

        return jsonify(
            {
                "providers": sorted(providers, key=lambda x: x["events_count"], reverse=True),
                "total_events": len(events_data),
                "categories": {
                    "sports": category_counts.get("sports", 0),
                    "crypto": category_counts.get("crypto", 0),
                    "tech": category_counts.get("tech", 0),
                    "other": sum(v for k, v in category_counts.items() if k not in ["sports", "crypto", "tech"]),
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get events providers: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/events/test", methods=["POST"])
@require_admin
def test_events_provider():
    """
    Протестировать провайдер событий.

    Body: { provider: str }

    Returns:
        JSON: {success: bool, events_found: int, sample_events: [...], error: str}
    """
    try:
        data = request.get_json()
        provider = data.get("provider")

        if not provider:
            return jsonify({"error": "Provider name is required"}), 400

        logger.info(f"Testing events provider: {provider}")
        db = get_sync_service()

        # Получаем события от этого провайдера
        result = db.safe_execute(db.sync_client.table("events").select("*").eq("source", provider).limit(5))

        events = result.data or []

        return jsonify(
            {
                "success": True,
                "events_found": len(events),
                "sample_events": events,
                "message": f"Found {len(events)} events from {provider}",
            }
        )

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
            except:
                pass
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
        except:
            pass

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
