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
    "• 📅 События — ближайшие события\n\n"
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
