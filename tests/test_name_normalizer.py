"""
Тесты для системы нормализации имён пользователей Telegram.

Покрывает все edge cases: emoji-only имена, RTL текст, невидимые символы,
длинные имена, китайские/японские символы, стилизованные Unicode.
"""

import pytest
from utils.text.name_normalizer import (
    normalize_user_name,
    is_safe_name,
    get_name_display_variant,
    _fix_corrupted_encoding,
    _remove_invisible_chars,
    _convert_styled_unicode,
    _is_emoji_only,
    _truncate_preserving_words,
)


class TestNameNormalizer:
    """Тесты основной функции нормализации имён."""

    def test_normalize_basic_name(self):
        """Тест нормализации обычного имени."""
        result = normalize_user_name("John Doe", "johndoe", 12345)
        assert result == "John Doe"

    def test_normalize_empty_name(self):
        """Тест нормализации пустого имени."""
        result = normalize_user_name("", "johndoe", 12345)
        assert result == "@johndoe"

        result = normalize_user_name(None, "johndoe", 12345)
        assert result == "@johndoe"

    def test_normalize_no_username(self):
        """Тест нормализации без username."""
        result = normalize_user_name("", None, 12345)
        assert result == "User #12345"

    def test_normalize_emoji_only(self):
        """Тест нормализации emoji-only имён."""
        result = normalize_user_name("🔥🔥🔥", "fireuser", 12345)
        assert result == "@fireuser"

        result = normalize_user_name("🔥🔥🔥", None, 12345)
        assert result == "User #12345"

        result = normalize_user_name("😀😁😂", None, 12345)
        assert result == "User #12345"

    def test_normalize_invisible_chars(self):
        """Тест нормализации невидимых символов."""
        result = normalize_user_name("John\u200bDoe", "johndoe", 12345)
        assert result == "JohnDoe"

        result = normalize_user_name("John\u202aDoe\u202c", "johndoe", 12345)
        assert result == "JohnDoe"

    def test_normalize_styled_unicode(self):
        """Тест нормализации стилизованных Unicode символов."""
        result = normalize_user_name("𝕀𝕧𝕒𝕟", "ivan", 12345)
        assert result == "Ivan"

        result = normalize_user_name("𝔸𝕝𝕖𝕩", "alex", 12345)
        assert result == "Alex"

    def test_normalize_corrupted_encoding(self):
        """Тест нормализации испорченной кодировки."""
        result = normalize_user_name("ÐÐ°Ð½", "ivan", 12345)
        assert result == "Иван"

        result = normalize_user_name("ÐÐ°ÑÐ°", "masha", 12345)
        assert result == "Маша"

    def test_normalize_long_name(self):
        """Тест нормализации длинных имён."""
        long_name = "A" * 100
        result = normalize_user_name(long_name, "longuser", 12345)
        assert len(result) <= 64
        assert result.endswith("A")  # Должно сохранить целостность слов

    def test_normalize_rtl_text(self):
        """Тест нормализации RTL текста."""
        result = normalize_user_name("مرحبا", "arabic", 12345)
        assert result == "مرحبا"  # RTL текст должен сохраниться

    def test_normalize_chinese_japanese(self):
        """Тест нормализации китайских и японских символов."""
        result = normalize_user_name("张三", "chinese", 12345)
        assert result == "张三"

        result = normalize_user_name("田中", "japanese", 12345)
        assert result == "田中"

    def test_normalize_mixed_content(self):
        """Тест нормализации смешанного контента."""
        result = normalize_user_name("John🔥Doe", "johndoe", 12345)
        assert result == "John🔥Doe"  # Эмодзи в середине должны сохраниться

    def test_normalize_whitespace(self):
        """Тест нормализации пробелов."""
        result = normalize_user_name("  John   Doe  ", "johndoe", 12345)
        assert result == "John Doe"  # Лишние пробелы должны быть удалены


