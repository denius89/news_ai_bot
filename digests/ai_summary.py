# digests/ai_summary.py
"""AI-сводки и дайджесты.

Функции:
- generate_summary_why_important_json: получить JSON-аннотацию новости.
- generate_summary_why_important: текстовый блок для Telegram.
- generate_batch_summary: общий AI-дайджест по списку новостей.
"""

import os
import json
import logging
from typing import List, Dict, Union

from openai import OpenAI
from digests.prompts import PROMPTS
from utils.formatters import format_digest_output
from utils.clean_text import clean_for_telegram

logger = logging.getLogger("ai_summary")

_TEMPS = {
    "analytical": 0.7,
    "business": 0.6,
    "meme": 0.9,
    "why_important": 0.5,
}


def get_client() -> OpenAI:
    """Ленивое создание OpenAI-клиента на основе переменной окружения."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ Нет OPENAI_API_KEY, установите ключ в .env")
    return OpenAI(api_key=api_key)


def generate_summary_why_important_json(
    news_item: Dict,
    max_tokens: int = 400,
    style: str = "why_important",
) -> Dict:
    """Вернуть JSON с кратким резюме и списком «почему важно».

    Возвращаемая структура:
        {
          "summary": "короткое резюме",
          "why_important": ["п1", "п2", "п3"]
        }
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
        logger.error("Ошибка при JSON-аннотации: %s", e, exc_info=True)
        return {"summary": title, "why_important": []}


def generate_summary_why_important(
    news_item: Dict,
    max_tokens: int = 400,
    style: str = "why_important",
) -> str:
    """Вернуть HTML-блок для Telegram (с фильтрацией HTML)."""
    data = generate_summary_why_important_json(news_item, max_tokens, style)
    formatted = format_digest_output(data, style="why_important")
    return clean_for_telegram(formatted)


def generate_batch_summary(
    news_items: List[Dict],
    max_tokens: int = 1500,
    style: str = "analytical",
) -> str:
    """Сформировать цельный AI-дайджест в выбранном стиле."""
    if not news_items:
        return "Сегодня новостей нет."

    text_block = "\n".join(
        f"{i+1}. {item.get('title')}: {(item.get('content') or '')[:400]}"
        for i, item in enumerate(news_items)
    )
    links_block = "\n".join(
        f"- {item.get('title')}: {item.get('link')}"
        for item in news_items
        if item.get("link")
    )

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
        raw_text: Union[str, Dict] = response.choices[0].message.content.strip()
        formatted = format_digest_output(raw_text, style=style)

        if "<b>Почему это важно" not in formatted:
            formatted += (
                "\n\n<b>Почему это важно:</b>\n"
                "— Событие влияет на рынок\n"
                "— Важно для инвесторов"
            )

        return clean_for_telegram(formatted)
    except Exception as e:
        logger.error("Ошибка при batch-аннотации: %s", e, exc_info=True)
        return "⚠️ Ошибка генерации AI-дайджеста."
