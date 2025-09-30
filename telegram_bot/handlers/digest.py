import logging
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from services.digest_service import build_daily_digest
from telegram_bot.utils.formatters import format_news
from digests.configs import CATEGORIES
from utils.clean_text import clean_for_telegram  # ✅ защита от кривой разметки

router = Router()
logger = logging.getLogger(__name__)


def select_news_by_importance(news_list, limit: int):
    """Выбирает limit новостей: важные → остальные → fallback."""
    important = [n for n in news_list if (n.get("importance") or 0) >= 0.4]
    other = [n for n in news_list if n not in important]

    selected = important[:limit]
    if len(selected) < limit:
        selected += other[: limit - len(selected)]
    if not selected and news_list:
        selected = news_list[:limit]  # fallback

    return selected


def categories_keyboard() -> types.InlineKeyboardMarkup:
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
    _, news = build_daily_digest(limit=50, categories=cats)

    if not news:
        text = (
            f"📭 Нет свежих новостей в категории «{CATEGORIES.get(category, category)}»"
            if category and category != "all"
            else "📭 Нет свежих новостей"
        )
    else:
        selected = select_news_by_importance(news, limit)
        header = (
            f"<b>{CATEGORIES.get(category, category)}:</b>\n\n"
            if category and category != "all"
            else ""
        )
        text = header + format_news(selected, limit=limit, min_importance=0.0)

    text = clean_for_telegram(text)
    markup = categories_keyboard()

    try:
        if isinstance(target, types.Message):
            # /digest → всегда новое сообщение
            await target.answer(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup,
            )
        else:
            # callback → всегда редактируем старое сообщение
            await target.message.edit_text(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup,
            )
            await target.answer()
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.info("ℹ️ Digest not modified, skip update")
        else:
            logger.warning("⚠️ Digest send failed (%s), fallback → новое сообщение", e)
            if not isinstance(target, types.Message):
                await target.message.answer(
                    text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=markup,
                )

    logger.info("✅ Digest sent: category=%s, count=%d", category, len(news))


# --- Хэндлеры ---
@router.message(Command("digest"))
async def cmd_digest(message: types.Message):
    """Команда /digest → выводим общий поток."""
    await send_digest(message, limit=5, category="all")


@router.callback_query(F.data.startswith("digest:"))
async def cb_digest(query: types.CallbackQuery):
    """Кнопки категорий → всегда обновляют текущее сообщение."""
    category = query.data.split(":", 1)[1] if ":" in query.data else "all"
    await send_digest(query, category=category)
