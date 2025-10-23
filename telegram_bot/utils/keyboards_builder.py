"""
Simplified keyboard builder for minimalist bot.

Only basic confirmation keyboards needed.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_confirmation_keyboard(
    confirm_action: str,
    cancel_action: str = "back",
    confirm_text: str = "✅ Подтвердить",
    cancel_text: str = "❌ Отмена",
) -> InlineKeyboardMarkup:
    """
    Build confirmation keyboard.

    Args:
        confirm_action: Callback data for confirm action
        cancel_action: Callback data for cancel action
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button

    Returns:
        InlineKeyboardMarkup with confirmation buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=confirm_text, callback_data=confirm_action),
                InlineKeyboardButton(text=cancel_text, callback_data=cancel_action),
            ]
        ]
    )
