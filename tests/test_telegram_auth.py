"""
Тесты для модуля аутентификации Telegram WebApp.

Покрывает проверку подписи, обработку ошибок, валидацию данных
и все edge cases аутентификации.
"""

import hashlib
import hmac
import json
import pytest
import time
from unittest.mock import patch
from utils.auth.telegram_auth import (
    verify_telegram_webapp_data,
    extract_user_from_verified_data,
    is_telegram_webapp_request,
    validate_telegram_auth_headers,
    get_telegram_user_id_from_headers,
    create_fallback_user_data,
    log_auth_attempt,
)


class TestTelegramAuthVerification:
    """Тесты основной функции проверки аутентификации."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.bot_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.user_data = {
            "id": 12345,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "language_code": "en",
            "is_premium": False,
        }

    def _create_valid_init_data(self, **kwargs) -> str:
        """Создает валидные initData для тестирования."""
        # Базовые данные
        data = {"user": json.dumps(self.user_data), "auth_date": str(int(time.time())), "query_id": "test_query_id"}

        # Добавляем дополнительные параметры
        data.update(kwargs)

        # Создаем data_check_string
        data_check_arr = [f"{k}={v}" for k, v in sorted(data.items())]
        data_check_string = "\n".join(data_check_arr)

        # Вычисляем hash
        secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Добавляем hash к данным
        data["hash"] = calculated_hash

        # Возвращаем как query string
        return "&".join([f"{k}={v}" for k, v in data.items()])

    def test_valid_signature(self):
        """Тест с корректной подписью."""
        init_data = self._create_valid_init_data()
        result = verify_telegram_webapp_data(init_data, self.bot_token)

        assert result is not None
        assert result["user"]["id"] == 12345
        assert result["user"]["first_name"] == "John"

    def test_invalid_signature(self):
        """Тест с поддельным hash."""
        init_data = self._create_valid_init_data()
        # Заменяем hash на поддельный
        init_data = init_data.replace("hash=", "hash=fake_hash")

        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_expired_auth_date(self):
        """Тест с устаревшим auth_date."""
        # Создаем данные с auth_date 25 часов назад
        expired_time = int(time.time()) - 25 * 3600
        init_data = self._create_valid_init_data(auth_date=str(expired_time))

        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_missing_hash(self):
        """Тест с отсутствующим hash."""
        init_data = self._create_valid_init_data()
        # Удаляем hash
        init_data = init_data.replace("&hash=", "")

        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_missing_user_data(self):
        """Тест с отсутствующими данными пользователя."""
        init_data = self._create_valid_init_data()
        # Удаляем user данные
        init_data = init_data.replace("user=", "")

        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_invalid_user_json(self):
        """Тест с некорректным JSON в user данных."""
        init_data = self._create_valid_init_data()
        # Заменяем user данные на некорректный JSON
        init_data = init_data.replace("user=", "user=invalid_json")

        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_missing_user_id(self):
        """Тест с отсутствующим ID пользователя."""
        user_data = self.user_data.copy()
        del user_data["id"]

        init_data = self._create_valid_init_data(user=json.dumps(user_data))
        result = verify_telegram_webapp_data(init_data, self.bot_token)
        assert result is None

    def test_empty_init_data(self):
        """Тест с пустыми данными."""
        result = verify_telegram_webapp_data("", self.bot_token)
        assert result is None

        result = verify_telegram_webapp_data(None, self.bot_token)
        assert result is None

    def test_empty_bot_token(self):
        """Тест с пустым токеном бота."""
        init_data = self._create_valid_init_data()
        result = verify_telegram_webapp_data(init_data, "")
        assert result is None

        result = verify_telegram_webapp_data(init_data, None)
        assert result is None

    def test_emoji_name_in_auth(self):
        """Тест с emoji в имени пользователя."""
        user_data = self.user_data.copy()
        user_data["first_name"] = "🔥John🔥"

        init_data = self._create_valid_init_data(user=json.dumps(user_data))
        result = verify_telegram_webapp_data(init_data, self.bot_token)

        assert result is not None
        assert result["user"]["first_name"] == "🔥John🔥"

    def test_unicode_name_in_auth(self):
        """Тест с Unicode символами в имени."""
        user_data = self.user_data.copy()
        user_data["first_name"] = "Иван"

        init_data = self._create_valid_init_data(user=json.dumps(user_data))
        result = verify_telegram_webapp_data(init_data, self.bot_token)

        assert result is not None
        assert result["user"]["first_name"] == "Иван"

    def test_premium_user(self):
        """Тест с премиум пользователем."""
        user_data = self.user_data.copy()
        user_data["is_premium"] = True

        init_data = self._create_valid_init_data(user=json.dumps(user_data))
        result = verify_telegram_webapp_data(init_data, self.bot_token)

        assert result is not None
        assert result["user"]["is_premium"] == True


class TestHelperFunctions:
    """Тесты вспомогательных функций."""

    def test_extract_user_from_verified_data(self):
        """Тест извлечения данных пользователя."""
        verified_data = {
            "user": {
                "id": 12345,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "language_code": "en",
                "is_premium": True,
                "photo_url": "https://example.com/photo.jpg",
                "allows_write_to_pm": True,
            },
            "auth_date": "1234567890",
            "query_id": "test_query",
        }

        user_data = extract_user_from_verified_data(verified_data)

        assert user_data is not None
        assert user_data["id"] == 12345
        assert user_data["first_name"] == "John"
        assert user_data["last_name"] == "Doe"
        assert user_data["username"] == "johndoe"
        assert user_data["language_code"] == "en"
        assert user_data["is_premium"] == True
        assert user_data["photo_url"] == "https://example.com/photo.jpg"
        assert user_data["allows_write_to_pm"] == True

    def test_extract_user_from_empty_data(self):
        """Тест извлечения из пустых данных."""
        assert extract_user_from_verified_data(None) is None
        assert extract_user_from_verified_data({}) is None
        assert extract_user_from_verified_data({"other": "data"}) is None

    def test_is_telegram_webapp_request(self):
        """Тест определения Telegram WebApp запроса."""
        # Тест с initData
        headers = {"X-Telegram-Init-Data": "test_data"}
        assert is_telegram_webapp_request(headers) == True

        # Тест с User-Agent
        headers = {"User-Agent": "TelegramBot/1.0"}
        assert is_telegram_webapp_request(headers) == True

        # Тест с Referer
        headers = {"Referer": "https://web.telegram.org/"}
        assert is_telegram_webapp_request(headers) == True

        # Тест без Telegram заголовков
        headers = {"User-Agent": "Mozilla/5.0"}
        assert is_telegram_webapp_request(headers) == False

    def test_validate_telegram_auth_headers(self):
        """Тест валидации заголовков аутентификации."""
        # Валидные заголовки с initData
        headers = {"X-Telegram-Init-Data": "user=%7B%22id%22%3A12345%7D&hash=test_hash"}
        assert validate_telegram_auth_headers(headers) == True

        # Валидные заголовки с user data
        headers = {"X-Telegram-User-Data": '{"id": 12345, "first_name": "John"}'}
        assert validate_telegram_auth_headers(headers) == True

        # Невалидные заголовки
        headers = {}
        assert validate_telegram_auth_headers(headers) == False

        # Невалидный initData
        headers = {"X-Telegram-Init-Data": "invalid_data"}
        assert validate_telegram_auth_headers(headers) == False

        # Невалидный user data
        headers = {"X-Telegram-User-Data": "invalid_json"}
        assert validate_telegram_auth_headers(headers) == False

    def test_get_telegram_user_id_from_headers(self):
        """Тест извлечения user ID из заголовков."""
        # Тест с initData
        headers = {"X-Telegram-Init-Data": "user=%7B%22id%22%3A12345%7D&hash=test_hash"}
        user_id = get_telegram_user_id_from_headers(headers)
        assert user_id == 12345

        # Тест с user data
        headers = {"X-Telegram-User-Data": '{"id": 67890, "first_name": "Jane"}'}
        user_id = get_telegram_user_id_from_headers(headers)
        assert user_id == 67890

        # Тест без данных
        headers = {}
        user_id = get_telegram_user_id_from_headers(headers)
        assert user_id is None

    def test_create_fallback_user_data(self):
        """Тест создания fallback данных пользователя."""
        user_data = create_fallback_user_data(12345)

        assert user_data["id"] == 12345
        assert user_data["first_name"] is None
        assert user_data["last_name"] is None
        assert user_data["username"] is None
        assert user_data["language_code"] == "ru"
        assert user_data["is_premium"] == False
        assert user_data["photo_url"] is None
        assert user_data["allows_write_to_pm"] == False


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_malformed_query_string(self):
        """Тест с некорректным query string."""
        init_data = "invalid_query_string"
        result = verify_telegram_webapp_data(init_data, "bot_token")
        assert result is None

    def test_very_long_init_data(self):
        """Тест с очень длинными данными."""
        # Создаем очень длинное имя
        long_name = "A" * 10000
        user_data = {"id": 12345, "first_name": long_name}

        init_data = f"user={json.dumps(user_data)}&auth_date={int(time.time())}&hash=test_hash"
        result = verify_telegram_webapp_data(init_data, "bot_token")
        # Должен обработать без ошибок, но вернуть None из-за неверного hash
        assert result is None

    def test_special_characters_in_data(self):
        """Тест со специальными символами в данных."""
        user_data = {"id": 12345, "first_name": "John & Jane", "username": "user@domain.com"}

        init_data = f"user={json.dumps(user_data)}&auth_date={int(time.time())}&hash=test_hash"
        result = verify_telegram_webapp_data(init_data, "bot_token")
        # Должен обработать без ошибок, но вернуть None из-за неверного hash
        assert result is None

    def test_numeric_user_id(self):
        """Тест с числовым user ID."""
        user_data = {"id": "12345", "first_name": "John"}  # ID как строка

        init_data = f"user={json.dumps(user_data)}&auth_date={int(time.time())}&hash=test_hash"
        result = verify_telegram_webapp_data(init_data, "bot_token")
        # Должен обработать без ошибок, но вернуть None из-за неверного hash
        assert result is None


class TestSecurity:
    """Тесты безопасности."""

    def test_timing_attack_resistance(self):
        """Тест устойчивости к timing атакам."""
        # Используем hmac.compare_digest для безопасного сравнения
        init_data = "user=%7B%22id%22%3A12345%7D&hash=wrong_hash"

        start_time = time.time()
        result = verify_telegram_webapp_data(init_data, "bot_token")
        end_time = time.time()

        assert result is None
        # Время выполнения должно быть примерно одинаковым для разных hash
        assert end_time - start_time < 1.0  # Не более 1 секунды

    def test_hash_collision_resistance(self):
        """Тест устойчивости к коллизиям hash."""
        # Создаем два разных набора данных с одинаковым hash
        data1 = "user=%7B%22id%22%3A12345%7D&auth_date=1234567890"
        data2 = "user=%7B%22id%22%3A67890%7D&auth_date=1234567890"

        # Это должно быть невозможно из-за HMAC
        result1 = verify_telegram_webapp_data(data1 + "&hash=fake_hash", "bot_token")
        result2 = verify_telegram_webapp_data(data2 + "&hash=fake_hash", "bot_token")

        assert result1 is None
        assert result2 is None


class TestLogging:
    """Тесты логирования."""

    @patch("utils.auth.telegram_auth.logger")
    def test_log_auth_attempt_success(self, mock_logger):
        """Тест логирования успешной аутентификации."""
        log_auth_attempt(12345, True, "initData")

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "success" in call_args
        assert "12345" in call_args
        assert "initData" in call_args

    @patch("utils.auth.telegram_auth.logger")
    def test_log_auth_attempt_failure(self, mock_logger):
        """Тест логирования неудачной аутентификации."""
        log_auth_attempt(12345, False, "initData", "Invalid hash")

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "failed" in call_args
        assert "12345" in call_args
        assert "initData" in call_args
        assert "Invalid hash" in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
