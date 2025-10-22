"""
Сервис для работы с категориями и источниками новостей.
Единый источник истины для всех категорий, подкатегорий и источников RSS.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Путь к файлу источников
SOURCES_FILE = Path(__file__).parent.parent / "config" / "data" / "sources.yaml"

# Настоящие категории новостей (исключаем технические настройки из sources.yaml)
NEWS_CATEGORIES = {"crypto", "sports", "markets", "tech", "world"}

# Кэш для загруженных данных
_sources_cache: Optional[Dict] = None
_cache_timestamp: Optional[float] = None


def _load_sources() -> Dict:
    """Загружает источники из YAML файла с кэшированием."""
    global _sources_cache, _cache_timestamp

    try:
        file_mtime = SOURCES_FILE.stat().st_mtime
        if _sources_cache is None or _cache_timestamp != file_mtime:
            with open(SOURCES_FILE, "r", encoding="utf-8") as f:
                _sources_cache = yaml.safe_load(f)
            _cache_timestamp = file_mtime
            logger.info("✅ Источники загружены из %s", SOURCES_FILE)

        return _sources_cache or {}
    except Exception as e:
        logger.error("❌ Ошибка загрузки источников: %s", e)
        return {}


def get_categories() -> List[str]:
    """
    Возвращает список всех категорий.

    Returns:
        List[str]: Список названий категорий
    """
    sources = _load_sources()
    # Фильтруем только настоящие категории новостей, исключаем технические настройки
    return [cat for cat in sources.keys() if cat in NEWS_CATEGORIES]


def get_subcategories(category: str) -> List[str]:
    """
    Возвращает список подкатегорий для указанной категории.

    Args:
        category: Название категории

    Returns:
        List[str]: Список названий подкатегорий
    """
    sources = _load_sources()
    if category not in sources:
        return []

    return list(sources[category].keys())


def get_icon(category: str, subcategory: str) -> Optional[str]:
    """
    Возвращает иконку для указанной подкатегории.

    Args:
        category: Название категории
        subcategory: Название подкатегории

    Returns:
        Optional[str]: Ключ иконки или None
    """
    sources = _load_sources()
    if category not in sources or subcategory not in sources[category]:
        return None

    return sources[category][subcategory].get("icon")


def get_sources(category: str, subcategory: str) -> List[Dict[str, str]]:
    """
    Возвращает список источников для указанной подкатегории.

    Args:
        category: Название категории
        subcategory: Название подкатегории

    Returns:
        List[Dict[str, str]]: Список источников с полями name и url
    """
    sources = _load_sources()
    if category not in sources or subcategory not in sources[category]:
        return []

    return sources[category][subcategory].get("sources", [])


def get_all_sources() -> List[Tuple[str, str, str, str]]:
    """
    Возвращает все источники в виде списка кортежей.

    Returns:
        List[Tuple[str, str, str, str]]: Список (category, subcategory, name, url)
    """
    all_sources = []
    sources = _load_sources()

    # Фильтруем только настоящие категории новостей
    for category, subcategories in sources.items():
        if category not in NEWS_CATEGORIES:
            continue

        for subcategory, data in subcategories.items():
            sources_list = data.get("sources", [])
            for source in sources_list:
                all_sources.append((category, subcategory, source.get("name", ""), source.get("url", "")))

    return all_sources


def get_category_structure() -> Dict[str, Dict[str, Dict]]:
    """
    Возвращает полную структуру категорий с иконками.

    Returns:
        Dict: Структура {category: {subcategory: {icon: str, sources: [...]}}}
    """
    sources = _load_sources()
    # Фильтруем только настоящие категории новостей, исключаем технические настройки
    return {cat: data for cat, data in sources.items() if cat in NEWS_CATEGORIES}


def get_emoji_icon(category: str, subcategory: str) -> str:
    """
    Возвращает emoji иконку для Telegram бота.

    Args:
        category: Название категории
        subcategory: Название подкатегории

    Returns:
        str: Emoji иконка
    """
    # Маппинг для основных категорий
    category_icons = {
        "crypto": "₿",
        "sports": "⚽",
        "markets": "📈",
        "tech": "🤖",
        "world": "🌍",
    }

    # Если запрашивается только категория (подкатегория пустая)
    if not subcategory:
        return category_icons.get(category, "📰")

    # Маппинг для подкатегорий
    icon_map = {
        # Crypto
        "btc": "₿",
        "bitcoin": "₿",
        "eth": "Ξ",
        "ethereum": "Ξ",
        "altcoin": "🪙",
        "altcoins": "🪙",
        "defi": "🏦",
        "nft": "🖼️",
        "gamefi": "🎮",
        "exchange": "🏢",
        "exchanges": "🏢",
        "regulation": "⚖️",
        "security": "🔒",
        "market_trends": "📊",
        # Sports - Football leagues
        "football": "⚽",
        "champions_league": "⚽",
        "europa_league": "⚽",
        "conference_league": "⚽",
        "premier_league": "⚽",
        "bundesliga": "⚽",
        "la_liga": "⚽",
        "serie_a": "⚽",
        "ligue_1": "⚽",
        "world_cup": "⚽",
        # Sports - Other sports
        "basketball": "🏀",
        "tennis": "🎾",
        "hockey": "🏒",
        "ufc": "🥊",
        "ufc_mma": "🥊",
        "cricket": "🏏",
        "baseball": "⚾",
        "american_football": "🏈",
        "rugby": "🏉",
        "volleyball": "🏐",
        "handball": "🤾",
        "badminton": "🏸",
        "table_tennis": "🏓",
        # Sports - Esports
        "esports": "🎮",
        "dota2": "🎮",
        "csgo": "🔫",
        "lol": "🎮",
        "valorant": "🎮",
        "overwatch": "🎮",
        "r6siege": "🎮",
        "sports_other": "🏆",
        "other": "🏆",
        # Markets
        "stocks": "📈",
        "bonds": "📊",
        "forex": "💱",
        "commodities": "🌾",
        "ipos": "📋",
        "earnings": "💰",
        "dividends": "💸",
        "splits": "✂️",
        "rates": "📊",
        "etf": "📊",
        "funds_etfs": "📊",
        "economic_data": "📊",
        "central_banks": "🏛️",
        # Tech
        "ai": "🤖",
        "bigtech": "💻",
        "hardware": "🔧",
        "software": "💿",
        "cybersecurity": "🛡️",
        "blockchain": "⛓️",
        "blockchain_tech": "⛓️",
        "startups": "🚀",
        "conferences": "🎤",
        "conference": "🎤",
        "release": "🚀",
        "launch": "🚀",
        "update": "🔄",
        # World
        "conflicts": "⚠️",
        "elections": "🗳️",
        "energy": "⚡",
        "geopolitics": "🌍",
        "diplomacy": "🤝",
        "sanctions": "🚫",
        "organizations": "🏛️",
        "migration": "👥",
        "climate": "🌱",
        "global_risks": "⚠️",
    }

    icon_key = get_icon(category, subcategory)
    return icon_map.get(icon_key, category_icons.get(category, "📰"))


def validate_sources() -> Tuple[bool, List[str]]:
    """
    Валидирует структуру источников.

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    sources = _load_sources()

    # Фильтруем только настоящие категории новостей
    filtered_sources = {cat: data for cat, data in sources.items() if cat in NEWS_CATEGORIES}

    if not filtered_sources:
        errors.append("Файл источников пуст или не найден")
        return False, errors

    for category, subcategories in filtered_sources.items():
        if not isinstance(subcategories, dict):
            errors.append(f"Категория '{category}' должна быть словарем")
            continue

        for subcategory, data in subcategories.items():
            if not isinstance(data, dict):
                errors.append(f"Подкатегория '{category}.{subcategory}' должна быть словарем")
                continue

            # Проверяем наличие иконки
            if "icon" not in data:
                errors.append(f"У подкатегории '{category}.{subcategory}' отсутствует иконка")

            # Проверяем источники
            sources_list = data.get("sources", [])
            if not isinstance(sources_list, list):
                errors.append(f"Источники в '{category}.{subcategory}' должны быть списком")
                continue

            for i, source in enumerate(sources_list):
                if not isinstance(source, dict):
                    errors.append(f"Источник #{i+1} в '{category}.{subcategory}' должен быть словарем")
                    continue

                if "name" not in source:
                    errors.append(f"Источник #{i+1} в '{category}.{subcategory}' без имени")
                if "url" not in source:
                    errors.append(f"Источник #{i+1} в '{category}.{subcategory}' без URL")

    return len(errors) == 0, errors


