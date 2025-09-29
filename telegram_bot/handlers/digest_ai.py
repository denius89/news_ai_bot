# telegram_bot/handlers/digest_ai.py
from datetime import datetime, time, timezone
import pytz
import logging

from aiogram import types, Router, F
from aiogram.filters import Command

from database.db_models import supabase
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


# ---------- Общая логика ----------
def build_digest_ai_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура выбора категории"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=label, callback_data=f"digest_ai:{cat}")]
            for cat, label in CATEGORIES.items()
        ]
        + [
            [types.InlineKeyboardButton(text="📚 Все категории", callback_data="digest_ai:all")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )


async def show_digest_ai_menu(target: types.Message | types.CallbackQuery):
    """Универсальный показ меню выбора категорий"""
    kb = build_digest_ai_keyboard()
    text = "📌 Выберите категорию для AI-дайджеста:"

    if isinstance(target, types.Message):
        await target.answer(text, reply_markup=kb)
    elif isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb)
        await target.answer()  # важно: без reply_markup!


# ---------- Хэндлеры ----------
@router.message(Command(commands=["digest_ai"], ignore_case=True))
async def cmd_digest_ai(message: types.Message):
    """Вызов через /digest_ai"""
    logger.info("🚀 /digest_ai → показать меню категорий")
    await show_digest_ai_menu(message)


@router.callback_query(F.data == "digest_ai")
async def cb_digest_ai_menu_root(query: types.CallbackQuery):
    """Вызов через кнопку в главном меню"""
    await show_digest_ai_menu(query)


@router.callback_query(F.data == "back")
async def cb_digest_ai_menu_back(query: types.CallbackQuery):
    """Возврат в меню категорий"""
    await show_digest_ai_menu(query)


@router.callback_query(F.data.startswith("digest_ai:"))
async def cb_digest_ai(query: types.CallbackQuery):
    """Формирование AI-дайджеста по выбранной категории"""
    # ⚡ быстрый ответ → чтобы Telegram не дал timeout
    await query.answer("⏳ Формирую дайджест...")

    raw_category = query.data.split(":", 1)[1]
    logger.info(f"➡️ Выбрана категория: {raw_category}")
    category = None if raw_category == "all" else raw_category

    try:
        # Берем побольше из БД (10), чтобы ИИ было что анализировать
        text = generate_digest(limit=10, ai=True, category=category)

        if not text or text.strip() == "":
            await query.message.edit_text("📭 Сегодня нет новостей по выбранной категории.")
            return

        # 🚨 Telegram ограничение — 4096 символов → режем на куски
        chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
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


# (Опционально — можно оставить для будущей фильтрации по дате)
def fetch_today_news(category: str | None = None, limit: int = 30) -> list[dict]:
    """Достаём все новости за текущий день (с опциональной категорией)."""
    now_local = datetime.now(LOCAL_TZ)
    today_start = LOCAL_TZ.localize(datetime.combine(now_local.date(), time.min)).astimezone(
        timezone.utc
    )
    today_end = LOCAL_TZ.localize(datetime.combine(now_local.date(), time.max)).astimezone(
        timezone.utc
    )

    query = (
        supabase.table("news")
        .select("title, content, link, published_at, source, category")
        .gte("published_at", today_start.isoformat())
        .lte("published_at", today_end.isoformat())
        .order("published_at", desc=True)
        .limit(limit)
    )

    if category:
        query = query.eq("category", category)

    res = query.execute()
    return res.data or []
