from datetime import datetime

from flask import Blueprint, render_template, request

from database.db_models import supabase

news_bp = Blueprint("news", __name__)


# --- Дайджест новостей ---
@news_bp.route("/digest")
def digest():
    categories = request.args.getlist("category")

    # Базовый запрос с AI-полями
    query = supabase.table("news").select(
        "title, content, link, published_at, credibility, importance, source, category"
    )

    if categories:
        query = query.in_("category", categories)

    response = (
        query.order("importance", desc=True).order("published_at", desc=True).limit(10).execute()
    )

    news_items = response.data or []

    for item in news_items:
        # форматируем дату
        if item.get("published_at"):
            try:
                dt = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                item["published_at_fmt"] = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                item["published_at_fmt"] = item["published_at"]
        else:
            item["published_at_fmt"] = "—"

        # credibility → float
        try:
            item["credibility"] = float(item.get("credibility") or 0.0)
        except Exception:
            item["credibility"] = 0.0

        # importance → float
        try:
            item["importance"] = float(item.get("importance") or 0.0)
        except Exception:
            item["importance"] = 0.0

        # источник
        item["source"] = item.get("source") or "—"

    return render_template(
        "digest.html",
        news=news_items,
        all_categories=["crypto", "economy", "world", "technology", "politics"],
        active_categories=categories,
    )


# --- Календарь событий ---
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
        # форматируем время
        if ev.get("event_time"):
            try:
                dt = datetime.fromisoformat(ev["event_time"].replace("Z", "+00:00"))
                ev["event_time_fmt"] = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                ev["event_time_fmt"] = ev["event_time"]
        else:
            ev["event_time_fmt"] = "—"

        # importance → int
        try:
            ev["importance"] = int(ev.get("importance") or 0)
        except Exception:
            ev["importance"] = 0

    return render_template("events.html", events=events_list, active_category=category)
