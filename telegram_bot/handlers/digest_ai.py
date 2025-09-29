# telegram_bot/handlers/digest_ai.py
import logging
from datetime import datetime, time, timedelta, timezone
from typing import Optional

import pytz
from aiogram import types, Router, F
from aiogram.filters import Command

from digests.generator import generate_digest
from telegram_bot.keyboards import back_inline_keyboard

router = Router()
logger = logging.getLogger("digest_ai")

# ⚙️ Локальная таймзона
LOCAL_TZ = pytz.timezone("Europe/Kyiv")

# Категории с эмодзи
CATEGORIES = {
    "crypto": "📊 Crypto",
    "economy": "💰 Economy",
    "world": "🌍 World",
    "technology": "⚙️ Technology",
    "politics": "🏛️ Politics",
}


# ---------- Клавиатуры ----------
def build_category_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура выбора категории"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=label, callback_data=f"digest_ai_category:{cat}")]
            for cat, label in CATEGORIES.items()
        ]
        + [[types.InlineKeyboardButton(text="📚 Все категории", callback_data="digest_ai_category:all")]]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )


def build_period_keyboard(category: str) -> types.InlineKeyboardMarkup:
    """Клавиатура выбора периода для выбранной категории"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📅 Сегодня", callback_data=f"digest_ai_period:today:{category}")],
            [types.InlineKeyboardButton(text="📅 Последние 7 дней", callback_data=f"digest_ai_period:7d:{category}")],
            [types.InlineKeyboardButton(text="📅 Последние 30 дней", callback_data=f"digest_ai_period:30d:{category}")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="digest_ai")],
        ]
    )


async def show_digest_ai_menu(target: types.Message | types.CallbackQuery):
    """Показ меню выбора категорий"""
    kb = build_category_keyboard()
    text = "📌 Выберите категорию для AI-дайджеста:"

    if isinstance(target, types.Message):
        await target.answer(text, reply_markup=kb)
    elif isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb)
        await target.answer()


# ---------- Хэндлеры ----------
@router.message(Command(commands=["digest_ai"], ignore_case=True))
async def cmd_digest_ai(message: types.Message):
    """Вызов через /digest_ai"""
    logger.info("🚀 /digest_ai → показать меню категорий")
    await show_digest_ai_menu(message)


@router.callback_query(F.data == "digest_ai")
async def cb_digest_ai_menu_root(query: types.CallbackQuery):
    """Возврат в меню категорий"""
    await show_digest_ai_menu(query)


@router.callback_query(F.data == "back")
async def cb_digest_ai_menu_back(query: types.CallbackQuery):
    """Возврат в меню категорий"""
    await show_digest_ai_menu(query)


@router.callback_query(F.data.startswith("digest_ai_category:"))
async def cb_digest_ai_category(query: types.CallbackQuery):
    """Переход к выбору периода"""
    raw_category = query.data.split(":", 1)[1]
    category = None if raw_category == "all" else raw_category
    logger.info(f"➡️ Выбрана категория: {category}")

    kb = build_period_keyboard(raw_category)
    await query.message.edit_text("📌 Категория выбрана. Теперь укажите период:", reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("digest_ai_period:"))
async def cb_digest_ai_period(query: types.CallbackQuery):
    """Формирование AI-дайджеста по категории и периоду"""
    await query.answer("⏳ Формирую дайджест...")

    _, period, raw_category = query.data.split(":")
    category = None if raw_category == "all" else raw_category
    logger.info(f"➡️ Категория: {category}, период: {period}")

    now = datetime.now(timezone.utc)
    start, end = None, None

    if period == "today":
        start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        end = datetime.combine(now.date(), time.max, tzinfo=timezone.utc)
    elif period == "7d":
        start = now - timedelta(days=7)
        end = now
    elif period == "30d":
        start = now - timedelta(days=30)
        end = now

    try:
        # генерируем дайджест с диапазоном дат
        text = generate_digest(ai=True, category=category, limit=30, start=start, end=end)

        if not text or text.strip() == "":
            await query.message.edit_text("📭 Нет новостей по выбранной категории/периоду.")
            return

        # 🚨 Telegram ограничение — 4096 символов → режем на куски
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                await query.message.edit_text(
                    chunk,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=back_inline_keyboard(),
                )
            else:
                await query.message.answer(
                    chunk,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

    except Exception as e:
        logger.error(f"Ошибка генерации AI-дайджеста: {e}", exc_info=True)
        await query.message.edit_text(f"⚠️ Ошибка при генерации AI-дайджеста: {e}")
