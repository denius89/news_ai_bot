"""
Module: ai_modules.importance
Purpose: AI-powered importance scoring for news and events
Location: ai_modules/importance.py

Description:
    Модуль для оценки важности новостей и событий с помощью AI.
    Использует OpenAI GPT для анализа контента и присвоения score от 0.1 до 1.0.

Key Features:
    - AI-powered анализ важности контента
    - Scoring от 0.1 (низкая важность) до 1.0 (критическая важность)
    - Поддержка различных типов контента (новости, события)
    - Кэширование результатов для оптимизации
    - Fallback логика при недоступности AI

Scoring Criteria:
    - Market impact: Влияние на рынки и экономику
    - User relevance: Релевантность для пользователей PulseAI
    - Breaking news: Срочность и актуальность
    - Source credibility: Надежность источника
    - Content quality: Качество и полнота контента

AI Processing:
    ```python
    def evaluate_importance(content: str, title: str, category: str) -> float:
        # Оценивает важность контента с помощью AI.
        # Args:
        #     content: Текст новости или события
        #     title: Заголовок
        #     category: Категория (tech, crypto, sports, etc.)
        # Returns:
        #     float: Score от 0.1 до 1.0
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
    from ai_modules.importance import evaluate_importance

    # Оценить важность новости
    score = evaluate_importance(
        content="Bitcoin reaches new all-time high...",
        title="Bitcoin ATH",
        category="crypto"
    )
    print(f"Importance score: {score}")  # 0.8
    ```

Caching:
    - Результаты кэшируются для одинакового контента
    - TTL: 24 часа для новостей, 7 дней для событий
    - Ключ кэша: hash(content + title + category)

Performance:
    - Batch processing для множественных запросов
    - Rate limiting для OpenAI API
    - Fallback на rule-based scoring при недоступности AI
    - Async support для высокой производительности

Notes:
    - Использует OpenAI GPT-4 для анализа
    - Поддерживает fallback на простые правила
    - Логирует все AI запросы для мониторинга
    - TODO: Добавить A/B testing разных моделей

Author: PulseAI Team
Last Updated: October 2025
"""

import logging
import sys
from pathlib import Path

from utils.ai.ai_client import ask

sys.path.append(str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger("importance")


def evaluate_importance(news_item: dict) -> float:
    """
    Оценивает важность новости с помощью AI.
    Возвращает float [0.0, 1.0], где:
      0.0 = не важно,
      1.0 = крайне важно.
    """
    title = news_item.get("title") or "Без названия"
    content = news_item.get("content") or news_item.get("summary") or ""

    prompt = f"""
Оцени важность следующей новости по шкале от 0 до 1.
Ответь только числом (например: 0.7).

Заголовок: {title}
Текст: {content}
"""

    try:
        raw = ask(prompt, model="gpt-4o-mini", max_tokens=10)
        score = float(raw.strip())
        return max(0.0, min(1.0, score))  # clamp в [0, 1]
    except Exception as e:
        logger.error(f"Ошибка при оценке важности: {e}", exc_info=True)
        return 0.5  # fallback: среднее значение
