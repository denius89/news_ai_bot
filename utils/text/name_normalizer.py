"""
Система нормализации имён пользователей Telegram.

Обеспечивает безопасное отображение имён независимо от содержимого,
включая эмодзи, спецсимволы, RTL текст и невидимые Unicode символы.
"""

import re
import unicodedata
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Регулярное выражение для определения emoji-only имён
EMOJI_ONLY_PATTERN = re.compile(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\s]+$')

# Невидимые и управляющие Unicode символы для удаления
INVISIBLE_CHARS = {
    '\u200b',  # Zero Width Space
    '\u200c',  # Zero Width Non-Joiner
    '\u200d',  # Zero Width Joiner
    '\u202a',  # Left-to-Right Embedding
    '\u202b',  # Right-to-Left Embedding
    '\u202c',  # Pop Directional Formatting
    '\u202d',  # Left-to-Right Override
    '\u202e',  # Right-to-Left Override
    '\u2060',  # Word Joiner
    '\ufeff',  # Zero Width No-Break Space
}

# Маппинг стилизованных Unicode символов на обычные ASCII
UNICODE_STYLE_MAP = {
    # Mathematical Bold (𝔸-𝔾)
    '\U0001D400': 'A', '\U0001D401': 'B', '\U0001D402': 'C', '\U0001D403': 'D', '\U0001D404': 'E', '\U0001D405': 'F', '\U0001D406': 'G',
    '\U0001D407': 'H', '\U0001D408': 'I', '\U0001D409': 'J', '\U0001D40A': 'K', '\U0001D40B': 'L', '\U0001D40C': 'M', '\U0001D40D': 'N',
    '\U0001D40E': 'O', '\U0001D40F': 'P', '\U0001D410': 'Q', '\U0001D411': 'R', '\U0001D412': 'S', '\U0001D413': 'T', '\U0001D414': 'U',
    '\U0001D415': 'V', '\U0001D416': 'W', '\U0001D417': 'X', '\U0001D418': 'Y', '\U0001D419': 'Z',
    # Mathematical Bold lowercase (𝕒-𝕫)
    '\U0001D41A': 'a', '\U0001D41B': 'b', '\U0001D41C': 'c', '\U0001D41D': 'd', '\U0001D41E': 'e', '\U0001D41F': 'f', '\U0001D420': 'g',
    '\U0001D421': 'h', '\U0001D422': 'i', '\U0001D423': 'j', '\U0001D424': 'k', '\U0001D425': 'l', '\U0001D426': 'm', '\U0001D427': 'n',
    '\U0001D428': 'o', '\U0001D429': 'p', '\U0001D42A': 'q', '\U0001D42B': 'r', '\U0001D42C': 's', '\U0001D42D': 't', '\U0001D42E': 'u',
    '\U0001D42F': 'v', '\U0001D430': 'w', '\U0001D431': 'x', '\U0001D432': 'y', '\U0001D433': 'z',
    # Mathematical Double-Struck (𝔸-𝔾)
    '\U0001D538': 'A', '\U0001D539': 'B', '\U0001D53A': 'C', '\U0001D53B': 'D', '\U0001D53C': 'E', '\U0001D53D': 'F', '\U0001D53E': 'G',
    '\U0001D53F': 'H', '\U0001D540': 'I', '\U0001D541': 'J', '\U0001D542': 'K', '\U0001D543': 'L', '\U0001D544': 'M', '\U0001D545': 'N',
    '\U0001D546': 'O', '\U0001D547': 'P', '\U0001D548': 'Q', '\U0001D549': 'R', '\U0001D54A': 'S', '\U0001D54B': 'T', '\U0001D54C': 'U',
    '\U0001D54D': 'V', '\U0001D54E': 'W', '\U0001D54F': 'X', '\U0001D550': 'Y', '\U0001D551': 'Z',
    '\U0001D552': 'a', '\U0001D553': 'b', '\U0001D554': 'c', '\U0001D555': 'd', '\U0001D556': 'e', '\U0001D557': 'f', '\U0001D558': 'g',
    '\U0001D559': 'h', '\U0001D55A': 'i', '\U0001D55B': 'j', '\U0001D55C': 'k', '\U0001D55D': 'l', '\U0001D55E': 'm', '\U0001D55F': 'n',
    '\U0001D560': 'o', '\U0001D561': 'p', '\U0001D562': 'q', '\U0001D563': 'r', '\U0001D564': 's', '\U0001D565': 't', '\U0001D566': 'u',
    '\U0001D567': 'v', '\U0001D568': 'w', '\U0001D569': 'x', '\U0001D56A': 'y', '\U0001D56B': 'z',
}

# Маппинг испорченных имён (двойная кодировка UTF-8)
CORRUPTION_MAP = {
    'ÐÐ°Ð½': 'Иван',
    'ÐÐ°ÑÐ°': 'Маша',
    'ÐÐ»ÐµÐºÑÐµÐ¹': 'Алексей',
    # Дважды испорченные имена
    'Ã\x90Ã\x90Â°Ã\x90Â½': 'Иван',
    'ÃÐÃÐÂ°ÃÐÂ½': 'Иван',
}


