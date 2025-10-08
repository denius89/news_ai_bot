import sys

sys.path.insert(0, "/Users/denisfedko/news_ai_bot")

import logging
import os

from utils.ai.ai_client import ask

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
