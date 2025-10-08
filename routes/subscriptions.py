"""
Telegram bot routes for subscription management.

This module provides aiogram v3 handlers for managing user subscriptions
to news categories.
"""

from aiogram import Router, types
from aiogram.filters import Command

from services.subscription_service import SubscriptionService
from config.core.constants import CATEGORIES

router = Router()
svc = SubscriptionService()


@router.message(Command("subscribe"))
async def cmd_subscribe(m: types.Message):
    """Handle /subscribe command to add subscription to a category."""
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Использование: /subscribe <category>")

    cat = parts[1].strip().lower()
    uid = await svc.get_or_create_user(m.from_user.id, m.from_user.username)
    ok = await svc.add(uid, cat)

    await m.answer("✅ Подписка добавлена" if ok else "ℹ️ Вы уже подписаны")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(m: types.Message):
    """Handle /unsubscribe command to remove subscription from a category."""
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Использование: /unsubscribe <category>")

    cat = parts[1].strip().lower()
    uid = await svc.get_or_create_user(m.from_user.id, m.from_user.username)
    deleted = await svc.remove(uid, cat)

    await m.answer("🗑 Подписка удалена" if deleted else "❓ Подписки не было")


@router.message(Command("my_subs"))
async def cmd_my_subs(m: types.Message):
    """Handle /my_subs command to show user's subscriptions."""
    uid = await svc.get_or_create_user(m.from_user.id, m.from_user.username)
    subs = await svc.list(uid)

    if not subs:
        return await m.answer("У вас пока нет подписок. Добавьте: /subscribe crypto")

    cats = ", ".join(sorted({s["category"] for s in subs}))
    await m.answer(f"Ваши подписки: {cats}")


@router.message(Command("categories"))
async def cmd_categories(m: types.Message):
    """Handle /categories command to show available categories."""
    cats_text = ", ".join(sorted(CATEGORIES))
    await m.answer(f"Доступные категории:\n\n{cats_text}")


@router.message(Command("help_subs"))
async def cmd_help_subs(m: types.Message):
    """Handle /help_subs command to show subscription help."""
    help_text = """
📋 Управление подписками:

/subscribe <категория> - подписаться на категорию
/unsubscribe <категория> - отписаться от категории
/my_subs - показать ваши подписки
/categories - показать доступные категории

Примеры:
/subscribe crypto
/subscribe economy
/unsubscribe tech
"""
    await m.answer(help_text)
