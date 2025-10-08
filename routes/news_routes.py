"""
Flask-маршруты для отображения новостей и событий.
"""

import logging
from typing import Dict, List
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
        
        # Сортируем ВСЕ новости перед пагинацией
        all_news.sort(key=calculate_score, reverse=True)
        
        # Применяем пагинацию ПОСЛЕ сортировки
        total = len(all_news)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_news = all_news[start_idx:end_idx]
        
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


@news_bp.route("/api/latest-weighted")
def api_latest_news_weighted():
    """API endpoint для получения новостей с взвешенным распределением по категориям."""
    try:
        from database.db_models import get_latest_news
        from services.categories import get_categories
        from utils.news_distribution import (
            distribute_news_weighted, 
            get_distribution_statistics,
            get_category_weights
        )
        
        # Получаем параметры
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        distribution_mode = request.args.get('mode', 'weighted')  # weighted, balanced, round_robin
        
        logger.info(f"📊 Запрос взвешенного распределения: page={page}, limit={limit}, mode={distribution_mode}")
        
        # Получаем новости по категориям
        news_by_category = {}
        all_categories = get_categories()
        
        for category in all_categories:
            try:
                category_news = get_latest_news(categories=[category], limit=100)  # ИСПРАВЛЕНО: передаем список
                news_by_category[category] = category_news
                logger.debug(f"Категория {category}: {len(category_news)} новостей")
            except Exception as e:
                logger.warning(f"Ошибка получения новостей для категории {category}: {e}")
                news_by_category[category] = []
        
        # Применяем взвешенное распределение
        if distribution_mode == 'weighted':
            distributed_news = distribute_news_weighted(news_by_category, limit)
        elif distribution_mode == 'balanced':
            # Равномерное распределение
            distributed_news = distribute_news_balanced(news_by_category, limit)
        else:
            # По умолчанию взвешенное
            distributed_news = distribute_news_weighted(news_by_category, limit)
        
        # Получаем статистику распределения
        distribution_stats = get_distribution_statistics(distributed_news)
        
        # Применяем пагинацию к распределенным новостям
        total_distributed = len(distributed_news)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_news = distributed_news[start_idx:end_idx]
        
        logger.info(f"✅ Распределено {len(distributed_news)} новостей, возвращаем {len(paginated_news)} для страницы {page}")
        
        return jsonify({
            "status": "success",
            "data": [
                {
                    "id": n.get("id"),
                    "title": n.get("title"),
                    "content": n.get("content"),
                    "source": n.get("source"),
                    "url": n.get("link"),
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
                "total": total_distributed,
                "total_pages": (total_distributed + limit - 1) // limit,
                "has_next": end_idx < total_distributed,
                "has_prev": page > 1
            },
            "distribution": {
                "mode": distribution_mode,
                "statistics": distribution_stats,
                "category_weights": get_category_weights()
            }
        })
        
    except Exception as e:
        logger.error(f"Ошибка взвешенного распределения новостей: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def distribute_news_balanced(news_by_category: Dict[str, List[Dict]], total_limit: int = 20) -> List[Dict]:
    """
    Равномерное распределение новостей по категориям (Round Robin).
    
    Args:
        news_by_category: Словарь {category: [news_items]}
        total_limit: Общее количество новостей
        
    Returns:
        List[Dict]: Список распределенных новостей
    """
    if not news_by_category:
        return []
    
    from utils.news_distribution import calculate_news_score
    
    # Сортируем новости в каждой категории по качеству
    for category in news_by_category:
        news_by_category[category].sort(key=calculate_news_score, reverse=True)
    
    # Равномерное распределение
    categories = list(news_by_category.keys())
    per_category = total_limit // len(categories)
    remainder = total_limit % len(categories)
    
    distributed_news = []
    for i, category in enumerate(categories):
        limit = per_category + (1 if i < remainder else 0)
        category_news = news_by_category[category][:limit]
        distributed_news.extend(category_news)
    
    return distributed_news


@news_bp.route("/api/distribution-stats")
def api_distribution_stats():
    """API endpoint для получения статистики распределения новостей."""
    try:
        from services.categories import get_categories
        from utils.news_distribution import get_category_weights, get_distribution_statistics
        from database.db_models import get_latest_news
        
        # Получаем статистику по категориям
        categories = get_categories()
        category_stats = {}
        total_news = 0
        
        for category in categories:
            try:
                category_news = get_latest_news(categories=[category], limit=1000)
                category_stats[category] = {
                    'count': len(category_news),
                    'avg_importance': sum(float(n.get('importance', 0.5)) for n in category_news) / len(category_news) if category_news else 0,
                    'avg_credibility': sum(float(n.get('credibility', 0.5)) for n in category_news) / len(category_news) if category_news else 0,
                }
                total_news += len(category_news)
            except Exception as e:
                logger.warning(f"Ошибка получения статистики для категории {category}: {e}")
                category_stats[category] = {'count': 0, 'avg_importance': 0, 'avg_credibility': 0}
        
        # Получаем веса категорий
        weights = get_category_weights()
        
        # Рассчитываем рекомендуемые веса на основе количества новостей
        recommended_weights = {}
        if total_news > 0:
            for category in categories:
                recommended_weights[category] = category_stats[category]['count'] / total_news
        
        return jsonify({
            "status": "success",
            "statistics": {
                "total_news": total_news,
                "categories_count": len(categories),
                "category_stats": category_stats,
                "current_weights": weights,
                "recommended_weights": recommended_weights,
                "distribution_efficiency": {
                    "crypto_ratio": category_stats.get('crypto', {}).get('count', 0) / total_news if total_news > 0 else 0,
                    "tech_ratio": category_stats.get('tech', {}).get('count', 0) / total_news if total_news > 0 else 0,
                    "world_ratio": category_stats.get('world', {}).get('count', 0) / total_news if total_news > 0 else 0,
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики распределения: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


__all__ = ["news_bp"]
