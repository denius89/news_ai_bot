"""
Flask-маршруты для отображения новостей и событий.
"""

import logging
from flask import Blueprint, render_template, request

from services.digest_service import build_daily_digest
from database.db_models import (
    get_latest_events,
)  # пока оставим здесь (можно позже вынести в EventsService)

logger = logging.getLogger(__name__)

news_bp = Blueprint("news", __name__)


# --- Дайджест новостей ---
@news_bp.route("/digest")
def digest():
    categories = request.args.getlist("category")

    digest_text, news_items = build_daily_digest(limit=10, categories=categories)

    # Обогащаем данными для шаблона
    enriched_items = []
    for item in news_items:
        # Преобразуем Pydantic модель в словарь для шаблона
        if hasattr(item, 'model_dump'):
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
        all_categories=["crypto", "economy", "world", "technology", "politics"],
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
        "events.html",
        events=events_list,
        active_category=category,
        active_page="events",
    )


# --- WebApp Dashboard ---
@news_bp.route("/webapp")
def webapp():
    """WebApp Dashboard with tabs for subscriptions, notifications, and calendar."""
    logger.info("📱 WebApp dashboard accessed")
    return render_template("webapp.html")


__all__ = ["news_bp"]
