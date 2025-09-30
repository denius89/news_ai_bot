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
    for item in news_items:
        item["source"] = item.get("source") or "—"
        item["credibility"] = float(item.get("credibility") or 0.0)
        item["importance"] = float(item.get("importance") or 0.0)
        item["published_at_fmt"] = item.get("published_at_fmt") or "—"

    return render_template(
        "digest.html",
        news=news_items,
        all_categories=["crypto", "economy", "world", "technology", "politics"],
        active_categories=categories,
        digest_text=digest_text,
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
    )


__all__ = ["news_bp"]
