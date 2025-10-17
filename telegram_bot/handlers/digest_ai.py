import logging
import pytz
from aiogram import types, Router, F
from aiogram.filters import Command
from services.unified_digest_service import get_async_digest_service
from telegram_bot.keyboards import back_inline_keyboard
from services.categories import get_categories
from services.subscription_service import get_async_subscription_service
from services.notification_service import get_notification_service
from digests.configs import PERIODS, STYLES
from utils.text.clean_text import clean_for_telegram
from utils.system.progress_animation import (
    show_generation_progress,
    show_quick_progress,
    build_digest_actions_keyboard,
)

router = Router()
logger = logging.getLogger("digest_ai")

LOCAL_TZ = pytz.timezone("Europe/Kyiv")


def build_category_keyboard() -> types.InlineKeyboardMarkup:
    from services.categories import get_emoji_icon

    categories = get_categories()
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"{get_emoji_icon(cat, '')} {cat.title()}",
                    callback_data=f"digest_ai_category:{cat}",
                )
            ]
            for cat in categories
        ]
        + [[types.InlineKeyboardButton(text="📚 Все категории", callback_data="digest_ai_category:all")]]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )


def build_period_keyboard(category: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=label, callback_data=f"digest_ai_period:{period}:{category}")]
            for period, label in PERIODS.items()
        ]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="digest_ai")]]
    )


def build_style_keyboard(category: str, period: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=label, callback_data=f"digest_ai_style:{style}:{category}:{period}")]
            for style, label in STYLES.items()
        ]
        + [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"digest_ai_period:{period}:{category}")]]
    )


async def show_digest_ai_menu(target: types.Message | types.CallbackQuery):
    kb = build_category_keyboard()
    text = (
        "🤖 <b>AI-дайджест</b>\n\n"
        "Персональный дайджест, созданный специально для вас!\n\n"
        "✨ <b>Что внутри:</b>\n"
        "• Анализ 255 источников новостей\n"
        "• ML-фильтрация по важности и достоверности\n"
        "• 4 профессиональных стиля на выбор\n"
        "• Адаптация под ваши интересы\n\n"
        "📌 <b>Выберите категорию:</b>"
    )
    if isinstance(target, types.Message):
        await target.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        await target.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
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

    category_display = "Все категории" if raw_category == "all" else raw_category.title()
    text = (
        f"📚 <b>AI-дайджест: {category_display}</b>\n\n"
        "⏱️ <b>Выберите период:</b>\n"
        "• <i>Сегодня</i> — новости за последние 24 часа\n"
        "• <i>За неделю</i> — главное за 7 дней\n"
        "• <i>За месяц</i> — ключевые события месяца"
    )
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await query.answer()


# First definition removed - using the more complete one below


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

    # Используем стиль, выбранный пользователем в клавиатуре

    logger.info(f"➡️ Генерация: category={category}, period={period}, style={style}")

    # Show immediate feedback
    await show_quick_progress(query, "⏳ Генерация дайджеста для тебя...")

    try:
        # Start animated progress
        animation = await show_generation_progress(query)

        # Generate AI digest using async service
        categories_list = None if category == "all" else [category]
        digest_service = get_async_digest_service()
        text = await digest_service.async_build_ai_digest(limit=20, categories=categories_list, style=style)

        # Stop animation
        animation.stop()

        # Проверяем тип результата
        if hasattr(text, "__await__"):
            logger.error(f"Got coroutine instead of string: {type(text)}")
            text = "❌ Ошибка: получена корутина вместо строки"
        else:
            text = clean_for_telegram(text)

        if not text.strip():
            await query.message.edit_text(
                "📭 Нет новостей по выбранной категории/периоду.",
                reply_markup=back_inline_keyboard(),
            )
            return

        # Build personalized header
        username = query.from_user.username or query.from_user.first_name or "друг"
        header = f"📰 Дайджест дня для @{username}"
        if category and category != "all":
            # Просто используем название категории как есть
            header += f" • {category.title()}"

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
                f"⚠️ Ошибка при генерации AI-дайджеста: {e}", reply_markup=back_inline_keyboard()
            )
        except Exception:
            # Message might be too old to edit, try sending a new one
            try:
                await query.message.answer(
                    f"⚠️ Ошибка при генерации AI-дайджеста: {e}", reply_markup=back_inline_keyboard()
                )
            except Exception:
                # If all else fails, just log the error
                logger.error("Failed to send error message to user")


