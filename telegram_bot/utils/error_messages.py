"""
User-friendly error messages for Telegram bot.

Simplified for minimalist bot (gateway + notifications).
"""

ERROR_MESSAGES = {
    # Rate limiting
    "rate_limit": "⏱️ Слишком много запросов. Подождите {seconds} секунд.",
    # Telegram API errors
    "bad_request": "❌ Некорректный запрос. Попробуйте другую команду.",
    "message_not_found": "❌ Сообщение не найдено. Возможно, оно было удалено.",
    "empty_message": "❌ Пустое сообщение. Попробуйте ещё раз.",
    "parse_error": "❌ Ошибка форматирования. Попробуйте ещё раз.",
    "api_error": "⚠️ Проблема с Telegram API. Попробуйте позже.",
    # User errors
    "user_not_found": "❌ Пользователь не найден. Попробуйте /start.",
    "permission_denied": "⛔ Недостаточно прав для выполнения действия.",
    "invalid_input": "❌ Некорректные данные. Проверьте ввод.",
    # Generic errors
    "unexpected_error": "⚠️ Произошла неожиданная ошибка. Мы уже работаем над исправлением.",
    "service_unavailable": "⚠️ Сервис временно недоступен. Попробуйте позже.",
    "try_again": "🔄 Попробуйте ещё раз через минуту.",
    # Success messages
    "success": "✅ Готово!",
    "settings_saved": "✅ Настройки сохранены",
}


# Helper function to get error message with optional formatting
def get_error_message(key: str, **kwargs) -> str:
    """
    Get error message by key with optional formatting.

    Args:
        key: Error message key
        **kwargs: Format parameters

    Returns:
        Formatted error message
    """
    message = ERROR_MESSAGES.get(key, ERROR_MESSAGES["unexpected_error"])
    try:
        return message.format(**kwargs)
    except (KeyError, ValueError):
        # If formatting fails, return original message
        return message
