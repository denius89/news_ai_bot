"""
Утилиты для распределения новостей по категориям.
Поддерживает различные стратегии распределения для обеспечения разнообразия контента.
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Веса категорий по умолчанию (в процентах)
DEFAULT_CATEGORY_WEIGHTS = {
    "crypto": 0.30,  # 30% - популярная категория
    "tech": 0.25,  # 25% - популярная категория
    "world": 0.20,  # 20% - важная категория
    "markets": 0.15,  # 15% - финансовая категория
    "sports": 0.10,  # 10% - развлекательная категория
}

# Минимальное количество новостей на категорию
MIN_NEWS_PER_CATEGORY = 1

# Максимальное количество новостей на категорию
MAX_NEWS_PER_CATEGORY = 10


def calculate_news_score(news_item: Dict) -> float:
    """
    Рассчитывает общий балл новости для ранжирования.

    Args:
        news_item: Словарь с данными новости

    Returns:
        float: Балл новости (0.0 - 1.0)
    """
    try:
        importance = float(news_item.get("importance", 0.5))
        credibility = float(news_item.get("credibility", 0.5))

        # Бонус за свежесть
        freshness_bonus = calculate_freshness_bonus(news_item.get("published_at"))

        # Бонус за качество источника
        source_bonus = calculate_source_quality_bonus(news_item.get("source"))

        # Общий балл
        score = importance * 0.4 + credibility * 0.3 + freshness_bonus * 0.2 + source_bonus * 0.1

        return min(max(score, 0.0), 1.0)  # Ограничиваем от 0 до 1

    except Exception as e:
        logger.warning(f"Ошибка расчета балла новости: {e}")
        return 0.5


def calculate_freshness_bonus(published_at: Optional[str]) -> float:
    """
    Рассчитывает бонус за свежесть новости.

    Args:
        published_at: Дата публикации в ISO формате

    Returns:
        float: Бонус за свежесть (0.0 - 0.3)
    """
    if not published_at:
        return 0.0

    try:
        now = datetime.now(timezone.utc)

        if isinstance(published_at, str):
            # Парсим ISO формат
            if published_at.endswith("Z"):
                published_at = published_at[:-1] + "+00:00"
            published_dt = datetime.fromisoformat(published_at)
        else:
            published_dt = published_at

        hours_ago = (now - published_dt).total_seconds() / 3600

        if hours_ago <= 1:
            return 0.3  # Очень свежие новости
        elif hours_ago <= 6:
            return 0.2  # Свежие новости
        elif hours_ago <= 24:
            return 0.1  # Недавние новости
        elif hours_ago <= 72:
            return 0.05  # Старые новости
        else:
            return 0.0  # Очень старые новости

    except Exception as e:
        logger.warning(f"Ошибка расчета свежести: {e}")
        return 0.0


def calculate_source_quality_bonus(source: Optional[str]) -> float:
    """
    Рассчитывает бонус за качество источника.

    Args:
        source: Название источника

    Returns:
        float: Бонус за источник (0.0 - 0.2)
    """
    if not source:
        return 0.05

    # Качественные источники получают бонус
    quality_sources = {
        "Reuters": 0.2,
        "BBC": 0.2,
        "CNN": 0.15,
        "Bloomberg": 0.15,
        "Associated Press": 0.15,
        "CoinDesk": 0.1,
        "TechCrunch": 0.1,
        "The Verge": 0.1,
        "Ars Technica": 0.1,
        "Wired": 0.1,
    }

    return quality_sources.get(source, 0.05)


def get_category_weights() -> Dict[str, float]:
    """
    Возвращает веса категорий для распределения.

    Returns:
        Dict[str, float]: Словарь с весами категорий
    """
    return DEFAULT_CATEGORY_WEIGHTS.copy()


def distribute_news_weighted(
    news_by_category: Dict[str, List[Dict]], total_limit: int = 20, weights: Optional[Dict[str, float]] = None
) -> List[Dict]:
    """
    Распределяет новости по категориям с учетом весов.

    Args:
        news_by_category: Словарь {category: [news_items]}
        total_limit: Общее количество новостей для распределения
        weights: Веса категорий (если None, используются по умолчанию)

    Returns:
        List[Dict]: Список распределенных новостей
    """
    if not news_by_category:
        return []

    if weights is None:
        weights = get_category_weights()

    # Сортируем новости в каждой категории по качеству
    for category in news_by_category:
        news_by_category[category].sort(key=calculate_news_score, reverse=True)

    # Рассчитываем количество новостей для каждой категории
    category_limits = {}
    available_categories = list(news_by_category.keys())

    # Нормализуем веса для доступных категорий
    total_weight = sum(weights.get(cat, 0.1) for cat in available_categories)
    normalized_weights = {cat: weights.get(cat, 0.1) / total_weight for cat in available_categories}

    # Распределяем новости
    distributed_news = []
    remaining_limit = total_limit

    for category in available_categories:
        weight = normalized_weights[category]
        category_limit = max(MIN_NEWS_PER_CATEGORY, min(MAX_NEWS_PER_CATEGORY, int(total_limit * weight)))

        # Берем лучшие новости из категории
        category_news = news_by_category[category][:category_limit]
        distributed_news.extend(category_news)

        logger.debug(f"Категория {category}: {len(category_news)} новостей (вес: {weight:.2f})")

    # Если не хватает новостей, добавляем из категорий с наибольшим количеством
    if len(distributed_news) < total_limit:
        for category in sorted(available_categories, key=lambda x: len(news_by_category[x]), reverse=True):
            if len(distributed_news) >= total_limit:
                break

            already_taken = len([n for n in distributed_news if n.get("category") == category])
            available_in_category = len(news_by_category[category])

            if already_taken < available_in_category:
                additional_news = news_by_category[category][already_taken : already_taken + 1]
                distributed_news.extend(additional_news)

    # Перемешиваем для разнообразия, но сохраняем качество
    distributed_news = shuffle_with_quality_preservation(distributed_news)

    # Ограничиваем общее количество
    return distributed_news[:total_limit]


def shuffle_with_quality_preservation(news_list: List[Dict]) -> List[Dict]:
    """
    Перемешивает новости с сохранением качества.
    Не ставит все новости одной категории подряд.

    Args:
        news_list: Список новостей для перемешивания

    Returns:
        List[Dict]: Перемешанный список новостей
    """
    if len(news_list) <= 1:
        return news_list

    # Группируем по категориям
    categories = {}
    for news in news_list:
        category = news.get("category", "unknown")
        if category not in categories:
            categories[category] = []
        categories[category].append(news)

    # Чередуем категории
    shuffled = []
    max_items = max(len(items) for items in categories.values())

    for i in range(max_items):
        for category, items in categories.items():
            if i < len(items):
                shuffled.append(items[i])

    return shuffled


def get_category_breakdown(news_list: List[Dict]) -> Dict[str, int]:
    """
    Возвращает разбивку новостей по категориям.

    Args:
        news_list: Список новостей

    Returns:
        Dict[str, int]: Словарь {category: count}
    """
    breakdown = {}
    for news in news_list:
        category = news.get("category", "unknown")
        breakdown[category] = breakdown.get(category, 0) + 1

    return breakdown


def calculate_distribution_score(news_list: List[Dict]) -> float:
    """
    Рассчитывает оценку равномерности распределения.

    Args:
        news_list: Список новостей

    Returns:
        float: Оценка распределения (0.0 - 1.0)
    """
    if not news_list:
        return 0.0

    breakdown = get_category_breakdown(news_list)
    if not breakdown:
        return 0.0

    # Чем меньше разброс, тем лучше баланс
    counts = list(breakdown.values())
    max_count = max(counts)
    min_count = min(counts)

    if max_count == 0:
        return 0.0

    balance_score = 1 - (max_count - min_count) / max_count
    return round(balance_score, 2)


def get_distribution_statistics(news_list: List[Dict]) -> Dict:
    """
    Возвращает статистику распределения новостей.

    Args:
        news_list: Список новостей

    Returns:
        Dict: Статистика распределения
    """
    breakdown = get_category_breakdown(news_list)
    distribution_score = calculate_distribution_score(news_list)

    return {
        "total_news": len(news_list),
        "categories_count": len(breakdown),
        "category_breakdown": breakdown,
        "distribution_score": distribution_score,
        "is_balanced": distribution_score >= 0.7,
        "avg_per_category": round(len(news_list) / len(breakdown), 1) if breakdown else 0,
    }