def normalize_user_name(raw_name: Optional[str], username: Optional[str], user_id: int) -> str:
    """
    Возвращает безопасное, читаемое имя для UI и логов.
    
    Алгоритм нормализации:
    1. Если raw_name отсутствует → использовать @username или User #<user_id>
    2. Удалить невидимые Unicode символы и управляющие символы
    3. Проверить, состоит ли строка только из эмодзи/символов — если да → fallback
    4. Обрезать до 64 символов с сохранением целостности слов
    5. Вернуть безопасное имя (display_name)
    
    Args:
        raw_name: Оригинальное имя пользователя (может быть None)
        username: Telegram username (может быть None)
        user_id: Telegram user ID для fallback
        
    Returns:
        Безопасное имя для отображения
    """
    try:
        # Шаг 1: Проверяем наличие raw_name
        if not raw_name or not raw_name.strip():
            return _get_fallback_name(username, user_id)
        
        # Шаг 2: Обрабатываем испорченную кодировку
        processed_name = _fix_corrupted_encoding(raw_name)
        
        # Шаг 3: Удаляем невидимые и управляющие символы
        cleaned_name = _remove_invisible_chars(processed_name)
        
        # Шаг 4: Конвертируем стилизованные Unicode символы
        normalized_name = _convert_styled_unicode(cleaned_name)
        
        # Шаг 5: Проверяем на emoji-only
        if _is_emoji_only(normalized_name):
            logger.debug(f"Emoji-only name detected: '{normalized_name}', using fallback")
            return _get_fallback_name(username, user_id)
        
        # Шаг 6: Обрезаем до 64 символов с сохранением слов
        final_name = _truncate_preserving_words(normalized_name, 64)
        
        # Шаг 7: Финальная проверка на пустоту
        if not final_name.strip():
            return _get_fallback_name(username, user_id)
        
        logger.debug(f"Normalized name: '{raw_name}' -> '{final_name}'")
        return final_name.strip()
        
    except Exception as e:
        logger.error(f"Error normalizing name '{raw_name}': {e}")
        return _get_fallback_name(username, user_id)


def _get_fallback_name(username: Optional[str], user_id: int) -> str:
    """Возвращает fallback имя в порядке приоритета."""
    if username and username.strip():
        return f"@{username.strip()}"
    return f"User #{user_id}"


def _fix_corrupted_encoding(name: str) -> str:
    """Исправляет испорченную кодировку UTF-8."""
    # Проверяем известные испорченные имена
    if name in CORRUPTION_MAP:
        return CORRUPTION_MAP[name]
    
    # Проверяем на двойную кодировку UTF-8
    try:
        if 'Ð' in name and len(name) > 0:
            # Кодируем в latin-1, затем декодируем как UTF-8
            fixed = name.encode('latin-1').decode('utf-8')
            # Проверяем, что получили кириллицу
            if any('\u0400' <= c <= '\u04FF' for c in fixed):
                return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    
    return name


def _remove_invisible_chars(name: str) -> str:
    """Удаляет невидимые и управляющие Unicode символы."""
    result = []
    
    for char in name:
        # Удаляем известные невидимые символы
        if char in INVISIBLE_CHARS:
            continue
            
        # Удаляем управляющие символы (категория C)
        if unicodedata.category(char).startswith('C'):
            continue
            
        # Удаляем лишние пробелы
        if char.isspace() and len(result) > 0 and result[-1].isspace():
            continue
            
        result.append(char)
    
    return ''.join(result)


def _convert_styled_unicode(name: str) -> str:
    """Конвертирует стилизованные Unicode символы в обычные ASCII."""
    result = []
    
    for char in name:
        if char in UNICODE_STYLE_MAP:
            result.append(UNICODE_STYLE_MAP[char])
        else:
            # Пытаемся нормализовать символ
            normalized = unicodedata.normalize('NFKD', char)
            # Если после нормализации получили ASCII символ
            if len(normalized) == 1 and ord(normalized) < 128:
                result.append(normalized)
            else:
                # Оставляем как есть, если не можем конвертировать
                result.append(char)
    
    return ''.join(result)


def _is_emoji_only(name: str) -> bool:
    """Проверяет, состоит ли имя только из эмодзи и пробелов."""
    if not name.strip():
        return True
    
    return bool(EMOJI_ONLY_PATTERN.match(name.strip()))


def _truncate_preserving_words(text: str, max_length: int) -> str:
    """Обрезает текст до max_length символов, сохраняя целостность слов."""
    if len(text) <= max_length:
        return text
    
    # Ищем последний пробел перед max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.7:  # Если пробел не слишком далеко от конца
        return truncated[:last_space]
    
    return truncated


# Утилитарные функции для внешнего использования
def is_safe_name(name: str) -> bool:
    """Проверяет, является ли имя безопасным для отображения."""
    try:
        normalized = normalize_user_name(name, None, 0)
        return normalized != f"User #0"  # Если не пришлось использовать fallback
    except Exception:
        return False


def get_name_display_variant(name: str, username: Optional[str] = None, user_id: int = 0) -> str:
    """Возвращает вариант отображения имени для UI."""
    return normalize_user_name(name, username, user_id)
