"""
digests/ai_summary.py
Модуль для генерации AI-саммари дайджестов.
"""

import os
import json
import logging
from typing import List, Dict  # ✅ фикс: добавляем импорт

from openai import OpenAI

logger = logging.getLogger("ai_summary")


def get_client() -> OpenAI:
    """Ленивое создание клиента OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ Нет OPENAI_API_KEY, установите ключ в .env")
    return OpenAI(api_key=api_key)


def generate_summary(news_list: List[Dict], max_tokens: int = 300) -> str:
    """Краткий дайджест (3–5 предложений)"""
    if not news_list:
        return "Сегодня новостей нет."

    text_block = "\n".join(
        [
            f"- {item.get('title','Без названия')} ({item.get('source','—')}): {(item.get('content') or '')[:200]}..."
            for item in news_list[:10]
        ]
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


def generate_summary_why_important(news_item: Dict, max_tokens: int = 400) -> Dict:
    """Резюме + «Почему важно» (до 3 пунктов)"""
    title = news_item.get("title") or "Без названия"
    content = news_item.get("content") or news_item.get("summary") or ""

    prompt = f"""
Ты — аналитик новостей.
Дай JSON:
{{
  "summary": "короткое резюме (1–2 предложения)",
  "why_important": ["пункт 1", "пункт 2", "пункт 3"]
}}

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
            temperature=0.5,
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "summary": data.get("summary") or title,
            "why_important": data.get("why_important", [])[:3],
        }
    except Exception as e:
        logger.error(f"Ошибка при AI-аннотации: {e}", exc_info=True)
        return {"summary": title, "why_important": []}


def generate_batch_summary(news_items: List[Dict], max_tokens: int = 1500) -> str:
    """
    Batch-аннотация: формирует связный аналитический дайджест в стиле FT/WSJ/ Economist.
    """
    if not news_items:
        return "Сегодня новостей нет."

    # Подготовка блока фактов
    text_block = "\n".join(
        [
            f"{i+1}. {item.get('title')}: {(item.get('content') or '')[:400]}"
            for i, item in enumerate(news_items)
        ]
    )

    # Подготовка блока ссылок
    links_block = "\n".join(
        [f"- {item.get('title')}: {item.get('link')}" for item in news_items if item.get("link")]
    )

    prompt = f"""
Ты — опытный журналист-аналитик уровня Financial Times, Wall Street Journal или The Economist.
Твоя задача — написать цельный аналитический дайджест, который читается как профессиональная статья.

🎯 Правила стиля:
- Тон: деловая журналистика высокого уровня — уверенный, аналитический, но живой.
- Читатель: образованный, следит за рынками и экономикой, ценит глубину анализа.
- Начинай с широкого контекста: почему именно сейчас рынок в центре внимания.
- Встраивай отдельные события как примеры, иллюстрирующие общую картину.
- Используй переходы («однако», «в то же время», «на фоне этого») для связности.
- Делай выводы: что это значит для рынков, инвесторов, геополитики.
- Все ссылки вставляй органично через HTML: `<a href="URL">Подробнее</a>`.
- Используй только HTML для форматирования текста:
  - `<b>` — жирный
  - `<i>` — курсив
  - `<a href="...">Подробнее</a>` — ссылки
  - Никаких `###`, `**`, `_` или Markdown.

📑 Структура:
1. Вводный абзац — общая картина и главная тема.
2. Основная часть (2–3 абзаца) — отдельные факты + контекст, связь между ними.
3. Абзац «Прогнозы и последствия».
4. В конце — блок «Почему это важно» (3–5 пунктов).
❗ После блока «Почему это важно» больше НИЧЕГО не писать. Это должен быть финал текста.

<b>Почему это важно:</b>
1. Ключевой вывод для инвесторов или рынков.
2. Последствия для компаний, регуляторов или технологий.
3. Долгосрочные тренды и риски.
(строго 3–5 пунктов, никаких заключений после списка)

📌 Данные для анализа:
{text_block}

📎 Ссылки для использования:
{links_block}
"""

    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,  # чуть выше, чтобы текст был «живее»
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка при batch-аннотации: {e}", exc_info=True)
        return "⚠️ Ошибка генерации AI-дайджеста."