class TestHelperFunctions:
    """Тесты вспомогательных функций."""

    def test_fix_corrupted_encoding(self):
        """Тест исправления испорченной кодировки."""
        assert _fix_corrupted_encoding("ÐÐ°Ð½") == "Иван"
        assert _fix_corrupted_encoding("ÐÐ°ÑÐ°") == "Маша"
        assert _fix_corrupted_encoding("Normal") == "Normal"

    def test_remove_invisible_chars(self):
        """Тест удаления невидимых символов."""
        assert _remove_invisible_chars("John\u200bDoe") == "JohnDoe"
        assert _remove_invisible_chars("John\u202aDoe\u202c") == "JohnDoe"
        assert _remove_invisible_chars("Normal") == "Normal"

    def test_convert_styled_unicode(self):
        """Тест конвертации стилизованных Unicode."""
        assert _convert_styled_unicode("𝕀𝕧𝕒𝕟") == "Ivan"
        assert _convert_styled_unicode("𝔸𝕝𝕖𝕩") == "Alex"
        assert _convert_styled_unicode("Normal") == "Normal"

    def test_is_emoji_only(self):
        """Тест проверки emoji-only имён."""
        assert _is_emoji_only("🔥🔥🔥") == True
        assert _is_emoji_only("😀😁😂") == True
        assert _is_emoji_only("John") == False
        assert _is_emoji_only("John🔥") == False
        assert _is_emoji_only("") == True
        assert _is_emoji_only("   ") == True

    def test_truncate_preserving_words(self):
        """Тест обрезки с сохранением слов."""
        text = "This is a very long text that should be truncated"
        result = _truncate_preserving_words(text, 20)
        assert len(result) <= 20
        assert not result.endswith(" ")  # Не должно заканчиваться пробелом

        # Тест с коротким текстом
        short_text = "Short"
        result = _truncate_preserving_words(short_text, 20)
        assert result == short_text


class TestUtilityFunctions:
    """Тесты утилитарных функций."""

    def test_is_safe_name(self):
        """Тест проверки безопасности имени."""
        assert is_safe_name("John Doe") == True
        assert is_safe_name("🔥🔥🔥") == False
        assert is_safe_name("") == False
        assert is_safe_name("𝕀𝕧𝕒𝕟") == True  # Стилизованные символы конвертируются

    def test_get_name_display_variant(self):
        """Тест получения варианта отображения имени."""
        assert get_name_display_variant("John Doe") == "John Doe"
        assert get_name_display_variant("🔥🔥🔥") == "User #0"
        assert get_name_display_variant("", "johndoe", 12345) == "@johndoe"


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_unicode_normalization(self):
        """Тест нормализации Unicode."""
        # Тест с различными формами Unicode
        result = normalize_user_name("café", "cafe", 12345)
        assert result == "café"  # Должно сохранить акценты

        result = normalize_user_name("naïve", "naive", 12345)
        assert result == "naïve"  # Должно сохранить умляуты

    def test_control_characters(self):
        """Тест управляющих символов."""
        result = normalize_user_name("John\x00Doe", "johndoe", 12345)
        assert "\x00" not in result  # Null символы должны быть удалены

    def test_very_long_emoji(self):
        """Тест очень длинных emoji-only имён."""
        long_emoji = "🔥" * 100
        result = normalize_user_name(long_emoji, None, 12345)
        assert result == "User #12345"

    def test_mixed_scripts(self):
        """Тест смешанных скриптов."""
        result = normalize_user_name("John田中", "mixed", 12345)
        assert result == "John田中"  # Смешанные скрипты должны сохраниться

    def test_special_characters(self):
        """Тест специальных символов."""
        result = normalize_user_name("John-Doe", "johndoe", 12345)
        assert result == "John-Doe"  # Дефисы должны сохраниться

        result = normalize_user_name("John_Doe", "johndoe", 12345)
        assert result == "John_Doe"  # Подчеркивания должны сохраниться


class TestPerformance:
    """Тесты производительности."""

    def test_large_input_performance(self):
        """Тест производительности с большими входными данными."""
        large_name = "A" * 10000
        result = normalize_user_name(large_name, "largeuser", 12345)
        assert len(result) <= 64
        assert result != "User #12345"  # Должно обработать, а не использовать fallback

    def test_many_unicode_chars(self):
        """Тест производительности с множеством Unicode символов."""
        unicode_name = "𝕀𝕧𝕒𝕟" * 1000
        result = normalize_user_name(unicode_name, "unicodeuser", 12345)
        assert len(result) <= 64
        assert "Ivan" in result  # Должно конвертировать стилизованные символы


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
