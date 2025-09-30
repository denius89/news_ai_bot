"""
Маршруты для веб-приложения:
 - /digest  → последние новости
 - /events  → список событий
"""

import logging
from flask import Blueprint, render_template, request

from database.db_models import supabase
from utils.dates import format_datetime

logger = logging.getLogger(__name__)

# Blueprint для всех новостных маршрутов
news_bp = Blueprint("news", __name__)


@news_bp.route("/digest")
def digest():
    categories = request.args.getlist("category")

    query = supabase.table("news").select(
        "title, content, link, published_at, credibility, importance, source, category"
    )
    if categories:
        query = query.in_("category", categories)

    response = (
        query.order("importance", desc=True).order("published_at", desc=True).limit(10).execute()
    )
    news_items = response.data or []

    # форматируем поля
    for item in news_items:
        item["published_at_fmt"] = format_datetime(item.get("published_at"))
        try:
            item["credibility"] = float(item.get("credibility") or 0.0)
        except Exception:
            item["credibility"] = 0.0
        try:
            item["importance"] = float(item.get("importance") or 0.0)
        except Exception:
            item["importance"] = 0.0
        item["source"] = item.get("source") or "—"

    return render_template(
        "digest.html",
        news=news_items,
        all_categories=["crypto", "economy", "world", "technology", "politics"],
        active_categories=categories,
    )


@news_bp.route("/events")
def events():
    category = request.args.get("category")

    query = supabase.table("events").select(
        "event_time, country, country_code, currency, title, importance, fact, forecast, previous, source"
    )
    if category:
        query = query.eq("category", category)

    response = query.order("event_time", desc=False).limit(50).execute()
    events_list = response.data or []

    for ev in events_list:
        ev["event_time_fmt"] = format_datetime(ev.get("event_time"))
        try:
            ev["importance"] = int(ev.get("importance") or 0)
        except Exception:
            ev["importance"] = 0

    return render_template("events.html", events=events_list, active_category=category)


# Экспортируем news_bp, чтобы тесты и webapp могли его импортировать
__all__ = ["news_bp"]
