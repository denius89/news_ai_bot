# telegram_bot/handlers/start.py
from aiogram import types, Router
from aiogram.filters import Command

from telegram_bot.keyboards import start_inline_keyboard, main_inline_keyboard

router = Router()

WELCOME_TEXT = (
    "👋 Привет! Я <b>PulseAI бот</b> 🤖\n\n"
    "Я помогаю отслеживать важные новости и события.\n\n"
    "📌 Доступные разделы:\n"
    "• 📰 Новости — последние материалы\n"
    "• 🤖 AI-дайджест — краткое саммари за день\n"
    "• 📅 События — ближайшие события\n"
    "• 🌐 WebApp — полное управление подписками\n\n"
    "✨ Нажми кнопку ниже 👇"
)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие + кнопка запуска"""
    await message.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=start_inline_keyboard())


@router.callback_query(lambda c: c.data == "start")
async def cb_start(query: types.CallbackQuery):
    """Показать главное меню"""
    await query.message.edit_text("📌 Главное меню:", reply_markup=main_inline_keyboard())


@router.callback_query(lambda c: c.data == "back")
async def cb_back(query: types.CallbackQuery):
    """Возврат в главное меню"""
    await query.message.edit_text("↩️ Главное меню:", reply_markup=main_inline_keyboard())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по командам бота"""
    help_text = (
        "🤖 <b>PulseAI Bot - Справка</b>\n\n"
        "📌 <b>Основные команды:</b>\n"
        "• /start - Запуск бота и главное меню\n"
        "• /digest - Последние новости\n"
        "• /events - Ближайшие события\n"
        "• /notifications - Управление уведомлениями\n"
        "• /help - Эта справка\n\n"
        "🌐 <b>WebApp:</b>\n"
        "• Нажмите кнопку '🌐 WebApp' для полного управления подписками\n\n"
        "🔔 <b>Уведомления:</b>\n"
        "• Настраивайте уведомления через бот или WebApp\n"
        "• Получайте важные новости в реальном времени\n\n"
        "❓ <b>Поддержка:</b>\n"
        "Если у вас есть вопросы, обратитесь к администратору."
    )
    await message.answer(help_text, parse_mode="HTML")
