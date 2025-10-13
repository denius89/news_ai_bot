"""
Форматтер для преобразования JSON дайджестов в читаемый HTML текст.
"""

import json
import logging
from typing import Dict, Any, List  # noqa: F401

logger = logging.getLogger("json_formatter")


def format_json_digest_to_html(json_data: str) -> str:
    """
    Преобразует JSON дайджест в читаемый HTML текст.

    Args:
        json_data: JSON строка или уже распарсенный dict

    Returns:
        HTML строка для отображения
    """
    try:
        # Если это строка, парсим JSON
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        if not isinstance(data, dict):
            logger.warning("JSON data is not a dictionary")
            return str(json_data)

        # Извлекаем основные поля
        title = data.get("title", "Дайджест новостей")
        dek = data.get("dek", "")
        summary = data.get("summary", "")
        why_important = data.get("why_important", [])
        context = data.get("context", "")
        what_next = data.get("what_next", "")
        sources_cited = data.get("sources_cited", [])

        # Формируем HTML
        html_parts = []

        # Заголовок
        if title:
            html_parts.append(f"<b>{title}</b>")

        # Подзаголовок
        if dek:
            html_parts.append(f"<i>{dek}</i>")

        # Основной текст
        if summary:
            html_parts.append(f"\n{summary}")

        # Почему важно
        if why_important and isinstance(why_important, list):
            html_parts.append("\n<b>Почему это важно:</b>")
            for i, point in enumerate(why_important, 1):
                if point and isinstance(point, str):
                    html_parts.append(f"{i}. {point}")

        # Дополнительный контекст
        if context:
            html_parts.append(f"\n<b>Контекст:</b>\n{context}")

        # Что ожидать дальше
        if what_next:
            html_parts.append(f"\n<b>Что дальше:</b>\n{what_next}")

        # Источники
        if sources_cited and isinstance(sources_cited, list):
            html_parts.append("\n<b>Источники:</b>")
            for source in sources_cited:
                if source and isinstance(source, str):
                    html_parts.append(f"• {source}")

        return "\n".join(html_parts)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return str(json_data)
    except Exception as e:
        logger.error(f"Error formatting JSON digest: {e}")
        return str(json_data)


def clean_json_from_text(text: str) -> str:
    """
    Очищает текст от JSON структур, оставляя только содержимое.

    Args:
        text: Текст, который может содержать JSON

    Returns:
        Очищенный текст
    """
    try:
        # Пытаемся найти JSON в тексте
        if text.strip().startswith("{") and text.strip().endswith("}"):
            # Весь текст - это JSON
            return format_json_digest_to_html(text)

        # Ищем JSON блоки в тексте
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                # Строка содержит JSON
                try:
                    json_obj = json.loads(stripped)
                    html_content = format_json_digest_to_html(json_obj)
                    cleaned_lines.append(html_content)
                except json.JSONDecodeError:
                    cleaned_lines.append(line)
            elif stripped.startswith("```json"):
                # Блок JSON с маркерами
                continue
            elif stripped.startswith("```") and not stripped.startswith("```json"):
                # Конец блока
                continue
            else:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    except Exception as e:
        logger.error(f"Error cleaning JSON from text: {e}")
        return text
