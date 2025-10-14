"""
Безопасная аутентификация Telegram WebApp пользователей.

Реализует проверку подлинности данных Telegram WebApp согласно
официальной документации с использованием HMAC SHA256.
"""

import hashlib
import hmac
import json
import logging
import time
from urllib.parse import parse_qsl
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


def get_user_uuid_by_telegram_id(telegram_id: int) -> Optional[str]:
    """
    Получить UUID пользователя по Telegram ID из базы данных.

    Args:
        telegram_id: Telegram ID пользователя

    Returns:
        UUID пользователя или None если не найден
    """
    try:
        from database.db_models import supabase

        if not supabase:
            logger.error("Supabase не инициализирован")
            return None

        result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()

        if result.data and len(result.data) > 0:
            user_uuid = result.data[0]["id"]
            logger.debug(f"Found user UUID {user_uuid} for telegram_id {telegram_id}")
            return user_uuid
        else:
            logger.warning(f"User not found for telegram_id {telegram_id}")
            return None

    except Exception as e:
        logger.error(f"Error getting user UUID for telegram_id {telegram_id}: {e}")
        return None


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> Optional[Dict[str, Any]]:
    """
    Проверяет подлинность данных Telegram WebApp.

    Алгоритм проверки согласно документации Telegram:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    Args:
        init_data: Строка initData от Telegram WebApp
        bot_token: Токен Telegram бота

    Returns:
        Dict с данными пользователя или None при ошибке аутентификации

    Raises:
        ValueError: При некорректных входных данных
    """
    if not init_data or not bot_token:
        logger.error("Missing required parameters: init_data or bot_token")
        return None

    try:
        # Парсим данные из query string
        parsed_data = dict(parse_qsl(init_data))

        # Извлекаем hash для проверки
        hash_value = parsed_data.pop("hash", None)
        if not hash_value:
            logger.error("Missing hash in init_data")
            return None

        # Проверяем auth_date (не старше 24 часов)
        auth_date_str = parsed_data.get("auth_date", "0")
        try:
            auth_date = int(auth_date_str)
        except ValueError:
            logger.error(f"Invalid auth_date format: {auth_date_str}")
            return None

        current_time = int(time.time())
        if current_time - auth_date > 86400:  # 24 часа
            logger.warning(f"Auth data expired: auth_date={auth_date}, current_time={current_time}")
            return None

        # Создаем data_check_string для проверки подписи
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = "\n".join(data_check_arr)

        # Вычисляем secret_key и hash
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Сравниваем вычисленный hash с полученным
        if not hmac.compare_digest(calculated_hash, hash_value):
            logger.debug("Hash mismatch - possible data tampering or corrupted initData")
            logger.debug(f"Expected: {calculated_hash}")
            logger.debug(f"Received: {hash_value}")
            logger.debug(f"Data check string: {data_check_string}")
            return None

        # Проверяем наличие обязательных полей
        if "user" not in parsed_data:
            logger.error("Missing 'user' field in init_data")
            return None

        # Парсим данные пользователя
        try:
            user_data = json.loads(parsed_data["user"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse user data: {e}")
            return None

        # Проверяем обязательные поля пользователя
        if not user_data.get("id"):
            logger.error("Missing user ID in user data")
            return None

        logger.debug(f"Successfully verified Telegram WebApp data for user {user_data.get('id')}")

        # Возвращаем все данные включая пользователя
        result = parsed_data.copy()
        result["user"] = user_data

        return result

    except Exception as e:
        logger.error(f"Error verifying Telegram WebApp data: {e}")
        return None


def extract_user_from_verified_data(verified_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Извлекает данные пользователя из проверенных данных Telegram.

    Args:
        verified_data: Данные, возвращенные verify_telegram_webapp_data()

    Returns:
        Dict с данными пользователя или None
    """
    if not verified_data or "user" not in verified_data:
        return None

    user_data = verified_data["user"]

    # Извлекаем основные поля пользователя
    return {
        "id": user_data.get("id"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "username": user_data.get("username"),
        "language_code": user_data.get("language_code"),
        "is_premium": user_data.get("is_premium", False),
        "photo_url": user_data.get("photo_url"),
        "allows_write_to_pm": user_data.get("allows_write_to_pm", False),
    }


def is_telegram_webapp_request(request_headers: Dict[str, str]) -> bool:
    """
    Проверяет, является ли запрос от Telegram WebApp.

    Args:
        request_headers: Заголовки HTTP запроса

    Returns:
        True если запрос от Telegram WebApp
    """
    # Проверяем наличие initData в заголовках
    init_data = request_headers.get("X-Telegram-Init-Data")
    if init_data:
        return True

    # Проверяем User-Agent на наличие Telegram
    user_agent = request_headers.get("User-Agent", "").lower()
    if "telegram" in user_agent:
        return True

    # Проверяем Referer на Telegram домены
    referer = request_headers.get("Referer", "").lower()
    telegram_domains = ["telegram.org", "web.telegram.org", "t.me"]
    if any(domain in referer for domain in telegram_domains):
        return True

    return False


def validate_telegram_auth_headers(request_headers: Dict[str, str]) -> bool:
    """
    Проверяет корректность заголовков Telegram аутентификации.

    Args:
        request_headers: Заголовки HTTP запроса

    Returns:
        True если заголовки корректны
    """
    # Проверяем наличие хотя бы одного из методов аутентификации
    init_data = request_headers.get("X-Telegram-Init-Data")
    user_data = request_headers.get("X-Telegram-User-Data")

    if not init_data and not user_data:
        logger.warning("No Telegram authentication headers found")
        return False

    # Если есть initData, проверяем его формат
    if init_data:
        try:
            parsed = dict(parse_qsl(init_data))
            if "hash" not in parsed or "user" not in parsed:
                logger.warning("Invalid initData format")
                return False
        except Exception as e:
            logger.warning(f"Failed to parse initData: {e}")
            return False

    # Если есть user data, проверяем его формат
    if user_data:
        try:
            json.loads(user_data)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid user data format: {e}")
            return False

    return True


def get_telegram_user_id_from_headers(request_headers: Dict[str, str]) -> Optional[int]:
    """
    Извлекает Telegram user ID из заголовков запроса.

    Args:
        request_headers: Заголовки HTTP запроса

    Returns:
        Telegram user ID или None
    """
    # Сначала пробуем извлечь из initData
    init_data = request_headers.get("X-Telegram-Init-Data")
    if init_data:
        try:
            parsed = dict(parse_qsl(init_data))
            user_data = json.loads(parsed.get("user", "{}"))
            user_id = user_data.get("id")
            if user_id:
                return int(user_id)
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Failed to extract user ID from initData: {e}")

    # Затем пробуем извлечь из user data
    user_data = request_headers.get("X-Telegram-User-Data")
    if user_data:
        try:
            user_info = json.loads(user_data)
            user_id = user_info.get("id")
            if user_id:
                return int(user_id)
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Failed to extract user ID from user data: {e}")

    return None


# Утилитарные функции для совместимости
def create_fallback_user_data(telegram_id: int) -> Dict[str, Any]:
    """
    Создает fallback данные пользователя для случаев, когда аутентификация недоступна.

    Args:
        telegram_id: Telegram user ID

    Returns:
        Dict с базовыми данными пользователя
    """
    return {
        "id": telegram_id,
        "first_name": None,
        "last_name": None,
        "username": None,
        "language_code": "ru",
        "is_premium": False,
        "photo_url": None,
        "allows_write_to_pm": False,
    }


def log_auth_attempt(telegram_id: int, success: bool, method: str, error: Optional[str] = None):
    """
    Логирует попытку аутентификации для мониторинга безопасности.

    Args:
        telegram_id: Telegram user ID
        success: Успешность аутентификации
        method: Метод аутентификации (initData, userData, fallback)
        error: Описание ошибки (если есть)
    """
    if success:
        logger.info(f"Telegram auth success: user_id={telegram_id}, method={method}")
    else:
        logger.warning(f"Telegram auth failed: user_id={telegram_id}, method={method}, error={error}")


def verify_telegram_auth(
    request_headers: Dict[str, str], session_data: Optional[Dict[str, Any]] = None, bot_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Унифицированная функция аутентификации с приоритизацией методов.

    Приоритет методов:
    1. HMAC SHA256 (X-Telegram-Init-Data) - высший приоритет
    2. Session (session['user_id']) - средний приоритет
    3. Fallback JSON (X-Telegram-User-Data) - низший приоритет

    Args:
        request_headers: Заголовки HTTP запроса
        session_data: Данные Flask session (опционально)
        bot_token: Токен Telegram бота для HMAC проверки (опционально)

    Returns:
        Dict с результатом аутентификации:
        {
            'success': bool,
            'user_id': str,
            'telegram_id': int,
            'method': str,
            'message': str
        }
    """
    # 1. ПРИОРИТЕТ 1: HMAC SHA256 аутентификация
    init_data = request_headers.get("X-Telegram-Init-Data")
    if init_data and bot_token:
        try:
            verified_data = verify_telegram_webapp_data(init_data, bot_token)
            if verified_data:
                user_data = extract_user_from_verified_data(verified_data)
                if user_data:
                    telegram_id = user_data["id"]
                    log_auth_attempt(telegram_id, True, "initData_HMAC")

                    # Получаем реальный UUID из базы данных
                    real_user_id = get_user_uuid_by_telegram_id(telegram_id)
                    if not real_user_id:
                        logger.error(f"User not found in database for telegram_id: {telegram_id}")
                        return {
                            "success": False,
                            "message": "User not found in database",
                        }

                    return {
                        "success": True,
                        "user_id": real_user_id,  # Реальный UUID из базы данных
                        "telegram_id": telegram_id,
                        "method": "initData_HMAC",
                        "message": "HMAC SHA256 authentication successful",
                    }
        except Exception as e:
            logger.debug(f"HMAC authentication failed (will try fallback): {e}")

    # 2. ПРИОРИТЕТ 2: Session аутентификация
    if session_data and session_data.get("user_id") and session_data.get("telegram_id"):
        telegram_id = session_data["telegram_id"]
        log_auth_attempt(telegram_id, True, "session")

        # Проверяем что session содержит UUID, а не Telegram ID
        session_user_id = session_data["user_id"]
        if len(session_user_id) > 10:  # UUID длиннее чем Telegram ID
            # Это уже UUID из предыдущей успешной аутентификации
            return {
                "success": True,
                "user_id": session_user_id,
                "telegram_id": telegram_id,
                "method": "session",
                "message": "Session authentication successful",
            }
        else:
            # Это Telegram ID, нужно получить UUID из базы
            real_user_id = get_user_uuid_by_telegram_id(telegram_id)
            if not real_user_id:
                logger.error(f"User not found in database for telegram_id: {telegram_id}")
                return {
                    "success": False,
                    "message": "User not found in database",
                }

            return {
                "success": True,
                "user_id": real_user_id,  # Реальный UUID из базы данных
                "telegram_id": telegram_id,
                "method": "session",
                "message": "Session authentication successful",
            }

    # 3. ПРИОРИТЕТ 3: Fallback JSON аутентификация
    user_data_header = request_headers.get("X-Telegram-User-Data")
    if user_data_header:
        try:
            user_info = json.loads(user_data_header)
            telegram_id = user_info.get("id")
            if telegram_id:
                log_auth_attempt(telegram_id, True, "userData_fallback")

                # Получаем реальный UUID из базы данных
                real_user_id = get_user_uuid_by_telegram_id(telegram_id)
                if not real_user_id:
                    logger.error(f"User not found in database for telegram_id: {telegram_id}")
                    return {
                        "success": False,
                        "message": "User not found in database",
                    }

                return {
                    "success": True,
                    "user_id": real_user_id,  # Реальный UUID из базы данных
                    "telegram_id": telegram_id,
                    "method": "userData_fallback",
                    "message": "Fallback JSON authentication successful",
                }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Fallback authentication failed: {e}")

    # Все методы аутентификации провалились
    log_auth_attempt(0, False, "none", "No valid authentication method found")
    return {
        "success": False,
        "user_id": None,
        "telegram_id": None,
        "method": "none",
        "message": "Authentication failed: no valid method found",
    }
