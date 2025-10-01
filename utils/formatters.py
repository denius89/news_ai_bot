from typing import Union, Dict, Any, List, Optional
from html import escape
from datetime import datetime
import zoneinfo

from models.news import NewsItem
from models.event import EventItem


def format_date(
    dt: Optional[datetime], fmt: str = "%-d %b %Y, %H:%M", tz: str = "Europe/Warsaw"
) -> str:
    """
    Format datetime object to human-readable string with timezone support.

    Args:
        dt: datetime object to format (can be None)
        fmt: strftime format string (default: "%-d %b %Y, %H:%M")
        tz: target timezone (default: "Europe/Warsaw")

    Returns:
        Formatted date string or "—" if None
    """
    if not dt:
        return "—"

    try:
        # Convert to target timezone
        target_tz = zoneinfo.ZoneInfo(tz)
        localized_dt = dt.astimezone(target_tz)

        # Format with the provided format
        return localized_dt.strftime(fmt)
    except Exception:
        # Fallback to ISO format with minutes precision
        try:
            return dt.isoformat(timespec="minutes")
        except Exception:
            return "—"


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


def format_news_item(item: NewsItem, index: Optional[int] = None) -> str:
    """
    HTML-блок одной новости с метриками, датой и ссылкой.
    """
    title_raw = (item.title or item.source or "Untitled").strip()
    title = escape(title_raw)
    link = item.link or ""
    source = escape(item.source or "—")
    published = format_date(item.published_at)

    cred = float(item.credibility or 0.0)
    imp = float(item.importance or 0.0)
    cred_icon = "✅" if cred > 0.7 else "⚠️" if cred > 0.4 else "❌"
    imp_icon = "🔥" if imp > 0.7 else "⚡" if imp > 0.4 else "💤"

    summary = (item.content or "").strip()
    if len(summary) > 260:
        summary = summary[:259] + "…"
    summary = escape(summary)

    prefix = f"{index}. " if index is not None else ""
    title_line = (
        f"<b>{prefix}<a href=\"{escape(link)}\">{title}</a></b>"
        if link
        else f"<b>{prefix}{title}</b>"
    )

    if summary:
        return (
            f"\n{title_line}\n"
            f"{source} · {published}\n"
            f"{cred_icon} <b>Credibility:</b> {cred:.2f} · "
            f"{imp_icon} <b>Importance:</b> {imp:.2f}\n"
            f"— {summary}"
        )
    return (
        f"\n{title_line}\n"
        f"{source} · {published}\n"
        f"{cred_icon} <b>Credibility:</b> {cred:.2f} · "
        f"{imp_icon} <b>Importance:</b> {imp:.2f}"
    )


def format_news(
    news_list: List[NewsItem], limit: Optional[int] = None, with_header: bool = True
) -> str:
    """
    Полный HTML-дайджест: заголовок и нумерованный список новостей.
    """
    if not news_list:
        if with_header:
            return "📰 <b>Дайджест новостей:</b>\n\nСегодня новостей нет."
        return "Сегодня новостей нет."
    items = news_list[:limit] if limit else news_list
    lines: List[str] = ["📰 <b>Дайджест новостей:</b>"] if with_header else []
    for idx, it in enumerate(items, start=1):
        lines.append(format_news_item(it, index=idx))
    text = "\n".join(lines)
    return text if len(text) <= 4000 else text[:3999] + "…"


def format_ai_fallback() -> str:
    """
    Блок по умолчанию «Почему это важно», если LLM не вернул пунктов.
    """
    return (
        "\n\n<b>Почему это важно:</b>\n"
        "— Событие влияет на рынок\n"
        "— Важно для инвесторов\n"
        "— Может повлиять на стратегию компаний"
    )


def format_news_items(news: List[NewsItem], limit: int = 5, min_importance: float = 0.4) -> str:
    """
    HTML-форматирование списка NewsItem для Telegram.
    Использует свойства модели: title, source, link, published_at_fmt, credibility, importance, content.
    """
    if not news:
        return "⚠️ No fresh news"

    filtered = [n for n in news if float(n.importance or 0.0) >= float(min_importance)]
    if not filtered:
        return "⚠️ No important news today"

    lines: List[str] = ["📰 <b>Top news</b>"]
    for i, item in enumerate(filtered[:limit], start=1):
        title_raw = (item.title or item.source or "Untitled").strip()
        title = escape(title_raw)
        link = item.link or ""
        source = escape(item.source or "—")
        published = format_date(item.published_at)

        cred = float(item.credibility or 0.0)
        imp = float(item.importance or 0.0)
        cred_icon = "✅" if cred > 0.7 else "⚠️" if cred > 0.4 else "❌"
        imp_icon = "🔥" if imp > 0.7 else "⚡" if imp > 0.4 else "💤"

        summary = (item.content or "").strip()
        if len(summary) > 260:
            summary = summary[:259] + "…"
        summary = escape(summary)

        title_line = (
            f"<b>{i}. <a href=\"{escape(link)}\">{title}</a></b>"
            if link
            else f"<b>{i}. {title}</b>"
        )

        if summary:
            lines.append(
                f"\n{title_line}\n"
                f"{source} · {published}\n"
                f"{cred_icon} <b>Credibility:</b> {cred:.2f} · "
                f"{imp_icon} <b>Importance:</b> {imp:.2f}\n"
                f"— {summary}"
            )
        else:
            lines.append(
                f"\n{title_line}\n"
                f"{source} · {published}\n"
                f"{cred_icon} <b>Credibility:</b> {cred:.2f} · "
                f"{imp_icon} <b>Importance:</b> {imp:.2f}"
            )

    text = "\n".join(lines)
    return text if len(text) <= 4000 else text[:3999] + "…"


def format_event_items(events: List[EventItem], limit: int = 5) -> str:
    """
    HTML-форматирование списка EventItem для Telegram.
    Использует свойства модели: event_time_fmt, country/currency, title, importance, fact/forecast/previous.
    """
    if not events:
        return "⚠️ No upcoming events"

    lines: List[str] = ["📅 <b>Upcoming events</b>"]
    for i, ev in enumerate(events[:limit], start=1):
        when = ev.event_time_fmt or "—"
        country = escape(ev.country or "")
        currency = escape(ev.currency or "")
        title = escape(ev.title or "—")

        importance = int(ev.importance or 0)
        stars = "⭐" * max(1, min(3, importance))
        importance_text = "Low" if importance <= 1 else "Medium" if importance == 2 else "High"

        fact = escape(ev.fact or "—")
        forecast = escape(ev.forecast or "—")
        previous = escape(ev.previous or "—")

        lines.append(
            f"\n<b>{i}. {title}</b>\n"
            f"{when} · {country} {currency}\n"
            f"{stars} <b>Importance:</b> {importance_text}\n"
            f"📊 <b>Actual:</b> {fact} · <b>Forecast:</b> {forecast} · <b>Previous:</b> {previous}"
        )

    text = "\n".join(lines)
    return text if len(text) <= 4000 else text[:3999] + "…"
