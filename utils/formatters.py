from typing import Union, Dict, Any, List


def format_digest_output(data: Union[str, Dict[str, Any]], style: str = "analytical") -> str:
    """
    Универсальный форматтер для дайджестов.
    - Если style == "why_important" → форматируем JSON в HTML с буллетами.
    - Для остальных стилей → возвращаем строку как есть.
    """

    if style == "why_important":
        if isinstance(data, dict):
            summary = data.get("summary", "—")
            points: List[str] = data.get("why_important", [])
            formatted_points = "\n".join([f"{i+1}. {p}" for i, p in enumerate(points) if p])

            return (
                f"<b>Краткое резюме:</b>\n{summary}\n\n"
                f"<b>Почему это важно:</b>\n{formatted_points if formatted_points else '—'}"
            )
        else:
            # fallback: если пришла строка, просто вернём её
            return str(data)

    # для текстовых стилей возвращаем как есть
    return str(data).strip()
