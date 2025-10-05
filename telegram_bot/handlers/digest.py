import logging
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from services.async_digest_service import async_digest_service
from services.categories import get_categories
from utils.clean_text import clean_for_telegram
from models.news import NewsItem

router = Router()
logger = logging.getLogger(__name__)


def select_news_by_importance(news_list: list[NewsItem], limit: int) -> list[NewsItem]:
    """Выбирает limit новостей: важные → остальные → fallback."""
    important = [n for n in news_list if float(n.importance or 0) >= 0.4]
    other = [n for n in news_list if n not in important]

    selected = important[:limit]
    if len(selected) < limit:
        selected += other[: limit - len(selected)]
    if not selected and news_list:
        selected = news_list[:limit]  # fallback

    return selected


def categories_keyboard() -> types.InlineKeyboardMarkup:
    """Формируем inline-клавиатуру для выбора категории"""
    categories = get_categories()
    keyboard = [
        [types.InlineKeyboardButton(text=cat.title(), callback_data=f"digest:{cat}")]
        for cat in categories
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

    # ⚡️ используем асинхронный сервис дайджестов
    digest_text, news = await async_digest_service.build_daily_digest(
        limit=limit, style="analytical", categories=cats
    )

    # Используем готовый текст из сервиса, чтобы сохранить метрики важности/актуальности
    text = digest_text

    text = clean_for_telegram(text)
    markup = categories_keyboard()

    try:
        if isinstance(target, types.Message):
            await target.answer(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup,
            )
        else:
            # избегаем "message is not modified"
            if target.message.text and target.message.text.strip() == text.strip():
                await target.message.edit_reply_markup(reply_markup=markup)
            else:
                await target.message.edit_text(
                    text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=markup,
                )
            await target.answer(cache_time=0)
    except TelegramBadRequest as e:
        msg = str(e).lower()
        logger.warning("⚠️ Digest send failed: %s", e)
        if not isinstance(target, types.Message) and "message is not modified" in msg:
            try:
                await target.message.edit_reply_markup(reply_markup=markup)
                await target.answer(cache_time=0)
                return
            except Exception:
                pass
        if not isinstance(target, types.Message):
            await target.message.answer(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup,
            )
            await target.answer(cache_time=0)

    logger.info("✅ Digest sent: category=%s, count=%d", category, len(news))


@router.message(Command("digest"))
async def cmd_digest(message: types.Message):
    """Команда /digest → выводим общий поток."""
    await send_digest(message, limit=5, category="all")


@router.callback_query(F.data.startswith("digest:"))
async def cb_digest(query: types.CallbackQuery):
    """Кнопки категорий → всегда обновляют текущее сообщение."""
    category = query.data.split(":", 1)[1] if ":" in query.data else "all"
    await send_digest(query, limit=5, category=category)
