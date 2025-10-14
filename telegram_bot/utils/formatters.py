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
    Список ближайших событий (HTML) с category-specific форматированием.

    Автоматически определяет категорию события и применяет
    соответствующий форматтер для красивого отображения.

    Args:
        events: Список событий (dict с полями category, subcategory, metadata)
        limit: Максимальное количество событий для отображения

    Returns:
        Отформатированная HTML-строка для Telegram
    """
    if not events:
        return "⚠️ Нет свежих событий"

    lines = ["📅 <b>Предстоящие события</b>"]

    for i, event in enumerate(events[:limit], start=1):
        category = event.get("category", "").lower()
        subcategory = event.get("subcategory", "").lower()

        # Category + subcategory routing
        if category == "sports":
            # Esports subcategories
            if subcategory in [
                "dota2",
                "csgo",
                "lol",
                "valorant",
                "pubg",
                "overwatch",
                "fifa_esports",
                "rocket_league",
                "starcraft",
                "esports_general",
            ]:
                text = format_event_esports(event)
            else:
                # Traditional sports
                text = format_event_sports(event)

        elif category == "crypto":
            text = format_event_crypto(event)

        elif category == "tech":
            text = format_event_tech(event)

        elif category == "markets":
            text = format_event_markets(event)

        elif category == "world":
            text = format_event_world(event)

        else:
            # Fallback для legacy событий или неизвестных категорий
            text = format_event_generic(event)

        lines.append(f"\n<b>{i}.</b> {text}")

    return _clamp_tg("\n".join(lines))


# -------- Category-specific event formatters --------


def format_event_sports(event: dict) -> str:
    """
    Форматирование традиционных спортивных событий.

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    metadata = event.get("metadata", {})
    subcategory = event.get("subcategory", "general")

    # Футбол
    if subcategory == "football":
        home = metadata.get("home_team", "")
        away = metadata.get("away_team", "")
        competition = metadata.get("competition", "")
        matchday = metadata.get("matchday", "")
        status = metadata.get("status", "Scheduled")

        title_text = f"{home} vs {away}" if home and away else event.get("title", "")
        comp_text = competition if competition else ""
        matchday_text = f" • Matchday {matchday}" if matchday else ""

        return (
            f"⚽ <b>{escape(title_text)}</b>\n"
            f"🏆 {escape(comp_text)}{matchday_text}\n"
            f"📅 {_fmt_dt(event.get('starts_at'))}\n"
            f"⚡ Status: {escape(status)}"
        )

    # Баскетбол
    elif subcategory == "basketball":
        home = metadata.get("home_team", "")
        away = metadata.get("away_team", "")
        league = metadata.get("league", metadata.get("competition", ""))

        title_text = f"{home} vs {away}" if home and away else event.get("title", "")

        return f"🏀 <b>{escape(title_text)}</b>\n" f"🏆 {escape(league)}\n" f"📅 {_fmt_dt(event.get('starts_at'))}"

    # Хоккей
    elif subcategory == "hockey":
        home = metadata.get("home_team", "")
        away = metadata.get("away_team", "")
        league = metadata.get("league", metadata.get("competition", ""))

        title_text = f"{home} vs {away}" if home and away else event.get("title", "")

        return f"🏒 <b>{escape(title_text)}</b>\n" f"🏆 {escape(league)}\n" f"📅 {_fmt_dt(event.get('starts_at'))}"

    # Общий формат для других видов спорта
    else:
        return (
            f"🏆 <b>{escape(event.get('title', ''))}</b>\n"
            f"📅 {_fmt_dt(event.get('starts_at'))}\n"
            f"📍 {escape(event.get('location', ''))}"
            if event.get("location")
            else ""
        )


def format_event_esports(event: dict) -> str:
    """
    Форматирование киберспортивных событий.

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    metadata = event.get("metadata", {})
    subcategory = event.get("subcategory", "esports_general")

    team1 = metadata.get("team1", metadata.get("home_team", ""))
    team2 = metadata.get("team2", metadata.get("away_team", ""))
    tournament = metadata.get("tournament", metadata.get("competition", ""))
    game = metadata.get("game", subcategory.upper())
    format_type = metadata.get("format", "BO3")

    # Game-specific icons
    game_icons = {
        "dota2": "🐉",
        "csgo": "🔫",
        "lol": "⚔️",
        "valorant": "🎯",
        "pubg": "🎮",
        "overwatch": "🎮",
        "starcraft": "🎮",
    }
    icon = game_icons.get(subcategory, "🎮")

    title_text = f"{team1} vs {team2}" if team1 and team2 else event.get("title", "")

    lines = [
        f"{icon} <b>{escape(title_text)}</b>",
        f"🏆 {escape(tournament)} ({escape(game)})",
        f"📅 {_fmt_dt(event.get('starts_at'))}",
    ]

    if format_type:
        lines.append(f"⚔️ Format: {escape(format_type)}")

    return "\n".join(lines)


def format_event_crypto(event: dict) -> str:
    """
    Форматирование криптовалютных событий.

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    metadata = event.get("metadata", {})
    subcategory = event.get("subcategory", "general")

    coins = metadata.get("coins", [])
    vote_count = metadata.get("vote_count", 0)
    categories = metadata.get("categories", [])
    proof = metadata.get("proof", "")

    # Subcategory icons
    subcategory_icons = {
        "mainnet": "🚀",
        "airdrop": "💸",
        "listing": "📈",
        "token_unlock": "🔓",
        "hard_fork": "⚡",
        "protocol_upgrade": "🔧",
        "dao": "🏛️",
        "nft": "🖼️",
        "defi": "🏦",
    }
    icon = subcategory_icons.get(subcategory, "🪙")

    lines = [
        f"{icon} <b>{escape(event.get('title', ''))}</b>",
        f"📅 {_fmt_dt(event.get('starts_at'))}",
    ]

    if coins:
        coins_text = ", ".join(coins[:3])
        if len(coins) > 3:
            coins_text += f" +{len(coins) - 3} more"
        lines.append(f"💰 Coins: {escape(coins_text)}")

    if vote_count > 0:
        lines.append(f"👥 Votes: {vote_count:,}")

    if categories:
        cats_text = ", ".join(categories[:3])
        lines.append(f"🏷️ {escape(cats_text)}")

    if proof:
        lines.append(f'🔗 <a href="{escape(proof)}">Proof</a>')

    return "\n".join(lines)


