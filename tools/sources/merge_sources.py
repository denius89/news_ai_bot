#!/usr/bin/env python3
"""
Скрипт для правильного объединения старых и новых RSS-источников.
"""

import asyncio
import logging
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def load_yaml_file(file_path: Path) -> Dict:
    """Загрузка YAML файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Ошибка загрузки {file_path}: {e}")
        return {}


def save_yaml_file(file_path: Path, data: Dict):
    """Сохранение YAML файла."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)
        logger.info(f"Файл сохранен: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка сохранения {file_path}: {e}")


def extract_urls_from_sources(sources_list: List) -> Set[str]:
    """Извлечение URL из списка источников."""
    urls = set()

    for source in sources_list:
        if isinstance(source, dict):
            url = source.get("url", "")
            if url:
                urls.add(url)
        elif isinstance(source, str):
            if ":" in source:
                # Формат "name: url"
                url = source.split(":", 1)[1].strip()
                if url:
                    urls.add(url)
            else:
                # Просто URL
                if source.strip():
                    urls.add(source.strip())

    return urls


def merge_sources(old_sources: List, new_sources: List) -> List:
    """Объединение старых и новых источников без дубликатов."""
    # Извлекаем URL из старых источников
    old_urls = extract_urls_from_sources(old_sources)

    # Извлекаем URL из новых источников
    new_urls = extract_urls_from_sources(new_sources)

    # Объединяем URL
    all_urls = old_urls.union(new_urls)

    # Создаем объединенный список источников
    merged_sources = []

    # Сначала добавляем старые источники
    for source in old_sources:
        if isinstance(source, dict):
            url = source.get("url", "")
            if url in all_urls:
                merged_sources.append(source)
                all_urls.discard(url)  # Убираем из множества, чтобы не дублировать
        elif isinstance(source, str):
            if ":" in source:
                url = source.split(":", 1)[1].strip()
            else:
                url = source.strip()

            if url in all_urls:
                merged_sources.append(source)
                all_urls.discard(url)

    # Затем добавляем новые источники, которых не было в старых
    for source in new_sources:
        if isinstance(source, dict):
            url = source.get("url", "")
            if url in all_urls:
                merged_sources.append(source)
        elif isinstance(source, str):
            if ":" in source:
                url = source.split(":", 1)[1].strip()
            else:
                url = source.strip()

            if url in all_urls:
                merged_sources.append(source)

    return merged_sources


def merge_configs(old_config: Dict, new_config: Dict) -> Dict:
    """Объединение старых и новых конфигураций."""
    merged_config = {}

    # Получаем все категории из обеих конфигураций
    all_categories = set(old_config.keys()).union(set(new_config.keys()))

    for category in all_categories:
        merged_config[category] = {}

        # Получаем старые и новые подкатегории для этой категории
        old_subcategories = old_config.get(category, {})
        new_subcategories = new_config.get(category, {})

        # Получаем все подкатегории
        all_subcategories = set(old_subcategories.keys()).union(set(new_subcategories.keys()))

        for subcategory in all_subcategories:
            merged_config[category][subcategory] = {}

            # Получаем старые и новые источники
            old_subcategory_data = old_subcategories.get(subcategory, {})
            new_subcategory_data = new_subcategories.get(subcategory, {})

            old_sources = old_subcategory_data.get("sources", [])
            new_sources = new_subcategory_data.get("sources", [])

            # Объединяем источники
            merged_sources = merge_sources(old_sources, new_sources)

            # Сохраняем иконку (приоритет у старой конфигурации)
            icon = old_subcategory_data.get("icon") or new_subcategory_data.get("icon")

            merged_config[category][subcategory]["sources"] = merged_sources
            if icon:
                merged_config[category][subcategory]["icon"] = icon

    return merged_config


async def main():
    """Основная функция объединения."""
    logger.info("🔄 Начинаем объединение старых и новых RSS-источников")

    # Пути к файлам
    backup_path = Path("config/sources.backup.20251005.yaml")
    current_path = Path("config/data/sources.yaml")

    # Загружаем старую и новую конфигурации
    logger.info("📖 Загружаем резервную копию")
    old_config = load_yaml_file(backup_path)

    logger.info("📖 Загружаем текущую конфигурацию")
    new_config = load_yaml_file(current_path)

    if not old_config:
        logger.error("❌ Не удалось загрузить резервную копию")
        return

    if not new_config:
        logger.error("❌ Не удалось загрузить текущую конфигурацию")
        return

    # Объединяем конфигурации
    logger.info("🔗 Объединяем конфигурации")
    merged_config = merge_configs(old_config, new_config)

    # Создаем новую резервную копию
    backup_new_path = Path("config/sources.backup.merged.yaml")
    save_yaml_file(backup_new_path, merged_config)

    # Сохраняем объединенную конфигурацию
    logger.info("💾 Сохраняем объединенную конфигурацию")
    save_yaml_file(current_path, merged_config)

    # Статистика
    total_sources = 0
    for category, subcategories in merged_config.items():
        for subcategory, data in subcategories.items():
            sources = data.get("sources", [])
            total_sources += len(sources)

    logger.info(f"✅ Объединение завершено!")
    logger.info(f"📊 Всего источников в объединенной конфигурации: {total_sources}")

    # Показываем статистику по категориям
    for category, subcategories in merged_config.items():
        category_sources = 0
        for subcategory, data in subcategories.items():
            sources = data.get("sources", [])
            category_sources += len(sources)

        if category_sources > 0:
            logger.info(f"  • {category}: {category_sources} источников")


if __name__ == "__main__":
    asyncio.run(main())
