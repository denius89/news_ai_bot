# digests/ai_summary.py
import os
import json
import logging
from typing import List, Dict

from openai import OpenAI
from digests.prompts import PROMPTS  # ✅ все промты централизованно

logger = logging.getLogger("ai_summary")

# Температуры по умолчанию для разных стилей
_TEMPS = {
    "analytical": 0.7,
    "business": 0.6,
    "meme": 0.9,
    "why_important": 0.5,
}


def get_client() -> OpenAI:
    """Создание клиента OpenAI (ленивое)"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ Нет OPENAI_API_KEY, установите ключ в .env")
    return OpenAI(api_key=api_key)


def generate_summary_why_important(
    news_item: Dict,
    max_tokens: int = 400,
    style: str = "why_important",
) -> Dict:
    """
    Резюме + «Почему важно» (до 3 пунктов).
    Работает через PROMPTS["why_important"] или кастомный стиль.
    """
    title = news_item.get("title") or "Без названия"
    content = news_item.get("content") or news_item.get("summary") or ""

    base_prompt = PROMPTS.get(style, PROMPTS["why_important"])
    prompt = f"""{base_prompt}

Новость:
Заголовок: {title}
Текст: {content}
"""

    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=_TEMPS.get(style, 0.5),
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "summary": data.get("summary") or title,
            "why_important": data.get("why_important", [])[:3],
        }
    except Exception as e:
        logger.error(f"Ошибка при AI-аннотации: {e}", exc_info=True)
        return {"summary": title, "why_important": []}


def generate_batch_summary(
    news_items: List[Dict],
    max_tokens: int = 1500,
    style: str = "analytical",
) -> str:
    """
    Формирует цельный дайджест в выбранном стиле (PROMPTS[style]).
    """
    if not news_items:
        return "Сегодня новостей нет."

    # Подготовка данных
    text_block = "\n".join(
        [
            f"{i+1}. {item.get('title')}: {(item.get('content') or '')[:400]}"
            for i, item in enumerate(news_items)
        ]
    )
    links_block = "\n".join(
        [f"- {item.get('title')}: {item.get('link')}" for item in news_items if item.get("link")]
    )

    # Выбор промта и подстановка
    base_prompt = PROMPTS.get(style, PROMPTS["analytical"])
    prompt = base_prompt.format(text_block=text_block, links_block=links_block)

    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=_TEMPS.get(style, 0.7),
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка при batch-аннотации: {e}", exc_info=True)
        return "⚠️ Ошибка генерации AI-дайджеста."
