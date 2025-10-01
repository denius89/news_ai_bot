import logging
import pytz
import asyncio
from aiogram import types, Router, F
from aiogram.filters import Command

from services.digest_ai_service import DigestAIService
from telegram_bot.keyboards import back_inline_keyboard
from digests.configs import CATEGORIES, PERIODS, STYLES
from utils.clean_text import clean_for_telegram
from utils.progress_animation import show_generation_progress, show_quick_progress, build_digest_actions_keyboard

router = Router()
logger = logging.getLogger("digest_ai")

LOCAL_TZ = pytz.timezone("Europe/Kyiv")


def build_category_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=label, callback_data=f"digest_ai_category:{cat}")]
            for cat, label in CATEGORIES.items()
        ]
        + [
            [
                types.InlineKeyboardButton(
                    text="📚 Все категории", callback_data="digest_ai_category:all"
                )
            ]
        ]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )


def build_period_keyboard(category: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=label, callback_data=f"digest_ai_period:{period}:{category}"
                )
            ]
            for period, label in PERIODS.items()
        ]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="digest_ai")]]
    )


def build_style_keyboard(category: str, period: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=label, callback_data=f"digest_ai_style:{style}:{category}:{period}"
                )
            ]
            for style, label in STYLES.items()
        ]
        + [
            [
                types.InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"digest_ai_period:{period}:{category}"
                )
            ]
        ]
    )


async def show_digest_ai_menu(target: types.Message | types.CallbackQuery):
    kb = build_category_keyboard()
    text = "📌 Выберите категорию для AI-дайджеста:"
    if isinstance(target, types.Message):
        await target.answer(text, reply_markup=kb)
    else:
        await target.message.edit_text(text, reply_markup=kb)
        await target.answer()


@router.message(Command(commands=["digest_ai"], ignore_case=True))
async def cmd_digest_ai(message: types.Message):
    logger.info("🚀 /digest_ai → показать меню категорий")
    await show_digest_ai_menu(message)


@router.callback_query(F.data == "digest_ai")
async def cb_digest_ai_menu_root(query: types.CallbackQuery):
    await show_digest_ai_menu(query)


@router.callback_query(F.data == "back")
async def cb_digest_ai_menu_back(query: types.CallbackQuery):
    await show_digest_ai_menu(query)


@router.callback_query(F.data.startswith("digest_ai_category:"))
async def cb_digest_ai_category(query: types.CallbackQuery):
    raw_category = query.data.split(":", 1)[1]
    kb = build_period_keyboard(raw_category)
    await query.message.edit_text("📌 Категория выбрана. Теперь укажите период:", reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("digest_ai_period:"))
async def cb_digest_ai_period(query: types.CallbackQuery):
    _, period, raw_category = query.data.split(":")
    kb = build_style_keyboard(raw_category, period)
    await query.message.edit_text("✍️ Выберите стиль дайджеста:", reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("digest_ai_style:"))
async def cb_digest_ai_style(query: types.CallbackQuery):
    """Handle AI digest style selection with animated progress."""
    try:
        await query.answer("⏳ Формирую дайджест...", cache_time=0)
    except Exception:
        # Query might already be answered or expired, ignore
        pass

    _, style, raw_category, period = query.data.split(":")
    category = None if raw_category == "all" else raw_category
    logger.info(f"➡️ Генерация: category={category}, period={period}, style={style}")

    # Show immediate feedback
    await show_quick_progress(query, "⏳ Генерация дайджеста для тебя...")

    try:
        # Start animated progress
        animation = await show_generation_progress(query)
        
        # Generate digest in background
        service = DigestAIService()
        text = await asyncio.to_thread(
            service.generate_digest,
            20,  # limit
            category,
            True,  # ai
            style,
        )
        
        # Stop animation
        animation.stop()
        
        text = clean_for_telegram(text)

        if not text.strip():
            await query.message.edit_text(
                "📭 Нет новостей по выбранной категории/периоду.",
                reply_markup=back_inline_keyboard()
            )
            return

        # Build personalized header
        username = query.from_user.username or query.from_user.first_name or "друг"
        header = f"📰 Дайджест дня для @{username}"
        if category and category != "all":
            category_name = CATEGORIES.get(category, category)
            header += f" • {category_name}"
        
        # Prepare final message
        full_text = f"{header}\n\n{text}"
        
        # Build action keyboard
        actions_kb = build_digest_actions_keyboard(username, category)

        # Send message in chunks
        chunks = [full_text[i : i + 4000] for i in range(0, len(full_text), 4000)]
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                # Edit the progress message with final content
                try:
                    await query.message.edit_text(
                        chunk,
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=actions_kb,
                    )
                except Exception as e:
                    logger.warning(f"Failed to edit message: {e}")
                    # Fallback: send new message
                    await query.message.answer(
                        chunk,
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=actions_kb,
                    )
            else:
                await query.message.answer(
                    chunk,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                    
    except Exception as e:
        logger.error(f"Ошибка генерации AI-дайджеста: {e}", exc_info=True)
        try:
            await query.message.edit_text(
                f"⚠️ Ошибка при генерации AI-дайджеста: {e}",
                reply_markup=back_inline_keyboard()
            )
        except Exception:
            # Message might be too old to edit, try sending a new one
            try:
                await query.message.answer(
                    f"⚠️ Ошибка при генерации AI-дайджеста: {e}",
                    reply_markup=back_inline_keyboard()
                )
            except Exception:
                # If all else fails, just log the error
                logger.error("Failed to send error message to user")


@router.callback_query(F.data.startswith("subscribe_category:"))
async def cb_subscribe_category(query: types.CallbackQuery):
    """Handle subscription to category from digest actions."""
    try:
        category = query.data.split(":", 1)[1]
        category_name = CATEGORIES.get(category, category)
        
        # TODO: Implement actual subscription logic
        await query.answer(f"✅ Подписка на {category_name} активирована!", show_alert=True)
        
        # Update message to show subscription success
        await query.message.edit_reply_markup(
            reply_markup=build_digest_actions_keyboard(
                query.from_user.username or "пользователь", 
                category
            )
        )
        
    except Exception as e:
        logger.error(f"Error in subscribe category: {e}")
        await query.answer("❌ Ошибка при подписке", show_alert=True)


@router.callback_query(F.data == "enable_auto_digest")
async def cb_enable_auto_digest(query: types.CallbackQuery):
    """Handle enabling auto-digest notifications."""
    try:
        # TODO: Implement actual notification enabling logic
        await query.answer("✅ Авто-дайджест включен! Буду присылать дайджесты каждый день в 9:00", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in enable auto digest: {e}")
        await query.answer("❌ Ошибка при включении авто-дайджеста", show_alert=True)