@router.callback_query(F.data.startswith("subscribe_category:"))
async def cb_subscribe_category(query: types.CallbackQuery):
    """Handle subscription to category from digest actions."""
    try:
        category = query.data.split(":", 1)[1]
        category_name = get_categories().get(category, {}).get("name", category)

        # Subscribe user to category
        user_id = query.from_user.id
        subscription_service = get_async_subscription_service()
        success = await subscription_service.subscribe_to_category(user_id, category)

        if success:
            await query.answer(f"✅ Подписка на {category_name} активирована!", show_alert=True)
        else:
            await query.answer("❌ Ошибка при активации подписки", show_alert=True)

        # Update message to show subscription success
        await query.message.edit_reply_markup(
            reply_markup=build_digest_actions_keyboard(query.from_user.username or "пользователь", category)
        )

    except Exception as e:
        logger.error(f"Error in subscribe category: {e}")
        await query.answer("❌ Ошибка при подписке", show_alert=True)


@router.callback_query(F.data == "enable_auto_digest")
async def cb_enable_auto_digest(query: types.CallbackQuery):
    """Handle enabling auto-digest notifications."""
    try:
        # Enable auto-digest notifications
        user_id = query.from_user.id
        notification_service = get_notification_service()
        success = await notification_service.enable_auto_digest(user_id, enabled=True)

        if success:
            await query.answer(
                "✅ Авто-дайджест включен! Буду присылать дайджесты каждый день в 9:00",
                show_alert=True,
            )
        else:
            await query.answer("❌ Ошибка при включении авто-дайджеста", show_alert=True)

    except Exception as e:
        logger.error(f"Error in enable auto digest: {e}")
        await query.answer("❌ Ошибка при включении авто-дайджеста", show_alert=True)


@router.callback_query(F.data.startswith("digest_ai_period:"))
async def cb_digest_ai_period(query: types.CallbackQuery):
    """Обработчик выбора периода для AI дайджеста"""
    try:
        # Формат: digest_ai_period:period:category
        parts = query.data.split(":", 2)
        if len(parts) >= 3:
            period = parts[1]
            category = parts[2]

            # Показываем выбор стиля
            kb = build_style_keyboard(category, period)

            category_display = "Все категории" if category == "all" else category.title()
            period_display = PERIODS.get(period, period)

            text = (
                f"📚 <b>AI-дайджест: {category_display}</b>\n"
                f"⏱️ Период: <i>{period_display}</i>\n\n"
                "✍️ <b>Выберите стиль подачи:</b>\n\n"
                "📰 <b>Newsroom</b> — как Reuters/Bloomberg\n"
                "   Факты, цифры, без эмоций. Для быстрого чтения.\n\n"
                "🔍 <b>Analytical</b> — глубокий анализ\n"
                "   Причинно-следственные связи, контекст, инсайты.\n\n"
                "📖 <b>Magazine</b> — storytelling\n"
                "   Захватывающая подача, метафоры, вовлечение.\n\n"
                "💬 <b>Casual</b> — разговорный стиль\n"
                "   Простым языком, как разговор с другом."
            )
            await query.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            await query.answer()
        else:
            await query.answer("❌ Неверный формат данных")

    except Exception as e:
        logger.error(f"Error in digest_ai_period: {e}")
        await query.answer("❌ Ошибка при выборе периода")
