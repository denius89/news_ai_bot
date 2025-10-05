#!/usr/bin/env python3
"""
Скрипт для заполнения AI анализа (credibility/importance) для всех новостей в базе данных
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database.db_models import supabase, safe_execute
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_news_without_ai_analysis():
    """Получает новости без AI анализа или с дефолтными значениями"""
    logger.info("🔍 Ищем новости без качественного AI анализа...")
    
    try:
        # Получаем новости где credibility или importance равны null ИЛИ равны 0.5 (дефолтные значения)
        result = safe_execute(
            supabase.table("news")
            .select("*")
            .or_("credibility.is.null,importance.is.null,credibility.eq.0.5,importance.eq.0.5")
        )
        
        if result.data:
            logger.info(f"📊 Найдено {len(result.data)} новостей с дефолтными или отсутствующими AI оценками")
            return result.data
        else:
            logger.info("✅ Все новости уже имеют качественный AI анализ")
            return []
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении новостей: {e}")
        return []

def update_news_ai_analysis(news_uid, credibility, importance):
    """Обновляет AI анализ для конкретной новости"""
    try:
        result = safe_execute(
            supabase.table("news")
            .update({
                "credibility": credibility,
                "importance": importance
            })
            .eq("uid", news_uid)
        )
        
        if result.data:
            return True
        else:
            logger.warning(f"⚠️ Не удалось обновить новость {news_uid}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении новости {news_uid}: {e}")
        return False

def process_news_batch(news_list):
    """Обрабатывает батч новостей для AI анализа"""
    processed = 0
    errors = 0
    
    for news_item in news_list:
        try:
            news_uid = news_item['uid']
            logger.info(f"🔄 Обрабатываем: {news_item['title'][:50]}...")
            
            # AI анализ
            credibility = evaluate_credibility(news_item)
            importance = evaluate_importance(news_item)
            
            # Обновляем в базе
            if update_news_ai_analysis(news_uid, credibility, importance):
                processed += 1
                logger.info(f"✅ Обновлено: credibility={credibility:.2f}, importance={importance:.2f}")
            else:
                errors += 1
                
            # Показываем прогресс каждые 10 новостей
            if (processed + errors) % 10 == 0:
                logger.info(f"📊 Прогресс: {processed + errors}/{len(news_list)} обработано")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке новости {news_item.get('uid', 'unknown')}: {e}")
            errors += 1
            continue
    
    return processed, errors

def main():
    """Основная функция"""
    logger.info("🚀 Начинаем заполнение AI анализа...")
    
    if not supabase:
        logger.error("❌ Supabase не инициализирован")
        return False
    
    # Получаем новости без AI анализа
    news_list = get_news_without_ai_analysis()
    
    if not news_list:
        logger.info("🎉 Все новости уже имеют AI анализ!")
        return True
    
    logger.info(f"📝 Начинаем обработку {len(news_list)} новостей...")
    
    # Обрабатываем новости
    processed, errors = process_news_batch(news_list)
    
    # Итоги
    logger.info(f"🎯 Результаты:")
    logger.info(f"   ✅ Успешно обработано: {processed}")
    logger.info(f"   ❌ Ошибок: {errors}")
    logger.info(f"   📊 Всего новостей: {len(news_list)}")
    
    if processed > 0:
        logger.info(f"🎉 AI анализ успешно добавлен к {processed} новостям!")
        return True
    else:
        logger.error("❌ Не удалось обработать ни одной новости")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
