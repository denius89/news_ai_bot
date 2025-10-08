"""
API endpoints для статистики дашборда PulseAI.

Предоставляет реальные данные из базы данных для отображения
в дашборде администратора.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request

# Добавляем корень проекта в путь
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_models import supabase, safe_execute

logger = logging.getLogger(__name__)

# Создаем Blueprint для API статистики
dashboard_api = Blueprint("dashboard_api", __name__)


def get_news_stats_today() -> Dict:
    """Получает статистику новостей за сегодня."""
    if not supabase:
        return {"count": 0, "change": 0}

    try:
        # Сегодняшняя дата
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Новости за сегодня
        today_query = (
            supabase.table("news")
            .select("id", count="exact")
            .gte("published_at", today.isoformat())
            .lt("published_at", (today + timedelta(days=1)).isoformat())
        )

        # Новости за вчера
        yesterday_query = (
            supabase.table("news")
            .select("id", count="exact")
            .gte("published_at", yesterday.isoformat())
            .lt("published_at", today.isoformat())
        )

        today_result = safe_execute(today_query)
        yesterday_result = safe_execute(yesterday_query)

        today_count = today_result.count if today_result.count else 0
        yesterday_count = yesterday_result.count if yesterday_result.count else 0

        # Если сегодня нет новостей, показываем последние доступные данные
        if today_count == 0:
            # Берем новости за последние 7 дней
            week_ago = datetime.now() - timedelta(days=7)
            recent_query = supabase.table("news").select("id", count="exact").gte("published_at", week_ago.isoformat())
            recent_result = safe_execute(recent_query)
            today_count = recent_result.count if recent_result.count else 0

            # Для изменения берем предыдущую неделю
            two_weeks_ago = datetime.now() - timedelta(days=14)
            prev_week_query = (
                supabase.table("news")
                .select("id", count="exact")
                .gte("published_at", two_weeks_ago.isoformat())
                .lt("published_at", week_ago.isoformat())
            )
            prev_week_result = safe_execute(prev_week_query)
            prev_week_count = prev_week_result.count if prev_week_result.count else 0

            if prev_week_count > 0:
                change_percent = round(((today_count - prev_week_count) / prev_week_count) * 100)
            else:
                change_percent = 100 if today_count > 0 else 0
        else:
            # Вычисляем процент изменения для сегодняшних новостей
            if yesterday_count > 0:
                change_percent = round(((today_count - yesterday_count) / yesterday_count) * 100)
            else:
                change_percent = 100 if today_count > 0 else 0

        return {"count": today_count, "change": change_percent}

    except Exception as e:
        logger.error(f"Ошибка получения статистики новостей: {e}")
        return {"count": 0, "change": 0}


def get_active_sources_stats() -> Dict:
    """Получает статистику активных источников."""
    if not supabase:
        return {"count": 0, "change": 0}

    try:
        # Активные источники - получаем все источники и считаем уникальные
        sources_query = supabase.table("news").select("source").limit(1000)  # Ограничиваем для производительности

        result = safe_execute(sources_query)
        if result.data:
            unique_sources = set(item["source"] for item in result.data if item.get("source"))
            active_sources = len(unique_sources)
        else:
            active_sources = 0

        # Источники за предыдущую неделю
        week_ago = datetime.now() - timedelta(days=7)
        two_weeks_ago = datetime.now() - timedelta(days=14)

        prev_sources_query = (
            supabase.table("news")
            .select("source")
            .gte("published_at", two_weeks_ago.isoformat())
            .lt("published_at", week_ago.isoformat())
            .limit(1000)
        )

        prev_result = safe_execute(prev_sources_query)
        if prev_result.data:
            prev_unique_sources = set(item["source"] for item in prev_result.data if item.get("source"))
            prev_sources = len(prev_unique_sources)
        else:
            prev_sources = 0

        change = active_sources - prev_sources

        return {"count": active_sources, "change": change}

    except Exception as e:
        logger.error(f"Ошибка получения статистики источников: {e}")
        return {"count": 0, "change": 0}


def get_categories_stats() -> Dict:
    """Получает статистику категорий."""
    if not supabase:
        return {"count": 0, "change": 0}

    try:
        # Активные категории - получаем все категории и считаем уникальные
        categories_query = supabase.table("news").select("category")

        result = safe_execute(categories_query)
        if result.data:
            unique_categories = set(item["category"] for item in result.data if item.get("category"))
            active_categories = len(unique_categories)
        else:
            active_categories = 0

        return {"count": active_categories, "change": 0}  # Стабильно

    except Exception as e:
        logger.error(f"Ошибка получения статистики категорий: {e}")
        return {"count": 0, "change": 0}


def get_ai_digests_stats() -> Dict:
    """Получает статистику AI дайджестов."""
    if not supabase:
        return {"count": 0, "change": 0}

    try:
        # Дайджесты за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)

        digests_query = supabase.table("digests").select("id", count="exact").gte("created_at", week_ago.isoformat())

        result = safe_execute(digests_query)
        digests_count = result.count if result.count else 0

        # Дайджесты за предыдущую неделю
        two_weeks_ago = datetime.now() - timedelta(days=14)

        prev_digests_query = (
            supabase.table("digests")
            .select("id", count="exact")
            .gte("created_at", two_weeks_ago.isoformat())
            .lt("created_at", week_ago.isoformat())
        )

        prev_result = safe_execute(prev_digests_query)
        prev_digests_count = prev_result.count if prev_result.count else 0

        change = digests_count - prev_digests_count

        return {"count": digests_count, "change": change}

    except Exception as e:
        logger.error(f"Ошибка получения статистики дайджестов: {e}")
        return {"count": 0, "change": 0}


@dashboard_api.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Получает общую статистику для дашборда."""
    try:
        stats = {
            "news_today": get_news_stats_today(),
            "active_sources": get_active_sources_stats(),
            "categories": get_categories_stats(),
            "ai_digests": get_ai_digests_stats(),
        }

        logger.info(f"Получена статистика дашборда: {stats}")
        return jsonify({"success": True, "data": stats, "timestamp": datetime.now().isoformat()})

    except Exception as e:
        logger.error(f"Ошибка получения статистики дашборда: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "data": {
                        "news_today": {"count": 0, "change": 0},
                        "active_sources": {"count": 0, "change": 0},
                        "categories": {"count": 0, "change": 0},
                        "ai_digests": {"count": 0, "change": 0},
                    },
                }
            ),
            500,
        )


