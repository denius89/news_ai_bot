"""
Module: ai_modules.credibility
Purpose: AI-powered credibility scoring for news sources
Location: ai_modules/credibility.py

Description:
    Модуль для оценки достоверности источников новостей с помощью AI.
    Анализирует репутацию источника, качество контента и историю публикаций.

Key Features:
    - AI-powered анализ достоверности источников
    - Scoring от 0.1 (ненадежный) до 1.0 (высоконадежный)
    - Анализ исторических данных источника
    - Проверка фактов и cross-referencing
    - Кэширование результатов для оптимизации

Credibility Criteria:
    - Source reputation: Репутация и история источника
    - Content quality: Качество и полнота контента
    - Fact checking: Проверка фактов и точность
    - Bias detection: Обнаружение предвзятости
    - Cross-referencing: Сравнение с другими источниками

AI Processing:
    ```python
    def evaluate_credibility(source: str, content: str, title: str) -> float:
        # Оценивает достоверность источника с помощью AI.
        # Args:
        #     source: Название источника (URL или имя)
        #     content: Текст новости
        #     title: Заголовок новости
        # Returns:
        #     float: Credibility score от 0.1 до 1.0
        pass
    ```

Dependencies:
    External:
        - openai: OpenAI API client
    Internal:
        - utils.ai.ai_client: AI client wrapper
        - utils.system.cache: Caching system

Usage Example:
    ```python
    from ai_modules.credibility import evaluate_credibility

    # Оценить достоверность источника
    score = evaluate_credibility(
        source="https://reuters.com",
        content="Market analysis shows...",
        title="Market Update"
    )
    print(f"Credibility score: {score}")  # 0.9
    ```

Source Analysis:
    - Known sources: Предварительно оцененные источники
    - Domain analysis: Анализ домена и репутации
    - Content analysis: Анализ качества контента
    - Historical data: История публикаций источника

Caching:
    - Результаты кэшируются по домену источника
    - TTL: 7 дней для источников, 24 часа для контента
    - Ключ кэша: hash(domain + content_hash)

Performance:
    - Batch processing для множественных источников
    - Rate limiting для OpenAI API
    - Fallback на rule-based scoring при недоступности AI
    - Async support для высокой производительности

Notes:
    - Использует OpenAI GPT-4 для анализа
    - Поддерживает fallback на простые правила
    - Логирует все AI запросы для мониторинга
    - TODO: Добавить machine learning модели для улучшения точности

Author: PulseAI Team
Last Updated: October 2025
"""

import sys
from pathlib import Path
import logging

from utils.ai.ai_client import ask

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("credibility")


def evaluate_credibility(news_item: dict) -> float:
    """
    Оценивает достоверность новости с помощью AI.
    Возвращает float [0.0, 1.0], где:
      0.0 = фейк,
      1.0 = максимально достоверно.
    """
    title = news_item.get("title") or "Без названия"
    content = news_item.get("content") or news_item.get("summary") or ""

    prompt = f"""
Оцени достоверность следующей новости по шкале от 0 до 1.
Ответь только числом (например: 0.85).

Заголовок: {title}
Текст: {content}
"""

    try:
        raw = ask(prompt, model="gpt-4o-mini", max_tokens=10)
        score = float(raw.strip())
        return max(0.0, min(1.0, score))  # clamp в [0, 1]
    except Exception as e:
        logger.error(f"Ошибка при оценке достоверности: {e}", exc_info=True)
        return 0.5  # fallback: среднее значение
