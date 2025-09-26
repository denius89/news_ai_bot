"""
digests/ai_summary.py
Модуль для генерации AI-саммари дайджестов.
"""

import os
from typing import List, Dict, Optional

from openai import OpenAI


def get_client() -> OpenAI:
    """Ленивое создание клиента OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "❌ Нет OPENAI_API_KEY, установите ключ в .env или пропустите интеграционный тест"
        )
    return OpenAI(api_key=api_key)


def generate_summary(news_list: List[Dict], max_tokens: int = 300) -> str:
    """
    Генерация обычного краткого дайджеста (3–5 предложений).
    news_list — список словарей: [{"title": "...", "content": "...", "source": "..."}]
    """
    if not news_list:
        return "Сегодня новостей нет."

    # Формируем текстовую выборку новостей
    text_block = "\n".join(
        f"- {item.get('title')} ({item.get('source')}): {item.get('content', '')[:200]}..."
        for item in news_list[:10]
    )

    prompt = f"""
Составь краткий новостной дайджест (3–5 предложений) на основе следующих новостей:

{text_block}

Формат: связный текст, а не список пунктов.
    """

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


def generate_summary_why_important(
    news_item: Dict,
    max_tokens: int = 300,
    title: Optional[str] = None,
) -> str:
    """
    Генерация саммари для одной новости в стиле «почему важно».

    Формат:
    <Краткое резюме (1–2 предложения)>

    Почему важно:
    — Пункт 1
    — Пункт 2
    — Пункт 3
    """
    title = title or news_item.get("title", "Новость")
    content = news_item.get("content") or ""

    prompt = f"""
Составь краткое саммари для новости:

Заголовок: {title}
Текст: {content}

Формат ответа:
<Краткое резюме в 1–2 предложения>

Почему важно:
— причина 1
— причина 2
— причина 3
    """

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