@dashboard_api.route("/api/dashboard/news_trend", methods=["GET"])
def get_news_trend():
    """Получает тренд новостей за последние 7 дней."""
    if not supabase:
        return jsonify({"success": False, "error": "Database not available"}), 500

    try:
        # Данные за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)

        # Группируем по дням
        trend_query = (
            supabase.table("news")
            .select("published_at")
            .gte("published_at", week_ago.isoformat())
            .order("published_at", desc=False)
        )

        result = safe_execute(trend_query)

        # Группируем по дням
        daily_counts = {}
        for news_item in result.data or []:
            published_at = news_item.get("published_at")
            if published_at:
                try:
                    # Парсим дату и берем только дату (без времени)
                    date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    date_str = date_obj.date().isoformat()
                    daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                except Exception as e:
                    logger.warning(f"Ошибка парсинга даты {published_at}: {e}")
                    continue

        # Формируем массив для последних 7 дней
        trend_data = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date()
            date_str = date.isoformat()
            count = daily_counts.get(date_str, 0)
            trend_data.append({"date": date_str, "count": count})

        # Сортируем по дате (от старых к новым)
        trend_data.sort(key=lambda x: x["date"])

        return jsonify({"success": True, "data": trend_data})

    except Exception as e:
        logger.error(f"Ошибка получения тренда новостей: {e}")
        return jsonify({"success": False, "error": str(e), "data": []}), 500


@dashboard_api.route("/api/dashboard/latest_news", methods=["GET"])
def get_recent_news():
    """Получает последние новости для дашборда."""
    if not supabase:
        return jsonify({"success": False, "error": "Database not available"}), 500

    try:
        limit = request.args.get("limit", 10, type=int)

        recent_query = (
            supabase.table("news")
            .select("id, title, source, category, published_at, credibility, importance")
            .order("published_at", desc=True)
            .limit(limit)
        )

        result = safe_execute(recent_query)

        # Форматируем данные
        news_data = []
        for news_item in result.data or []:
            news_data.append(
                {
                    "id": news_item.get("id"),
                    "title": (
                        news_item.get("title", "")[:100] + "..."
                        if len(news_item.get("title", "")) > 100
                        else news_item.get("title", "")
                    ),
                    "source": news_item.get("source", ""),
                    "category": news_item.get("category", ""),
                    "published_at": news_item.get("published_at"),
                    "credibility": round(float(news_item.get("credibility", 0.5)), 2),
                    "importance": round(float(news_item.get("importance", 0.5)), 2),
                }
            )

        return jsonify({"success": True, "data": news_data})

    except Exception as e:
        logger.error(f"Ошибка получения последних новостей: {e}")
        return jsonify({"success": False, "error": str(e), "data": []}), 500


@dashboard_api.route("/api/dashboard/sources_breakdown", methods=["GET"])
def get_sources_breakdown():
    """Получает разбивку по источникам."""
    if not supabase:
        return jsonify({"success": False, "error": "Database not available"}), 500

    try:
        # Данные за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)

        sources_query = supabase.table("news").select("source").gte("published_at", week_ago.isoformat())

        result = safe_execute(sources_query)

        # Подсчитываем количество по источникам
        source_counts = {}
        for news_item in result.data or []:
            source = news_item.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        # Сортируем по количеству
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)

        # Формируем данные для графика
        breakdown_data = []
        for source, count in sorted_sources[:10]:  # Топ-10 источников
            breakdown_data.append({"source": source, "count": count})

        return jsonify({"success": True, "data": breakdown_data})

    except Exception as e:
        logger.error(f"Ошибка получения разбивки по источникам: {e}")
        return jsonify({"success": False, "error": str(e), "data": []}), 500
