# telegram_bot/handlers/start.py
from aiogram import types, Router
from aiogram.filters import Command

from telegram_bot.keyboards import start_inline_keyboard, main_inline_keyboard

router = Router()

WELCOME_TEXT = (
    "👋 Привет! Я <b>PulseAI</b> — твой персональный AI-ассистент новостей 🤖\n\n"
    "Я анализирую <b>255 источников</b> и создаю персональные дайджесты специально для тебя.\n\n"
    "📌 <b>Что я умею:</b>\n\n"
    "📰 <b>Новости</b>\n"
    "   • Последние материалы из 70 категорий\n"
    "   • AI-фильтрация по важности и достоверности\n\n"
    "🤖 <b>AI-дайджест</b>\n"
    "   • 4 профессиональных стиля: newsroom, analytical, magazine, casual\n"
    "   • Персонализация под твои интересы\n"
    "   • Система качества с ML-оптимизацией\n\n"
    "📅 <b>События</b>\n"
    "   • Умный календарь с AI-оценкой важности\n"
    "   • 20+ провайдеров: crypto, sports, markets, tech\n"
    "   • Уведомления о ключевых событиях\n\n"
    "🌐 <b>WebApp Dashboard</b>\n"
    "   • Полное управление подписками\n"
    "   • Настройка уведомлений\n"
    "   • Интерактивный календарь событий\n\n"
    "⚙️ <b>Настройки</b>\n"
    "   • Управление категориями подписок\n"
    "   • Настройка уведомлений\n"
    "   • Персонализация контента\n\n"
    "✨ <b>Начнём?</b> Нажми кнопку ниже 👇"
)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие + кнопка запуска"""
    await message.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=start_inline_keyboard())


@router.callback_query(lambda c: c.data == "start")
async def cb_start(query: types.CallbackQuery):
    """Показать главное меню"""
    await query.message.edit_text("📌 Главное меню:", reply_markup=main_inline_keyboard())
    await query.answer()


@router.callback_query(lambda c: c.data == "back")
async def cb_back(query: types.CallbackQuery):
    """Возврат в главное меню"""
    await query.message.edit_text("📌 Главное меню:", reply_markup=main_inline_keyboard())
    await query.answer()


@router.callback_query(lambda c: c.data == "settings")
async def cb_settings(query: types.CallbackQuery):
    """Показать меню настроек"""
    from telegram_bot.keyboards import settings_inline_keyboard

    settings_text = (
        "⚙️ <b>Настройки PulseAI</b>\n\n"
        "Здесь вы можете настроить систему под себя:\n\n"
        "📋 <b>Подписки</b>\n"
        "   • 2-уровневая структура: Категории → Подкатегории\n"
        "   • 70 категорий на выбор\n"
        "   • Добавить/удалить подписки\n"
        "   • Просмотр активных подписок\n\n"
        "🔔 <b>Уведомления</b>\n"
        "   • Настройка уведомлений о дайджестах\n"
        "   • Уведомления о событиях\n"
        "   • Персональные настройки времени\n\n"
        "💡 Все настройки также доступны в WebApp Dashboard"
    )
    await query.message.edit_text(settings_text, parse_mode="HTML", reply_markup=settings_inline_keyboard())
    await query.answer()


@router.callback_query(lambda c: c.data == "help")
async def cb_help(query: types.CallbackQuery):
    """Показать справку"""
    help_text = (
        "📖 <b>Справка по PulseAI</b>\n\n"
        "<b>Основные команды:</b>\n"
        "• /start — главное меню и приветствие\n"
        "• /digest_ai — AI-дайджест с выбором стиля\n"
        "• /events — календарь важных событий\n"
        "• /dashboard — открыть WebApp Dashboard\n"
        "• /notifications — управление уведомлениями\n"
        "• /subscribe <категория> — подписаться\n"
        "• /my_subs — мои подписки\n\n"
        "<b>💡 Возможности:</b>\n\n"
        "<b>📰 Новости:</b>\n"
        "• 255 RSS-источников в 70 категориях\n"
        "• ML-фильтрация по важности ≥ 0.6\n"
        "• Проверка достоверности ≥ 0.7\n\n"
        "<b>🤖 AI-дайджесты:</b>\n"
        "• <i>newsroom</i> — как Reuters/Bloomberg\n"
        "• <i>analytical</i> — глубокий анализ\n"
        "• <i>magazine</i> — storytelling стиль\n"
        "• <i>casual</i> — разговорный формат\n\n"
        "<b>📅 События:</b>\n"
        "• 20+ провайдеров (crypto, sports, tech)\n"
        "• AI-оценка важности событий\n"
        "• Автоматические уведомления\n\n"
        "<b>🌐 WebApp:</b>\n"
        "• Интерактивный календарь\n"
        "• Настройка подписок и уведомлений\n"
        "• Статистика и метрики\n\n"
        "<b>⚡ Советы:</b>\n"
        "• Используйте кнопки для быстрой навигации\n"
        "• Настройте категории в разделе Настройки\n"
        "• WebApp даёт полный контроль над системой\n"
        "• AI-дайджесты адаптируются под ваши интересы"
    )
    await query.message.edit_text(help_text, parse_mode="HTML", reply_markup=main_inline_keyboard())
    await query.answer()
