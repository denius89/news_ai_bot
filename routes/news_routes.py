from flask import Blueprint, render_template
from database.db_models import supabase
from datetime import datetime

news_bp = Blueprint("news", __name__)

@news_bp.route("/digest")
def digest():
    # Загружаем последние 10 новостей, сортировка: важность → дата
    response = (
        supabase.table("news")
        .select("title, content, link, published_at, importance")
        .order("importance", desc=True)
        .order("published_at", desc=True)
        .limit(10)
        .execute()
    )

    news_items = response.data if response.data else []

    # Форматируем дату для отображения
    for item in news_items:
        if item.get("published_at"):
            try:
                dt = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                item["published_at_fmt"] = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                item["published_at_fmt"] = item["published_at"]
        else:
            item["published_at_fmt"] = "—"

    return render_template("digest.html", news=news_items)