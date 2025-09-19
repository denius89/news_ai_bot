"""
digests/ai_summary.py
Модуль для генерации AI-саммари дайджестов.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(news_list, max_tokens=300) -> str:
    """
    news_list — список словарей: [{"title": "...", "content": "...", "source": "..."}]
    Возвращает краткий дайджест 3–5 предложений.
    """
    if not news_list:
        return "Сегодня новостей нет."

    # Формируем текстовую выборку новостей
    text_block = "\n".join(
        f"- {item.get('title')} ({item.get('source')}): {item.get('content')[:200]}..."
        for item in news_list[:10]  # ограничим максимум 10 новостей за раз
    )

    prompt = f"""
Составь краткий новостной дайджест (3–5 предложений) на основе следующих новостей:

{text_block}

Формат: связный текст, а не список пунктов.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
