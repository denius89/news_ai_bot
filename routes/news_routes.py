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
@news_bp.route("/api/latest")  # Добавляем альтернативный маршрут для совместимости
def api_latest_news():
    """API endpoint для получения последних новостей."""
    try:
        from database.db_models import get_latest_news
        
        # Получаем параметры пагинации
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Получаем новости из базы данных
        all_news = get_latest_news(limit=1000)  # Получаем больше для пагинации
        
        # Применяем пагинацию
        total = len(all_news)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        news = all_news[start_idx:end_idx]
        
        # Сортируем по важности, достоверности и свежести
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        
        def calculate_score(item):
            importance = float(item.get('importance', 0.5))
            credibility = float(item.get('credibility', 0.5))
            
            # Бонус за свежесть
            published_at = item.get('published_at')
            if published_at:
                if isinstance(published_at, str):
                    try:
                        published_at = datetime.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    except:
                        published_at = now
                hours_ago = (now - published_at).total_seconds() / 3600
                freshness_bonus = 0.1 if hours_ago <= 6 else 0.05 if hours_ago <= 24 else 0
            else:
                freshness_bonus = 0
            
            return importance * 0.6 + credibility * 0.4 + freshness_bonus
        
        news.sort(key=calculate_score, reverse=True)
        
        # Применяем пагинацию после сортировки
        paginated_news = news[start_idx:end_idx]
        
        return jsonify({
            "status": "success",
            "data": [
                {
                    "id": n.get("id"),
                    "title": n.get("title"),
                    "content": n.get("content"),
                    "source": n.get("source"),
                    "url": n.get("link"),  # Добавляем ссылку на новость
                    "published_at": n.get("published_at").isoformat() if n.get("published_at") else None,
                    "category": n.get("category"),
                    "credibility": n.get("credibility"),
                    "importance": n.get("importance")
                }
                for n in paginated_news
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
                "has_next": end_idx < total,
                "has_prev": page > 1
            }
        })
    except Exception as e:
        logger.error(f"Ошибка получения новостей: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- WebApp Dashboard ---
# Moved to webapp_routes.py to avoid conflicts


__all__ = ["news_bp"]
