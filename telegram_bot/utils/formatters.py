# telegram_bot/utils/formatters.py
from __future__ import annotations
from datetime import datetime
from html import escape

MAX_TG_LEN = 4000  # безопасная длина для Telegram (реальный лимит 4096)


def _clamp_tg(text: str, max_len: int = MAX_TG_LEN) -> str:
    """Обрезает текст до безопасной длины для Telegram, добавляя многоточие."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _fmt_dt(iso: str | None) -> str:
    """Красиво форматирует ISO-datetime → 'DD Mon YYYY, HH:MM' или '—'."""
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return iso


def _metric_icons(cred: float, imp: float) -> tuple[str, str]:
    """Эмодзи для метрик (credibility, importance)."""
    cred_icon = "✅" if cred > 0.7 else "⚠️" if cred > 0.4 else "❌"
    imp_icon = "🔥" if imp > 0.7 else "⚡" if imp > 0.4 else "💤"
    return cred_icon, imp_icon


def _short(text: str, n: int = 220) -> str:
    """Короткое описание (для сниппета)."""
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def country_flag(code: str | None) -> str:
    """Преобразует ISO-код страны в эмодзи-флаг."""
    if not code:
        return ""
    code = code.upper()
    if code == "EU":
        return "🇪🇺"
    try:
        return "".join(chr(127397 + ord(c)) for c in code)
    except Exception:
        return code


# -------- новости --------


def format_news(news: list[dict], limit: int = 5, min_importance: float = 0.4) -> str:
    if not news:
        return "⚠️ No fresh news"

    filtered = [n for n in news if float(n.get("importance") or 0) >= float(min_importance)]
    if not filtered:
        return "⚠️ No important news today"

    lines = ["📰 <b>Top news</b>"]
    for i, item in enumerate(filtered[:limit], start=1):
        title_raw = (item.get("title") or item.get("source") or "Untitled").strip()
        title = escape(title_raw)
        link = item.get("link") or ""
        source = escape(item.get("source") or "—")
        published = _fmt_dt(item.get("published_at"))

        cred = float(item.get("credibility") or 0.0)
        imp = float(item.get("importance") or 0.0)
        cred_icon, imp_icon = _metric_icons(cred, imp)

        summary = _short(item.get("content") or item.get("summary") or "", 260)
        summary = escape(summary)

        title_line = f'<b>{i}. <a href="{escape(link)}">{title}</a></b>'

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

    return _clamp_tg("\n".join(lines))


# -------- события --------


def format_events(events: list[dict], limit: int = 5) -> str:
    """
    Список ближайших событий (HTML).
    - время, страна/валюта, заголовок
    - важность (звёзды + текст)
    - факт/прогноз/предыдущее
    """
    if not events:
        return "⚠️ No upcoming events"

    lines = ["📅 <b>Upcoming events</b>"]
    for i, ev in enumerate(events[:limit], start=1):
        # дата/время
        when = _fmt_dt(ev.get("event_time"))
        # страна/валюта
        flag = country_flag(ev.get("country_code"))
        currency = escape(ev.get("currency") or "")
        country = escape(ev.get("country") or "")
        # заголовок
        title = escape(ev.get("title") or "—")

        # важность
        importance = int(ev.get("importance") or 0)
        stars = "⭐" * max(1, min(3, importance))
        importance_text = "Low" if importance <= 1 else "Medium" if importance == 2 else "High"

        # метрики
        fact = escape(ev.get("fact") or "—")
        forecast = escape(ev.get("forecast") or "—")
        previous = escape(ev.get("previous") or "—")

        lines.append(
            f"\n<b>{i}. {title}</b>\n"
            f"{when} · {flag} {country} {currency}\n"
            f"{stars} <b>Importance:</b> {importance_text}\n"
            f"📊 <b>Actual:</b> {fact} · <b>Forecast:</b> {forecast} · <b>Previous:</b> {previous}"
        )

    return _clamp_tg("\n".join(lines))


# -------- AI-дайджест --------


def format_digest_ai(summary: str, news: list[dict] | None = None, limit: int = 5) -> str:
    """
    Текст AI-дайджеста + короткий список ссылок.
    """
    if not summary:
        return "📭 No AI summary"

    lines = ["🤖 <b>AI digest</b>", "", escape(summary.strip())]

    if news:
        lines.append("")
        lines.append("🔗 <b>Links:</b>")
        for i, item in enumerate(news[:limit], start=1):
            title_raw = (item.get("title") or item.get("source") or "Untitled").strip()
            title = escape(title_raw)
            link = escape(item.get("link") or "")
            lines.append(f'{i}. <a href="{link}">{title}</a>')

    return _clamp_tg("\n".join(lines))
