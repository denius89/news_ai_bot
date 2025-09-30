import logging
from aiogram import types, Router, F
from aiogram.filters import Command

from services.digest_service import build_daily_digest
from telegram_bot.utils.formatters import format_news
from digests.configs import CATEGORIES
from utils.clean_text import clean_for_telegram  # ✅ чтобы Telegram не падал

router = Router()
logger = logging.getLogger(__name__)


def select_news_by_importance(news_list, limit):
    """Выбирает limit новостей: важные → остальные → fallback."""
    important = [n for n in news_list if (n.get("importance") or 0) >= 0.4]
    other = [n for n in news_list if n not in important]

    selected = important[:limit]
    if len(selected) < limit:
        selected += other[: limit - len(selected)]
    if not selected and news_list:
        selected = news_list[:limit]  # fallback

    return selected


def categories_keyboard():
    """Формируем inline-клавиатуру для выбора категории"""
    keyboard = [
        [types.InlineKeyboardButton(text=label, callback_data=f"digest:{key}")]
        for key, label in CATEGORIES.items()
    ]
    keyboard.append(
        [types.InlineKeyboardButton(text="🌐 Все категории", callback_data="digest:all")]
    )
    keyboard.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


async def send_digest(
    target: types.Message | types.CallbackQuery,
    limit: int = 5,
    category: str | None = None,
):
    """Формирует дайджест для выбранной категории (или общего потока)."""
    cats = None if (category is None or category == "all") else [category]
    _, news = build_daily_digest(limit=50, categories=cats)  # digest_text не используем

    if not news:
        text = (
            f"📭 Нет свежих новостей в категории «{CATEGORIES.get(category, category)}»"
            if category and category != "all"
            else "📭 Нет свежих новостей"
        )
    else:
        selected = select_news_by_importance(news, limit)
        header = ""
        if category and category != "all":
            header = f"<b>{CATEGORIES.get(category, category)}:</b>\n\n"
        text = header + format_news(selected, limit=limit, min_importance=0.0)

    text = clean_for_telegram(text)  # ✅ защита от кривой разметки
    markup = categories_keyboard()

    if isinstance(target, types.Message):
        await target.answer(
            text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup
        )
    else:
        await target.message.edit_text(
            text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup
        )
        await target.answer()

    logger.info("✅ Digest sent: category=%s, count=%d", category, len(news))


@router.message(Command("digest"))
async def cmd_digest(message: types.Message):
    await send_digest(message, limit=5, category="all")


@router.callback_query(F.data.startswith("digest:"))
async def cb_digest(query: types.CallbackQuery):
    category = query.data.split(":", 1)[1] if ":" in query.data else "all"
    await send_digest(query, category=category)
