# telegram_bot/handlers/start.py
from aiogram import Router, types
from config.core.cloudflare import get_webapp_url

router = Router()

WEBAPP_URL = get_webapp_url()

WELCOME_TEXT = (
    "👋 Привет! Я PulseAI — твой AI-ассистент новостей\n\n"
    "Я анализирую 255 источников и создаю персональные дайджесты.\n\n"
    "📱 Открой приложение для работы:\n"
    "   • Новости и AI-дайджесты\n"
    "   • Календарь событий\n"
    "   • Настройка подписок\n"
    "   • Управление уведомлениями\n\n"
    "💡 Я буду присылать тебе уведомления о важных событиях!"
)


@router.message()
async def any_message(message: types.Message):
    """Обработка любого сообщения - показываем приложение"""
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📱 Открыть приложение", web_app=types.WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)