def get_statistics() -> Dict:
    """
    Возвращает статистику по источникам.

    Returns:
        Dict: Статистика с количеством категорий, подкатегорий и источников
    """
    sources = _load_sources()

    # Фильтруем только настоящие категории новостей
    filtered_sources = {cat: data for cat, data in sources.items() if cat in NEWS_CATEGORIES}

    total_categories = len(filtered_sources)
    total_subcategories = 0
    total_sources = 0

    for category, subcategories in filtered_sources.items():
        total_subcategories += len(subcategories)
        for subcategory, data in subcategories.items():
            sources_list = data.get("sources", [])
            total_sources += len(sources_list)

    return {
        "categories": total_categories,
        "subcategories": total_subcategories,
        "sources": total_sources,
        "avg_sources_per_subcategory": (
            round(total_sources / total_subcategories, 1) if total_subcategories > 0 else 0
        ),
    }


def reload_sources() -> bool:
    """
    Принудительно перезагружает источники из файла.

    Returns:
        bool: True если успешно перезагружено
    """
    global _sources_cache, _cache_timestamp
    _sources_cache = None
    _cache_timestamp = None

    try:
        _load_sources()
        return True
    except Exception as e:
        logger.error("❌ Ошибка перезагрузки источников: %s", e)
        return False
