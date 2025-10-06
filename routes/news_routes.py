"""
Flask-маршруты для отображения новостей и событий.
"""

import logging
from flask import Blueprint, render_template, request, jsonify

from services.unified_digest_service import get_sync_digest_service
from services.categories import get_categories
from database.db_models import (
    get_latest_events,
)  # пока оставим здесь (можно позже вынести в EventsService)

logger = logging.getLogger(__name__)

news_bp = Blueprint("news", __name__)


# --- Дайджест новостей ---
@news_bp.route("/digest")
def digest():
    categories = request.args.getlist("category")

    digest_service = get_sync_digest_service()
    digest_text = digest_service.build_daily_digest(limit=10, categories=categories)

    # Получаем новости отдельно для шаблона
    news_items = digest_service.db_service.get_latest_news(categories=categories, limit=10)

    # Обогащаем данными для шаблона
    enriched_items = []
    for item in news_items:
        # Преобразуем Pydantic модель в словарь для шаблона
        if hasattr(item, "model_dump"):
            item_dict = item.model_dump()
        else:
            item_dict = dict(item)

        item_dict["source"] = item_dict.get("source") or "—"
        item_dict["credibility"] = float(item_dict.get("credibility") or 0.0)
        item_dict["importance"] = float(item_dict.get("importance") or 0.0)
        item_dict["published_at_fmt"] = item_dict.get("published_at_fmt") or "—"
        enriched_items.append(item_dict)

    news_items = enriched_items

    return render_template(
        "digest.html",
        news=news_items,
        all_categories=get_categories(),  # Используем новую систему категорий
        active_categories=categories,
        digest_text=digest_text,
        active_page="digest",
    )


# --- Календарь событий ---
@news_bp.route("/events")
def events():
    category = request.args.get("category")

    events_list = get_latest_events(limit=50)

    # фильтрация по категории (если у события есть category)
    if category:
        events_list = [ev for ev in events_list if ev.get("category") == category]

    for ev in events_list:
        ev["event_time_fmt"] = ev.get("event_time_fmt") or "—"
        try:
            ev["importance"] = int(ev.get("importance") or 0)
        except Exception:
            ev["importance"] = 0

    return render_template(
        "calendar.html",
        events=events_list,
        active_category=category,
        active_page="events",
    )


# --- API Endpoints ---
@news_bp.route("/latest")
def api_latest_news():
    """API endpoint для получения последних новостей."""
    try:
        from database.db_models import get_latest_news
        news = get_latest_news(limit=10)
        
        return jsonify({
            "status": "success",
            "count": len(news),
            "data": [
                {
                    "id": n.get("id"),
                    "title": n.get("title"),
                    "source": n.get("source"),
                    "published_at": n.get("published_at").isoformat() if n.get("published_at") else None,
                    "category": n.get("category"),
                    "credibility": n.get("credibility"),
                    "importance": n.get("importance")
                }
                for n in news
            ]
        })
    except Exception as e:
        logger.error(f"Ошибка получения новостей: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- WebApp Dashboard ---
# Moved to webapp_routes.py to avoid conflicts


__all__ = ["news_bp"]
