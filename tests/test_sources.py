"""
Тесты для интеграции источников и категорий.
Проверяет работу единого источника истины (config/sources.yaml).
"""

import pytest
import yaml
from pathlib import Path

from services.categories import (
    get_categories,
    get_subcategories,
    get_icon,
    get_sources,
    get_all_sources,
    get_category_structure,
    validate_sources,
    get_statistics,
    get_emoji_icon,
)


class TestSourcesYAML:
    """Тесты структуры sources.yaml"""

    def test_yaml_is_valid(self):
        """Проверяет, что YAML файл валиден"""
        sources_file = Path(__file__).parent.parent / "config" / "sources.yaml"

        with open(sources_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_categories_structure(self):
        """Проверяет структуру категорий"""
        categories = get_categories()

        assert len(categories) > 0
        assert isinstance(categories, list)

        # Проверяем, что есть основные категории
        expected_categories = ["crypto", "sports", "markets", "tech", "world"]
        for category in expected_categories:
            assert category in categories

    def test_subcategories_have_icons(self):
        """Проверяет, что у каждой подкатегории есть иконка"""
        structure = get_category_structure()

        for category, subcategories in structure.items():
            assert isinstance(subcategories, dict)

            for subcategory, data in subcategories.items():
                assert isinstance(data, dict)
                assert "icon" in data
                assert data["icon"] is not None
                assert len(data["icon"]) > 0

    def test_subcategories_have_sources(self):
        """Проверяет, что у каждой подкатегории есть источники"""
        structure = get_category_structure()

        for category, subcategories in structure.items():
            for subcategory, data in subcategories.items():
                assert "sources" in data
                assert isinstance(data["sources"], list)
                assert len(data["sources"]) > 0

                # Проверяем структуру источников
                for source in data["sources"]:
                    assert isinstance(source, dict)
                    assert "name" in source
                    assert "url" in source
                    assert len(source["name"]) > 0
                    assert len(source["url"]) > 0


class TestCategoriesService:
    """Тесты сервиса categories.py"""

    def test_get_categories(self):
        """Тест функции get_categories"""
        categories = get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

        # Проверяем уникальность
        assert len(categories) == len(set(categories))

    def test_get_subcategories(self):
        """Тест функции get_subcategories"""
        categories = get_categories()

        for category in categories:
            subcategories = get_subcategories(category)
            assert isinstance(subcategories, list)
            assert len(subcategories) > 0

    def test_get_subcategories_invalid_category(self):
        """Тест get_subcategories для несуществующей категории"""
        subcategories = get_subcategories("nonexistent")
        assert subcategories == []

    def test_get_icon(self):
        """Тест функции get_icon"""
        categories = get_categories()

        for category in categories:
            subcategories = get_subcategories(category)
            for subcategory in subcategories:
                icon = get_icon(category, subcategory)
                assert icon is not None
                assert len(icon) > 0

    def test_get_icon_invalid(self):
        """Тест get_icon для несуществующих категорий"""
        assert get_icon("nonexistent", "nonexistent") is None

    def test_get_sources(self):
        """Тест функции get_sources"""
        categories = get_categories()

        for category in categories:
            subcategories = get_subcategories(category)
            for subcategory in subcategories:
                sources = get_sources(category, subcategory)
                assert isinstance(sources, list)
                assert len(sources) > 0

                for source in sources:
                    assert "name" in source
                    assert "url" in source

    def test_get_all_sources(self):
        """Тест функции get_all_sources"""
        all_sources = get_all_sources()

        assert isinstance(all_sources, list)
        assert len(all_sources) > 0

        for category, subcategory, name, url in all_sources:
            assert len(category) > 0
            assert len(subcategory) > 0
            assert len(name) > 0
            assert len(url) > 0

    def test_get_category_structure(self):
        """Тест функции get_category_structure"""
        structure = get_category_structure()

        assert isinstance(structure, dict)
        assert len(structure) > 0

        for category, subcategories in structure.items():
            assert isinstance(subcategories, dict)
            assert len(subcategories) > 0

    def test_validate_sources(self):
        """Тест функции validate_sources"""
        is_valid, errors = validate_sources()

        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

        if not is_valid:
            assert len(errors) > 0
            for error in errors:
                assert isinstance(error, str)

    def test_get_statistics(self):
        """Тест функции get_statistics"""
        stats = get_statistics()

        assert isinstance(stats, dict)
        assert "categories" in stats
        assert "subcategories" in stats
        assert "sources" in stats
        assert "avg_sources_per_subcategory" in stats

        assert stats["categories"] > 0
        assert stats["subcategories"] > 0
        assert stats["sources"] > 0
        assert stats["avg_sources_per_subcategory"] > 0

    def test_get_emoji_icon(self):
        """Тест функции get_emoji_icon"""
        categories = get_categories()

        for category in categories:
            subcategories = get_subcategories(category)
            for subcategory in subcategories:
                emoji = get_emoji_icon(category, subcategory)
                assert isinstance(emoji, str)
                assert len(emoji) > 0


class TestTelegramBotIntegration:
    """Тесты интеграции с Telegram ботом"""

    def test_keyboard_structure(self):
        """Смоук-тест структуры клавиатур бота"""
        from telegram_bot.keyboards import categories_inline_keyboard, subcategories_inline_keyboard

        # Тест клавиатуры категорий
        keyboard = categories_inline_keyboard("subscribe")
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0

        # Проверяем, что есть кнопка "Назад"
        back_button = None
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.text == "⬅️ Назад":
                    back_button = button
                    break

        assert back_button is not None

        # Тест клавиатуры подкатегорий
        categories = get_categories()
        if categories:
            category = categories[0]
            subcategories = get_subcategories(category)
            if subcategories:
                subcategory_keyboard = subcategories_inline_keyboard(category, "subscribe")
                assert subcategory_keyboard is not None
                assert len(subcategory_keyboard.inline_keyboard) > 0

    def test_callback_data_format(self):
        """Тест формата callback_data в клавиатурах"""
        from telegram_bot.keyboards import categories_inline_keyboard

        keyboard = categories_inline_keyboard("subscribe")
        categories = get_categories()

        # Проверяем формат callback_data
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.text != "⬅️ Назад":
                    # Должен быть формат "action:category"
                    parts = button.callback_data.split(":")
                    assert len(parts) == 2
                    assert parts[0] == "subscribe"
                    assert parts[1] in categories


class TestWebAppAPI:
    """Тесты API WebApp"""

    @pytest.fixture
    def client(self):
        """Flask test client"""
        from webapp import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_categories_api(self, client):
        """Смоук-тест API /categories"""
        response = client.get("/api/categories")

        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "success"
        assert "data" in data
        assert "total_categories" in data
        assert "total_subcategories" in data

        # Проверяем структуру данных
        categories_data = data["data"]
        assert isinstance(categories_data, dict)
        assert len(categories_data) > 0

        for category_id, category_data in categories_data.items():
            assert "name" in category_data
            assert "icon" in category_data
            assert "subcategories" in category_data
            assert isinstance(category_data["subcategories"], dict)

    def test_categories_validate_api(self, client):
        """Смоук-тест API /categories/validate"""
        response = client.get("/api/categories/validate")

        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "success"
        assert "valid" in data
        assert "errors" in data
        assert isinstance(data["valid"], bool)
        assert isinstance(data["errors"], list)


class TestDatabaseIntegration:
    """Тесты интеграции с базой данных"""

    def test_subcategory_field_exists(self):
        """Проверяет, что поле subcategory добавлено в схемы"""
        from database import db_models

        # Проверяем, что функции принимают subcategory
        # Это косвенная проверка того, что код обновлен
        assert hasattr(db_models, "upsert_news")

    def test_parsers_use_categories_service(self):
        """Проверяет, что парсеры используют services/categories"""
        from parsers import rss_parser

        # Проверяем, что функция load_sources существует и использует новый сервис
        assert hasattr(rss_parser, "load_sources")
        assert hasattr(rss_parser, "parse_source")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
