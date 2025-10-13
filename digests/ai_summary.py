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
import time
from typing import List, Union
from pathlib import Path

from openai import OpenAI
from digests.prompts import PROMPTS
from utils.text.formatters import format_digest_output
from models.news import NewsItem
from utils.text.clean_text import clean_for_telegram

# Setup logger
logger = logging.getLogger(__name__)

# Try to import v2 prompts for backward compatibility
try:
    from digests.prompts_v2 import build_prompt, validate_sources, validate_output_schema, calculate_confidence_score
    HAS_V2 = True
except ImportError:
    HAS_V2 = False
    logger.warning("prompts_v2 not found, using legacy prompts")

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / "config_files" / "environment" / ".env")

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
    news_item: NewsItem,
    max_tokens: int = 400,
    style: str = "why_important",
) -> dict:
    """Вернуть JSON с кратким резюме и списком «почему важно».

    Возвращаемая структура:
        {
          "summary": "короткое резюме",
          "why_important": ["п1", "п2", "п3"]
        }
    """
    title = news_item.title or "Без названия"
    content = news_item.content or ""

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
    news_item: NewsItem,
    max_tokens: int = 400,
    style: str = "why_important",
) -> str:
    """Вернуть HTML-блок для Telegram (с фильтрацией HTML)."""
    data = generate_summary_why_important_json(news_item, max_tokens, style)
    formatted = format_digest_output(data, style="why_important")
    return clean_for_telegram(formatted)


def generate_batch_summary(
    news_items: List[NewsItem],
    max_tokens: int = 1500,
    style: str = "analytical",
) -> str:
    """Сформировать цельный AI-дайджест в выбранном стиле."""
    if not news_items:
        return "Сегодня новостей нет."

    text_block = "\n".join(f"{i+1}. {item.title}: {(item.content or '')[:400]}" for i, item in enumerate(news_items))
    links_block = "\n".join(f"- {item.title}: {item.link}" for item in news_items if item.link)

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
        raw_text: Union[str, dict] = response.choices[0].message.content.strip()

        # Check if response is JSON and convert to HTML
        if isinstance(raw_text, str) and raw_text.strip().startswith('{') and raw_text.strip().endswith('}'):
            from digests.json_formatter import format_json_digest_to_html
            logger.info("Converting JSON response to HTML in ai_summary")
            formatted = format_json_digest_to_html(raw_text)
        else:
            formatted = format_digest_output(raw_text, style=style)

        if "<b>Почему это важно" not in formatted:
            formatted += "\n\n<b>Почему это важно:</b>\n" "— Событие влияет на рынок\n" "— Важно для инвесторов"

        return clean_for_telegram(formatted)
    except Exception as e:
        logger.error("Ошибка при batch-аннотации: %s", e, exc_info=True)
        return "⚠️ Ошибка генерации AI-дайджеста."


def generate_summary_journalistic_v2(
    news_items: List[NewsItem],
    lang: str = "ru",
    category: str = "tech",
    style_profile: str = "analytical",
    tone: str = "neutral",
    length: str = "medium",
    audience: str = "general",
    max_tokens: int = 800,
    min_importance: float = 0.6,
    min_credibility: float = 0.7,
) -> dict:
    """
    Generate journalistic-style digest with v2 prompts.

    Args:
        news_items: List of NewsItem objects
        lang: Language (default: "ru")
        category: News category (crypto, markets, tech, sports, world)
        style_profile: Style profile (newsroom, analytical, magazine, casual)
        tone: Tone (neutral, insightful, critical, optimistic)
        length: Length (short, medium, long)
        audience: Audience (general, pro)
        max_tokens: Maximum tokens for generation
        min_importance: Minimum importance threshold
        min_credibility: Minimum credibility threshold

    Returns:
        Dictionary with structured digest or error information
    """
    if not HAS_V2:
        logger.warning("V2 prompts not available, falling back to legacy generation")
        return {
            "error": "V2 prompts not available",
            "fallback": True,
            "legacy_result": generate_batch_summary(news_items, max_tokens, style_profile)
        }

    if not news_items:
        return {
            "error": "No news items provided",
            "skipped_reason": "empty input"
        }

    # Start timer for generation time tracking
    start_time = time.time()

    # Prepare sources for validation
    sources = []
    for item in news_items:
        sources.append({
            "title": item.title or "Без названия",
            "content": item.content or "",
            "importance": item.importance or 0.0,
            "credibility": item.credibility or 0.0,
            "source": item.source or "Unknown",
            "published_at": item.published_at_fmt if item.published_at else "Unknown"
        })

    # Validate sources
    validation_result = validate_sources(sources, min_importance, min_credibility)

    if not validation_result["valid"]:
        logger.warning(f"Skipping generation due to: {validation_result['reason']}")
        return {
            "skipped_reason": validation_result["reason"],
            "skipped_count": validation_result["skipped_count"],
            "valid_sources_count": len(validation_result["valid_sources"])
        }

    # Prepare news text for AI
    news_text = "\n\n".join([
        f"ЗАГОЛОВОК: {source['title']}\n"
        f"ИСТОЧНИК: {source['source']} | ДАТА: {source['published_at']}\n"
        f"ДОСТОВЕРНОСТЬ: {source['credibility']:.1f} | ВАЖНОСТЬ: {source['importance']:.1f}\n"
        f"СОДЕРЖАНИЕ: {source['content'][:300]}..."
        for source in validation_result["valid_sources"]
    ])

    # Build prompts
    try:
        input_payload = {
            "category": category,
            "style_profile": style_profile,
            "tone": tone,
            "length": length,
            "audience": audience,
            "news_text": news_text,
            "min_importance": min_importance,
            "min_credibility": min_credibility
        }

        system_prompt, user_prompt = build_prompt(input_payload)

    except Exception as e:
        logger.error(f"Error building prompts: {e}")
        return {
            "error": f"Prompt building failed: {str(e)}"
        }

    # Call OpenAI
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=_TEMPS.get(style_profile, 0.7),
        )

        raw_response = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            parsed_output = json.loads(raw_response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {raw_response}")
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "raw_response": raw_response
            }

        # Validate output schema
        schema_validation = validate_output_schema(parsed_output)
        if not schema_validation["valid"]:
            logger.error(f"Schema validation failed: {schema_validation['errors']}")
            return {
                "error": f"Schema validation failed: {schema_validation['errors']}",
                "parsed_output": parsed_output
            }

        # Calculate confidence score
        confidence = calculate_confidence_score(parsed_output, len(validation_result["valid_sources"]))

        # Calculate generation time
        generation_time = time.time() - start_time

        # Update meta with confidence and generation time
        if "meta" in parsed_output:
            parsed_output["meta"]["confidence"] = confidence
            parsed_output["meta"]["generation_time_sec"] = round(generation_time, 2)
        else:
            parsed_output["meta"] = {
                "confidence": confidence,
                "generation_time_sec": round(generation_time, 2)
            }

        logger.info(f"Successfully generated v2 digest with confidence: {confidence}, time: {generation_time:.2f}s")
        return parsed_output

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "error": f"OpenAI API failed: {str(e)}"
        }
