#!/usr/bin/env python3
"""
Скрипт для очистки старых новостей и загрузки 500 новых на разные тематики
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database.db_models import supabase, safe_execute
from parsers.rss_parser import parse_source
from services.categories import get_all_sources
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
import random
from datetime import datetime, timezone

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_old_news():
    """Очищает все старые новости из базы данных"""
    logger.info("🗑️ Очищаем старые новости...")
    
    try:
        # Удаляем все новости
        result = safe_execute(
            supabase.table("news").delete().neq("uid", "")
        )
        logger.info(f"✅ Удалено {len(result.data) if result.data else 0} старых новостей")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке новостей: {e}")
        return False

def load_news_from_sources(target_count=500):
    """Загружает новости из различных источников"""
    logger.info(f"📰 Загружаем {target_count} новых новостей...")
    
    # Получаем все источники из categories service
    try:
        all_sources_data = get_all_sources()
        logger.info(f"📋 Найдено {len(all_sources_data)} источников")
    except Exception as e:
        logger.error(f"❌ Ошибка при получении источников: {e}")
        return 0
    
    # Перемешиваем источники для разнообразия
    random.shuffle(all_sources_data)
    
    loaded_count = 0
    processed_sources = 0
    
    for category, subcategory, source_name, source_url in all_sources_data:
        if loaded_count >= target_count:
            break
            
        try:
            logger.info(f"🔄 Обрабатываем {source_name} ({category}/{subcategory})")
            
            # Парсим RSS фид
            news_items = parse_source(
                source_url, 
                category, 
                subcategory, 
                source_name
            )
            
            if not news_items:
                logger.warning(f"⚠️ Нет новостей в {source_name}")
                continue
            
            # Обрабатываем каждую новость
            for item in news_items:
                if loaded_count >= target_count:
                    break
                    
                try:
                    # AI анализ
                    credibility = evaluate_credibility(item)
                    importance = evaluate_importance(item)
                    
                    # Подготавливаем данные для вставки
                    news_data = {
                        'uid': item['uid'],
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'published_at': item.get('published_at'),
                        'content': item.get('content', ''),
                        'credibility': credibility,
                        'importance': importance,
                        'source': source_name,
                        'category': category,
                        'subcategory': subcategory
                    }
                    
                    # Вставляем в базу данных
                    result = safe_execute(
                        supabase.table("news").insert(news_data)
                    )
                    
                    if result.data:
                        loaded_count += 1
                        if loaded_count % 50 == 0:
                            logger.info(f"📊 Загружено {loaded_count}/{target_count} новостей")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при обработке новости: {e}")
                    continue
            
            processed_sources += 1
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке источника {source_name}: {e}")
            continue
    
    logger.info(f"✅ Загружено {loaded_count} новостей из {processed_sources} источников")
    return loaded_count

def main():
    """Основная функция"""
    logger.info("🚀 Начинаем обновление новостей...")
    
    if not supabase:
        logger.error("❌ Supabase не инициализирован")
        return False
    
    # Очищаем старые новости
    if not clear_old_news():
        logger.error("❌ Не удалось очистить старые новости")
        return False
    
    # Загружаем новые новости
    loaded_count = load_news_from_sources(500)
    
    if loaded_count > 0:
        logger.info(f"🎉 Успешно загружено {loaded_count} новых новостей!")
        return True
    else:
        logger.error("❌ Не удалось загрузить новости")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