def format_event_markets(event: dict) -> str:
    """
    Форматирование рыночных/экономических событий.

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    metadata = event.get("metadata", {})

    country = event.get("location", "")
    country_code = metadata.get("country_code", "")
    fact = metadata.get("fact", event.get("fact", "—"))
    forecast = metadata.get("forecast", event.get("forecast", "—"))
    previous = metadata.get("previous", event.get("previous", "—"))

    # Country flag
    flag = country_flag(country_code) if country_code else ""

    lines = [
        f"📈 <b>{escape(event.get('title', ''))}</b>",
    ]

    if flag and country:
        lines.append(f"{flag} {escape(country)}")
    elif country:
        lines.append(f"🌍 {escape(country)}")

    lines.append(f"📅 {_fmt_dt(event.get('starts_at'))}")

    # Metrics (только если не "—")
    if fact != "—" or forecast != "—" or previous != "—":
        lines.append(
            f"📊 Факт: {escape(str(fact))} · " f"Прогноз: {escape(str(forecast))} · " f"Пред.: {escape(str(previous))}"
        )

    return "\n".join(lines)


def format_event_tech(event: dict) -> str:
    """
    Форматирование технологических событий.

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    metadata = event.get("metadata", {})
    subcategory = event.get("subcategory", "general")

    # Software releases
    if subcategory == "software_release":
        version = metadata.get("version", "")
        project = metadata.get("project", "")
        link = event.get("link", "")

        title_text = event.get("title", "")
        if project and version:
            project_text = f"{project} v{version}"
        elif project:
            project_text = project
        else:
            project_text = ""

        lines = [
            f"💻 <b>{escape(title_text)}</b>",
        ]

        if project_text:
            lines.append(f"📦 {escape(project_text)}")

        lines.append(f"📅 {_fmt_dt(event.get('starts_at'))}")

        if link:
            lines.append(f'🔗 <a href="{escape(link)}">Link</a>')

        return "\n".join(lines)

    # Conferences
    elif subcategory == "conference":
        location = event.get("location", "")
        organizer = event.get("organizer", "")

        lines = [
            f"🎤 <b>{escape(event.get('title', ''))}</b>",
        ]

        if location:
            lines.append(f"📍 {escape(location)}")

        lines.append(f"📅 {_fmt_dt(event.get('starts_at'))}")

        if organizer:
            lines.append(f"🏛️ {escape(organizer)}")

        return "\n".join(lines)

    # General tech events
    else:
        lines = [
            f"💻 <b>{escape(event.get('title', ''))}</b>",
            f"📅 {_fmt_dt(event.get('starts_at'))}",
        ]

        if event.get("description"):
            desc = _short(event.get("description", ""), 150)
            lines.append(f"📝 {escape(desc)}")

        return "\n".join(lines)


def format_event_world(event: dict) -> str:
    """
    Форматирование мировых событий (политика, климат, ООН).

    Args:
        event: Event dictionary с metadata

    Returns:
        Formatted event string для Telegram
    """
    location = event.get("location", "")
    organizer = event.get("organizer", "")

    lines = [
        f"🌍 <b>{escape(event.get('title', ''))}</b>",
    ]

    if location:
        lines.append(f"📍 {escape(location)}")

    lines.append(f"📅 {_fmt_dt(event.get('starts_at'))}")

    if organizer:
        lines.append(f"🏛️ {escape(organizer)}")

    if event.get("description"):
        desc = _short(event.get("description", ""), 150)
        lines.append(f"📋 {escape(desc)}")

    return "\n".join(lines)


def format_event_generic(event: dict) -> str:
    """
    Общий форматтер для событий без специфической категории.

    Args:
        event: Event dictionary

    Returns:
        Formatted event string для Telegram
    """
    lines = [
        f"📅 <b>{escape(event.get('title', ''))}</b>",
        f"🕐 {_fmt_dt(event.get('starts_at'))}",
    ]

    if event.get("location"):
        lines.append(f"📍 {escape(event.get('location', ''))}")

    return "\n".join(lines)


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
