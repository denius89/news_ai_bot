from flask import Blueprint, render_template, request
from database.db_models import supabase
from datetime import datetime

news_bp = Blueprint("news", __name__)

@news_bp.route("/digest")
def digest():
    # Получаем список активных категорий из query params
    categories = request.args.getlist("category")

    # Базовый запрос
    query = supabase.table("news").select(
        "title, content, link, published_at, importance, source, category"
    )

    # Фильтрация по категориям (если выбраны)
    if categories:
        query = query.in_("category", categories)

    response = (
        query.order("importance", desc=True)
             .order("published_at", desc=True)
             .limit(10)
             .execute()
    )

    news_items = response.data if response.data else []

    for item in news_items:
        # Форматируем дату
        if item.get("published_at"):
            try:
                dt = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                item["published_at_fmt"] = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                item["published_at_fmt"] = item["published_at"]
        else:
            item["published_at_fmt"] = "—"

        # importance → float
        try:
            item["importance"] = float(item.get("importance") or 0.0)
        except Exception:
            item["importance"] = 0.0

        item["source"] = item.get("source") or "—"

    return render_template(
        "digest.html",
        news=news_items,
        all_categories=["crypto", "economy", "world", "technology", "politics"],
        active_categories=categories
    )