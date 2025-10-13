#!/usr/bin/env python3
"""
Тесты для JSON форматера дайджестов.
"""

import unittest
import json
from digests.json_formatter import format_json_digest_to_html, clean_json_from_text


class TestJSONFormatter(unittest.TestCase):
    """Тесты для форматирования JSON дайджестов."""

    def test_format_json_digest_to_html(self):
        """Тест преобразования JSON в HTML."""
        json_data = {
            "title": "Криптовалютный рынок обновляет максимумы",
            "dek": "Bitcoin достиг новых высот на фоне институционального интереса",
            "summary": "Bitcoin показал впечатляющий рост на этой неделе, достигнув новых максимумов. Институциональные инвесторы продолжают наращивать позиции.",
            "why_important": [
                "Рост институционального спроса",
                "Регуляторная ясность улучшается",
                "Технологические инновации ускоряются",
            ],
            "context": "Рынок показывает признаки зрелости",
            "what_next": "Ожидается продолжение роста",
            "sources_cited": ["CoinDesk", "Bloomberg"],
        }

        result = format_json_digest_to_html(json_data)

        # Проверяем наличие основных элементов
        self.assertIn("<b>Криптовалютный рынок обновляет максимумы</b>", result)
        self.assertIn("<i>Bitcoin достиг новых высот на фоне институционального интереса</i>", result)
        self.assertIn("Bitcoin показал впечатляющий рост", result)
        self.assertIn("<b>Почему это важно:</b>", result)
        self.assertIn("1. Рост институционального спроса", result)
        self.assertIn("2. Регуляторная ясность улучшается", result)
        self.assertIn("3. Технологические инновации ускоряются", result)
        self.assertIn("<b>Контекст:</b>", result)
        self.assertIn("<b>Что дальше:</b>", result)
        self.assertIn("<b>Источники:</b>", result)
        self.assertIn("• CoinDesk", result)
        self.assertIn("• Bloomberg", result)

    def test_format_json_string(self):
        """Тест преобразования JSON строки в HTML."""
        json_string = '{"title": "Тест", "summary": "Тестовый текст", "why_important": ["Важно"]}'

        result = format_json_digest_to_html(json_string)

        self.assertIn("<b>Тест</b>", result)
        self.assertIn("Тестовый текст", result)
        self.assertIn("1. Важно", result)

    def test_clean_json_from_text(self):
        """Тест очистки JSON из текста."""
        text_with_json = """
        Обычный текст
        {"title": "JSON заголовок", "summary": "JSON текст"}
        Еще обычный текст
        """

        result = clean_json_from_text(text_with_json)

        self.assertIn("Обычный текст", result)
        self.assertIn("<b>JSON заголовок</b>", result)
        self.assertIn("JSON текст", result)
        self.assertIn("Еще обычный текст", result)

    def test_clean_json_blocks(self):
        """Тест очистки JSON блоков с маркерами."""
        text_with_json_block = """
        Начало текста
        ```json
        {"title": "Заголовок", "summary": "Текст"}
        ```
        Конец текста
        """

        result = clean_json_from_text(text_with_json_block)

        self.assertIn("Начало текста", result)
        self.assertIn("<b>Заголовок</b>", result)
        self.assertIn("Текст", result)
        self.assertIn("Конец текста", result)

    def test_invalid_json_handling(self):
        """Тест обработки некорректного JSON."""
        invalid_json = '{"title": "Тест", "summary": "Текст"'  # Неполный JSON

        result = format_json_digest_to_html(invalid_json)

        # Должен вернуть исходную строку
        self.assertEqual(result, invalid_json)

    def test_empty_data_handling(self):
        """Тест обработки пустых данных."""
        empty_data = {}

        result = format_json_digest_to_html(empty_data)

        self.assertIn("<b>Дайджест новостей</b>", result)

    def test_minimal_data(self):
        """Тест обработки минимальных данных."""
        minimal_data = {"title": "Заголовок", "summary": "Текст"}

        result = format_json_digest_to_html(minimal_data)

        self.assertIn("<b>Заголовок</b>", result)
        self.assertIn("Текст", result)
        # Не должно быть секций, которых нет в данных
        self.assertNotIn("<b>Почему это важно:</b>", result)
        self.assertNotIn("<b>Контекст:</b>", result)


if __name__ == "__main__":
    unittest.main()
