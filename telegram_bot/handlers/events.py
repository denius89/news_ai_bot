from aiogram import types, Router, F
from aiogram.filters import Command

from telegram_bot.utils.formatters import format_events
from telegram_bot.keyboards import back_inline_keyboard

router = Router()


async def send_events(
    target: types.Message | types.CallbackQuery,
    limit: int = 5,
    min_importance: float = 0.5,
):
    """Отправка ближайших событий из базы (новая таблица events_new с metadata)."""
    from database.db_models import supabase
    from datetime import datetime, timezone, timedelta

    if not supabase:
        text = (
            "⚠️ <b>База данных недоступна</b>\n\n"
            "Не удается подключиться к базе данных событий.\n"
            "Попробуйте позже или обратитесь к администратору."
        )
    else:
        # Читаем из events_new (с metadata!)
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)

        result = (
            supabase.table("events_new")
            .select("*")
            .gte("starts_at", now.isoformat())
            .lte("starts_at", future.isoformat())
            .order("starts_at")
            .limit(limit * 2)  # Берем больше для фильтрации
            .execute()
        )

        events = result.data or []

        if not events:
            text = (
                "📅 <b>Календарь событий</b>\n\n"
                "⚠️ Пока нет запланированных событий на ближайший месяц.\n\n"
                "✨ <b>Что мы отслеживаем:</b>\n"
                "• 🪙 Crypto — листинги, хардфорки, релизы\n"
                "• 🏈 Sports — матчи, турниры, финалы\n"
                "• 📈 Markets — отчеты, IPO, дивиденды\n"
                "• 💻 Tech — конференции, релизы, апдейты\n"
                "• 🌍 World — саммиты, выборы, праздники\n\n"
                "События появятся в течение ближайших дней."
            )
        else:
            # Фильтруем по importance
            filtered = [e for e in events if (e.get("importance") or 0) >= min_importance]
            filtered = filtered[:limit]

            if not filtered:
                text = (
                    "📅 <b>Календарь событий</b>\n\n"
                    f"⚠️ Нет событий с важностью ≥ {min_importance}\n\n"
                    f"Всего событий найдено: {len(events)}\n"
                    "Попробуйте изменить фильтр важности в настройках."
                )
            else:
                header = (
                    "📅 <b>Ближайшие важные события</b>\n\n"
                    f"Показано {len(filtered)} из {len(events)} событий\n"
                    f"Фильтр: важность ≥ {min_importance}\n\n"
                )
                text = header + format_events(filtered, limit=limit)

    if isinstance(target, types.Message):
        await target.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=back_inline_keyboard(),
        )
    else:
        await target.message.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=back_inline_keyboard(),
        )
        await target.answer()


@router.message(Command("events"))
async def cmd_events(message: types.Message):
    await send_events(message)


@router.callback_query(F.data == "events")
async def cb_events(query: types.CallbackQuery):
    await send_events(query)
