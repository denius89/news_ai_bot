from aiogram import types, Router, F
from aiogram.filters import Command

from database.db_models import get_latest_news
from telegram_bot.utils.formatters import format_news
from telegram_bot.keyboards import back_inline_keyboard

router = Router()


async def send_digest(
    target: types.Message | types.CallbackQuery,
    limit: int = 5,
):
    """Обычный дайджест: показывает только важные новости (importance >= 0.4)."""
    news = get_latest_news(limit=10)
    text = "⚠️ No fresh news" if not news else format_news(news, limit=limit, min_importance=0.4)

    if isinstance(target, types.Message):
        await target.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=back_inline_keyboard(),
        )
    else:  # callback query
        await target.message.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=back_inline_keyboard(),
        )
        await target.answer()


@router.message(Command("digest"))
async def cmd_digest(message: types.Message):
    await send_digest(message)


@router.callback_query(F.data == "digest")
async def cb_digest(query: types.CallbackQuery):
    await send_digest(query)
