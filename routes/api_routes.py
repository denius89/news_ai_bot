"""
Module: routes.api_routes
Purpose: Main API endpoints for PulseAI WebApp
Location: routes/api_routes.py

Description:
    Flask Blueprint для основных API endpoints веб-приложения.
    Обрабатывает subscriptions, user management, categories, и webhooks.

    ⚠️ TODO: Добавить authentication, rate limiting, input validation

Key Endpoints:
    GET  /api/categories - Список доступных категорий новостей
    GET  /api/subscriptions - Подписки пользователя
    POST /api/subscriptions - Добавить подписку
    DELETE /api/subscriptions - Удалить подписку
    GET  /api/user - Информация о пользователе
    POST /api/feedback - Отправить feedback
    POST /api/telegram/webhook - Telegram WebApp webhook

Dependencies:
    External:
        - Flask: Web framework
        - database.db_models: Database operations (legacy)
    Internal:
        - digests.configs: Category configuration
        - utils.text.name_normalizer: Unicode name conversion

Usage Example:
    ```python
    # Получить категории
    GET /api/categories
    Response: {"categories": [...]}

    # Добавить подписку
    POST /api/subscriptions
    Body: {"user_id": "123", "category": "tech"}
    ```

Security Notes:
    ⚠️ CRITICAL: API endpoints не защищены!
    - Нет authentication
    - Нет rate limiting
    - Нет input validation
    - Нужно добавить в priority

Notes:
    - Categories централизованы в digests/configs.py
    - Использует legacy db_models (нужна миграция на service.py)
    - Unicode name conversion для Telegram имен
    - TODO: Добавить proper error handling

Author: PulseAI Team
Last Updated: October 2025
"""

import asyncio
import logging
import unicodedata

from flask import Blueprint, request, jsonify
from database.db_models import (
    list_notifications,
    get_user_notifications,
    mark_notification_read,
)
from database.service import get_sync_service
from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService
from services.categories import (
    get_category_structure,
    get_emoji_icon,
    validate_sources,
)


def convert_unicode_name(name):
    """Конвертирует Unicode стилизованные символы в обычные ASCII"""
    if not name:
        return name

    # Специальные случаи испорченных имен
    corruption_map = {
        'ÐÐ°Ð½': 'Иван',
        'ÐÐ°ÑÐ°': 'Маша',
        'ÐÐ»ÐµÐºÑÐµÐ¹': 'Алексей',
        # Дважды испорченные имена
        'Ã\x90Ã\x90Â°Ã\x90Â½': 'Иван',
        'ÃÐÃÐÂ°ÃÐÂ½': 'Иван',
    }

    if name in corruption_map:
        return corruption_map[name]

    # Проверяем на двойную кодировку UTF-8
    try:
        if 'Ð' in name and len(name) > 0:
            try:
                # Кодируем в latin-1, затем декодируем как UTF-8
                fixed = name.encode('latin-1').decode('utf-8')
                # Проверяем, что получили кириллицу
                if any('\u0400' <= c <= '\u04FF' for c in fixed):
                    return fixed
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
    except Exception:
        pass

    # Маппинг Unicode стилизованных символов на обычные
    unicode_map = {
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

    # Конвертируем символы
    result = ""
    for char in name:
        if char in unicode_map:
            result += unicode_map[char]
        else:
            # Пытаемся нормализовать символ
            normalized = unicodedata.normalize('NFKD', char)
            # Если после нормализации получили ASCII символ
            if len(normalized) == 1 and ord(normalized) < 128:
                result += normalized
            else:
                # Оставляем как есть, если не можем конвертировать
                result += char

    return result


logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Initialize services
subscription_service = SubscriptionService()
notification_service = NotificationService()


def convert_to_uuid(user_id_input):
    """Convert various user ID formats to UUID string."""
    if isinstance(user_id_input, str):
        # If it looks like a UUID, return as-is
        if len(user_id_input) == 36 and user_id_input.count("-") == 4:
            return user_id_input
        # For demo users, create a consistent UUID from the input
        import hashlib

        hash_obj = hashlib.md5(f"demo-{user_id_input}".encode())
        hex_dig = hash_obj.hexdigest()
        # Format as UUID
        uuid_str = f"{hex_dig[:8]}-{hex_dig[8:12]}-{hex_dig[12:16]}-{hex_dig[16:20]}-{hex_dig[20:32]}"
        return uuid_str
    else:
        # Assume it's already a UUID (for direct API calls)
        return user_id_input


# Convert to API format with descriptions
def get_subscription_categories():
    """Convert centralized categories to API format (legacy)"""
    category_descriptions = {
        "crypto": "Latest cryptocurrency news and market updates",
        "economy": "Economic analysis and financial market insights",
        "world": "Global news and international developments",
        "technology": "Technology innovations and industry updates",
        "politics": "Political news and government developments",
    }

    # Используем новую систему категорий
    from services.categories import get_categories

    categories = get_categories()

    return [
        {
            "id": category_id,
            "name": category_id.title(),
            "description": category_descriptions.get(category_id, f"News about {category_id.lower()}"),
        }
        for category_id in categories
    ]


SUBSCRIPTION_CATEGORIES = get_subscription_categories()


def run_async(coro):
    """Helper to run async functions in Flask context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


@api_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    """
    GET /api/subscriptions?user_id=<id>
    Returns user's subscription status for all categories.
    """
    user_id_input = request.args.get("user_id")
    if not user_id_input:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        # Convert to UUID if needed
        user_id = convert_to_uuid(user_id_input)

        # Get user's current subscriptions
        subscriptions = run_async(subscription_service.list(user_id))
        subscribed_categories = {sub["category"] for sub in subscriptions}

        # Build response with all categories and their status
        categories_with_status = []
        for category in SUBSCRIPTION_CATEGORIES:
            categories_with_status.append(
                {
                    "id": category["id"],
                    "name": category["name"],
                    "description": category["description"],
                    "subscribed": category["id"] in subscribed_categories,
                }
            )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "categories": categories_with_status,
                    "total_subscriptions": len(subscribed_categories),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching subscriptions for user %s: %s", user_id_input, e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route("/subscriptions/update", methods=["POST"])
def update_subscription():
    """
    POST /api/subscriptions/update
    Updates user's subscription status for a category.
    Body: {"user_id": "uuid", "category": "crypto", "enabled": true}
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    data = request.get_json()
    user_id = data.get("user_id")
    category = data.get("category")
    enabled = data.get("enabled")

    if not user_id or not category or enabled is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "user_id, category, and enabled are required",
                }
            ),
            400,
        )

    # Validate category
    valid_categories = [cat["id"] for cat in SUBSCRIPTION_CATEGORIES]
    if category not in valid_categories:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                }
            ),
            400,
        )

    try:
        # Convert to UUID if needed
        user_id = convert_to_uuid(user_id)

        if enabled:
            # For demo users, create user with a fake telegram_id
            demo_telegram_id = 999999999
            created_user_id = run_async(subscription_service.get_or_create_user(demo_telegram_id, "demo-user", "en"))

            # Add subscription using the created user_id
            success = run_async(subscription_service.add(created_user_id, category))
            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Successfully subscribed to {category}",
                        "data": {"category": category, "subscribed": True},
                    }
                )
            else:
                return jsonify({"status": "error", "message": "Failed to add subscription"}), 500
        else:
            # Remove subscription
            success = run_async(subscription_service.remove(user_id, category))
            if success:
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Successfully unsubscribed from {category}",
                        "data": {"category": category, "subscribed": False},
                    }
                )
            else:
                return jsonify({"status": "error", "message": "Failed to remove subscription"}), 500

    except Exception as e:
        logger.error("Error updating subscription: %s", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route("/user_notifications", methods=["GET"])
def get_user_notifications_api():
    """
    GET /api/user_notifications?user_id=<id>&limit=50&offset=0
    Returns list of user notifications.
    """
    user_id_input = request.args.get("user_id")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    if not user_id_input:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        # Convert user_id - try UUID format first, then fallback to int
        if len(user_id_input) == 36 and user_id_input.count("-") == 4:
            # It's a UUID
            user_id = user_id_input
            logger.info("Using UUID directly: %s", user_id)
        else:
            try:
                # Try to convert to int and then get UUID from users table
                telegram_id = int(user_id_input)
                logger.info("Converting telegram_id to UUID: %d", telegram_id)
                # Get UUID from users table
                db_service = get_sync_service()
                user_data = db_service.get_user_by_telegram(telegram_id)
                if user_data:
                    user_id = user_data["id"]
                    logger.info("Found user data: %s", user_data)
                else:
                    # Use first user as fallback
                    user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"  # First user from our check
                    logger.warning("User not found, using fallback: %s", user_id)
            except ValueError:
                # Use first user as fallback
                user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"
                logger.warning("Invalid user_id format, using fallback: %s", user_id)

        logger.info("Final user_id for query: %s", user_id)

        # Get notifications from database
        logger.info("Calling get_user_notifications with user_id=%s, limit=%d", user_id, limit)
        notifications = get_user_notifications(user_id=user_id, limit=limit, offset=offset)
        logger.info("get_user_notifications returned %d notifications", len(notifications))

        logger.info(
            "Retrieved %d notifications for user %s (original input: %s)",
            len(notifications),
            user_id,
            user_id_input,
        )

        # Transform notifications to match expected API format
        formatted_notifications = []
        for notification in notifications:
            formatted_notifications.append(
                {
                    "id": notification["id"],
                    "title": notification["title"],
                    # Use message field
                    "text": notification.get("message", notification.get("text", "")),
                    # Default timestamp
                    "created_at": notification.get("created_at", "2025-10-03T00:00:00Z"),
                    "read": notification["read"],
                }
            )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "notifications": formatted_notifications,
                    "total_count": len(formatted_notifications),
                    "limit": limit,
                    "offset": offset,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching notifications for user %s: %s", user_id_input, e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route("/notifications", methods=["GET"])
def get_notifications():
    """
    GET /api/notifications?user_id=<id>
    Returns list of notifications for user (legacy endpoint).
    """
    user_id_input = request.args.get("user_id")
    if not user_id_input:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        # Convert to UUID if needed
        user_id = convert_to_uuid(user_id_input)

        # Get notifications from database
        notifications = list_notifications(user_id)

        # Format response
        unread_count = sum(1 for n in notifications if not n.get("read", False))
        total_count = len(notifications)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "notifications": notifications,
                    "total_count": total_count,
                    "unread_count": unread_count,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching notifications for user %s: %s", user_id_input, e)
        # Return empty list on error (graceful degradation)
        return jsonify(
            {
                "status": "success",
                "data": {
                    "notifications": [],
                    "total_count": 0,
                    "unread_count": 0,
                },
            }
        )


@api_bp.route("/user_notifications/mark_read", methods=["POST"])
def mark_user_notification_read():
    """
    POST /api/user_notifications/mark_read
    Marks a user notification as read.
    Body: {"notification_id": 1}
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    data = request.get_json()
    notification_id = data.get("notification_id")
    user_id_input = data.get("user_id", 1)  # Default to user 1 for demo

    if not notification_id:
        return jsonify({"status": "error", "message": "notification_id is required"}), 400

    try:
        # Convert user_id - try UUID format first, then fallback to int
        if len(str(user_id_input)) == 36 and str(user_id_input).count("-") == 4:
            # It's a UUID
            user_id = user_id_input
        else:
            try:
                # Try to convert to int and then get UUID from users table
                telegram_id = int(user_id_input)
                # Get UUID from users table
                db_service = get_sync_service()
                user_data = db_service.get_user_by_telegram(telegram_id)
                if user_data:
                    user_id = user_data["id"]
                else:
                    # Use first user as fallback
                    user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"
            except ValueError:
                # Use first user as fallback
                user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"

        # Mark notification as read
        success = mark_notification_read(user_id=user_id, notification_id=notification_id)

        if success:
            logger.info(
                "Notification marked as read: user_id=%s, notification_id=%s",
                user_id,
                notification_id,
            )
            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "success": True,
                        "notification_id": notification_id,
                    },
                }
            )
        else:
            logger.warning(
                "Failed to mark notification as read: user_id=%s, notification_id=%s",
                user_id,
                notification_id,
            )
            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "success": False,
                        "notification_id": notification_id,
                        "reason": "Notification not found or does not belong to user",
                    },
                }
            )

    except Exception as e:
        logger.error("Error marking notification as read: %s", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route("/notifications/mark-read", methods=["POST"])
def mark_notification_read_endpoint():
    """
    POST /api/notifications/mark-read
    Marks a notification as read (legacy endpoint).
    """
    return (
        jsonify({"status": "error", "message": "Use /api/user_notifications/mark_read instead"}),
        501,
    )


@api_bp.route("/notification-settings", methods=["GET"])
def get_notification_settings():
    """
    GET /api/notification-settings?user_id=<id>
    Returns user's notification settings for all categories.
    TODO: Implement get_notification_settings function in db_models
    """
    return jsonify({"status": "error", "message": "Not implemented yet"}), 501


@api_bp.route("/notification-settings/update", methods=["POST"])
def update_notification_settings():
    """
    POST /api/notification-settings/update
    Updates user's notification settings.
    TODO: Implement upsert_notification_setting function in db_models
    """
    return jsonify({"status": "error", "message": "Not implemented yet"}), 501


@api_bp.route("/users", methods=["POST"])
def create_user():
    """
    POST /api/users
    Creates a new user or returns existing user.
    Body: {"telegram_id": 123456789, "username": "optional"}
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    data = request.get_json()
    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if not telegram_id:
        return jsonify({"status": "error", "message": "telegram_id is required"}), 400

    try:
        # Create or get user
        user_id = run_async(subscription_service.get_or_create_user(telegram_id, username))

        return jsonify(
            {
                "status": "success",
                "message": "User created or retrieved successfully",
                "data": {
                    "user_id": user_id,
                    "telegram_id": telegram_id,
                    "username": username,
                },
            }
        )

    except Exception as e:
        logger.error("Error creating user: %s", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """GET /api/health - Health check endpoint with digest v2 status"""
    try:
        from database.db_models import get_daily_digest_analytics

        # Get digest analytics for today
        analytics = get_daily_digest_analytics()
        avg_confidence = analytics.get("avg_confidence", 0.0)

        # Determine digest v2 status
        if avg_confidence >= 0.7:
            digest_v2_status = "ok"
        elif avg_confidence >= 0.5:
            digest_v2_status = "warning"
        else:
            digest_v2_status = "error"

        return jsonify({
            "status": "success",
            "message": "PulseAI API is healthy",
            "version": "1.0.0",
            "digest_v2_status": digest_v2_status,
            "avg_confidence": round(avg_confidence, 3),
            "generated_today": analytics.get("generated_count", 0)
        })

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "error",
            "message": "Health check failed",
            "digest_v2_status": "error",
            "error": str(e)
        }), 500


@api_bp.route("/categories", methods=["GET"])
def get_categories_api():
    """
    API endpoint для получения полной структуры категорий с иконками.

    Returns:
        JSON с категориями, подкатегориями и их иконками
    """
    try:
        structure = get_category_structure()

        # Преобразуем в формат для WebApp
        categories_data = {}
        for category, subcategories in structure.items():
            categories_data[category] = {
                "name": category.title(),
                "icon": get_emoji_icon(category, ""),
                "emoji": get_emoji_icon(category, ""),  # Добавляем emoji для удобства
                "subcategories": {},
            }

            for subcategory, data in subcategories.items():
                categories_data[category]["subcategories"][subcategory] = {
                    "name": subcategory.title(),
                    "icon": data.get("icon", ""),
                    "emoji": get_emoji_icon(category, subcategory),
                    "sources_count": len(data.get("sources", [])),
                }

        return jsonify(
            {
                "status": "success",
                "data": categories_data,
                "total_categories": len(categories_data),
                "total_subcategories": sum(len(cat["subcategories"]) for cat in categories_data.values()),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        return jsonify({"status": "error", "message": "Ошибка получения категорий"}), 500


@api_bp.route("/categories/validate", methods=["GET"])
def validate_categories_api():
    """
    API endpoint для валидации структуры категорий.

    Returns:
        JSON с результатами валидации
    """
    try:
        is_valid, errors = validate_sources()

        return jsonify(
            {
                "status": "success",
                "valid": is_valid,
                "errors": errors,
                "message": "Валидация завершена" if is_valid else "Найдены ошибки в структуре",
            }
        )

    except Exception as e:
        logger.error(f"Ошибка валидации категорий: {e}")
        return jsonify({"status": "error", "message": "Ошибка валидации категорий"}), 500


# Events endpoint moved to routes/events_routes.py


# --- Digest API Endpoints ---
@api_bp.route("/digests/styles", methods=["GET"])
def get_digest_styles():
    """Get available digest styles v2."""
    try:
        from digests.prompts_v2 import STYLE_CARDS

        # Extract styles and descriptions from v2
        styles = {}
        descriptions = {}

        for key, style_card in STYLE_CARDS.items():
            styles[key] = style_card["name"]
            descriptions[key] = style_card["description"]

        return jsonify(
            {
                "status": "success",
                "data": {
                    "styles": styles,
                    "descriptions": descriptions,
                },
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения стилей дайджеста v2: {e}")
        return jsonify({"status": "error", "message": "Ошибка получения стилей"}), 500


@api_bp.route("/digests/categories", methods=["GET"])
def get_digest_categories():
    """Get available digest categories."""
    try:
        from services.categories import get_categories

        # Get real categories from sources.yaml
        real_categories = get_categories()

        # Map to display names without emojis (clean for WebApp)
        category_display = {
            "crypto": "Криптовалюты",
            "sports": "Спорт",
            "markets": "Рынки",
            "tech": "Технологии",
            "world": "Мир",
        }

        # Build categories dict
        categories_dict = {}
        for cat in real_categories:
            categories_dict[cat] = category_display.get(cat, cat.title())

        return jsonify(
            {
                "status": "success",
                "data": {
                    "categories": categories_dict,
                    "periods": {"today": "Сегодня", "7d": "Последние 7 дней", "30d": "Последние 30 дней"},
                },
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения категорий дайджеста: {e}")
        return jsonify({"status": "error", "message": "Ошибка получения категорий"}), 500


@api_bp.route("/digests/generate", methods=["POST"])
def generate_digest():
    """Generate AI digest with specified parameters and save it for user."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    data = request.get_json()
    category = data.get("category", "all")
    style = data.get("style", "analytical")
    period = data.get("period", "today")
    limit = data.get("limit", 10)
    length = data.get("length", "medium")  # Новый параметр длины текста
    user_id = data.get("user_id")  # Новый параметр для привязки к пользователю
    save_digest = data.get("save", True)  # По умолчанию сохраняем

    # ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ
    logger.info("🔍 DIGEST GENERATION REQUEST:")
    logger.info(f"  - category: {category}")
    logger.info(f"  - style: {style}")
    logger.info(f"  - period: {period}")
    logger.info(f"  - limit: {limit}")
    logger.info(f"  - length: {length}")
    logger.info(f"  - user_id: {user_id}")
    logger.info(f"  - save_digest: {save_digest}")
    logger.info(f"  - Full data: {data}")

    # НОВЫЕ ПАРАМЕТРЫ ДЛЯ УМНОЙ ФИЛЬТРАЦИИ
    min_importance = data.get("min_importance", None)  # Минимальная важность новостей
    enable_smart_filtering = data.get("enable_smart_filtering", True)  # Включить умную фильтрацию
    use_user_preferences = data.get("use_user_preferences", True)  # Использовать предпочтения пользователя

    try:
        from services.unified_digest_service import get_async_digest_service
        from digests.prompts_v2 import STYLE_CARDS, LENGTH_SPECS
        from services.categories import get_categories

        # ИМПОРТЫ ДЛЯ НОВОЙ ФУНКЦИОНАЛЬНОСТИ
        from database.db_models import (
            get_user_preferences,
            save_user_preferences,
            log_digest_generation,
            get_smart_filter_for_time
        )
        import time

        # Get real categories
        real_categories = get_categories()

        # Validate parameters
        if style not in STYLE_CARDS:
            return jsonify({"status": "error", "message": f"Invalid style: {style}"}), 400

        if length not in LENGTH_SPECS:
            return jsonify({"status": "error", "message": f"Invalid length: {length}"}), 400

        if category != "all" and category not in real_categories:
            return jsonify({"status": "error", "message": f"Invalid category: {category}"}), 400

        # УМНАЯ ФИЛЬТРАЦИЯ: Получаем предпочтения пользователя
        user_preferences = None
        if user_id and use_user_preferences:
            try:
                user_preferences = get_user_preferences(user_id)
                logger.debug(f"Получены предпочтения пользователя {user_id}: {user_preferences}")
            except Exception as e:
                logger.warning(f"Не удалось получить предпочтения пользователя {user_id}: {e}")

        # УМНАЯ ФИЛЬТРАЦИЯ: Определяем параметры фильтрации
        final_min_importance = min_importance
        if enable_smart_filtering and user_preferences:
            # Используем предпочтения пользователя
            if user_preferences.get("enable_smart_filtering", True):
                final_min_importance = user_preferences.get("min_importance", 0.3)
                logger.debug(f"Применена умная фильтрация из предпочтений: min_importance={final_min_importance}")
        elif enable_smart_filtering:
            # Используем умный фильтр по времени
            try:
                smart_filter = get_smart_filter_for_time()
                final_min_importance = smart_filter.get("min_importance", 0.3)
                logger.debug(f"Применен умный фильтр по времени: min_importance={final_min_importance}")
            except Exception as e:
                logger.warning(f"Не удалось получить умный фильтр: {e}")

        # Generate digest using async service
        categories_list = None if category == "all" else [category]
        digest_service = get_async_digest_service()

        # ИЗМЕРЯЕМ ВРЕМЯ ГЕНЕРАЦИИ ДЛЯ АНАЛИТИКИ
        start_time = time.time()

        # Use async method to generate AI digest with smart filtering
        digest_text = run_async(
            digest_service.async_build_ai_digest(
                limit=limit,
                categories=categories_list,
                style=style,
                length=length,  # Передаем параметр длины текста
                min_importance=final_min_importance  # Передаем параметр фильтрации
            )
        )

        # ВРЕМЯ ГЕНЕРАЦИИ ДЛЯ АНАЛИТИКИ
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Category display mapping
        category_display = {
            "crypto": "₿ Криптовалюты",
            "sports": "⚽ Спорт",
            "markets": "📈 Рынки",
            "tech": "🤖 Технологии",
            "world": "🌍 Мир",
        }

        # Save digest to database if user_id provided and save_digest is True
        digest_id = None
        if user_id and save_digest:
            try:
                # user_id уже является UUID строкой, не нужно искать пользователя
                db_service = get_sync_service()
                digest_id = db_service.save_digest({
                    "user_id": str(user_id),
                    "summary": digest_text,
                    "category": category,
                    "style": style,
                    "period": period,
                    "limit_count": limit,
                    "metadata": {
                        "generation_time_ms": generation_time_ms,
                        "news_count": digest_text.count('\n') if digest_text else 0,
                        "min_importance": final_min_importance,
                        "smart_filtering": enable_smart_filtering,
                        "user_preferences_used": use_user_preferences
                    }
                })
                logger.info(f"Дайджест сохранен для пользователя {user_id}: {digest_id}")
            except Exception as save_error:
                logger.warning(f"Не удалось сохранить дайджест: {save_error}")
                # Продолжаем выполнение даже если сохранение не удалось

        # СОХРАНЯЕМ ПРЕДПОЧТЕНИЯ ПОЛЬЗОВАТЕЛЯ
        if user_id and use_user_preferences:
            try:
                save_user_preferences(
                    user_id=str(user_id),
                    preferred_category=category,
                    preferred_style=style,
                    preferred_period=period,
                    min_importance=final_min_importance or 0.3,
                    enable_smart_filtering=enable_smart_filtering
                )
                logger.debug(f"Предпочтения пользователя {user_id} обновлены")
            except Exception as pref_error:
                logger.warning(f"Не удалось сохранить предпочтения пользователя {user_id}: {pref_error}")

        # ЛОГИРУЕМ АНАЛИТИКУ ГЕНЕРАЦИИ
        if user_id:
            try:
                # Подсчитываем количество новостей в дайджесте (примерно)
                news_count = digest_text.count('\n') if digest_text else 0

                log_digest_generation(
                    user_id=str(user_id),
                    category=category,
                    style=style,
                    period=period,
                    min_importance=final_min_importance,
                    generation_time_ms=generation_time_ms,
                    success=True,
                    news_count=news_count
                )
                logger.debug(f"Аналитика генерации дайджеста залогирована для пользователя {user_id}")
            except Exception as analytics_error:
                logger.warning(f"Не удалось залогировать аналитику для пользователя {user_id}: {analytics_error}")

        return jsonify(
            {
                "status": "success",
                "data": {
                    "digest": digest_text,
                    "digest_id": digest_id,
                    "saved": bool(digest_id),
                    "metadata": {
                        "category": category,
                        "style": style,
                        "period": period,
                        "limit": limit,
                        "style_name": STYLE_CARDS.get(style, {}).get("name", style),
                        "category_name": (
                            category_display.get(category, "Все категории") if category != "all" else "Все категории"
                        ),
                        "min_importance": final_min_importance,  # Информация о фильтрации
                        "smart_filtering_enabled": enable_smart_filtering,
                        "generation_time_ms": generation_time_ms,  # Время генерации
                        "user_preferences_applied": bool(user_preferences),  # Применены ли предпочтения
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"Ошибка генерации дайджеста: {e}")
        return jsonify({"status": "error", "message": f"Ошибка генерации: {str(e)}"}), 500


@api_bp.route("/digests/history", methods=["GET"])
def get_digest_history():
    """Get user's digest history with soft delete support."""
    from flask import g

    # Получаем данные пользователя из middleware аутентификации
    if not hasattr(g, 'current_user') or not g.current_user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    user_id = g.current_user['user_id']
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    # Параметры пока не используются; зарезервированы для будущих фильтров
    # include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    # include_archived = request.args.get("include_archived", "false").lower() == "true"

    logger.info(f"🔍 Getting digest history for user {user_id} (method: {g.current_user['method']})")

    try:
        # Convert telegram_id to UUID if needed
        if user_id.isdigit() and len(user_id) < 10:
            # user_id is telegram_id, convert to UUID
            db_service = get_sync_service()
            user_data = db_service.get_user_by_telegram(int(user_id))
            if not user_data:
                return jsonify({"status": "error", "message": "User not found"}), 404
            user_uuid = user_data['id']
        else:
            # user_id is already UUID
            user_uuid = user_id

        # Get user's digest history with soft delete support
        db_service = get_sync_service()
        digests = db_service.get_user_digests(str(user_uuid), limit=limit)

        # Format digests for response (updated for new schema after migration)
        formatted_digests = []
        for digest in digests:
            formatted_digest = {
                "id": digest.get("id"),
                "user_id": digest.get("user_id"),  # Добавляем user_id
                "summary": digest.get("summary"),
                "category": digest.get("category"),
                "style": digest.get("style"),
                "period": digest.get("period"),
                "limit_count": digest.get("limit_count"),
                "created_at": digest.get("created_at"),
                "preview": (
                    digest.get("summary")[:200] + "..."
                    if len(digest.get("summary", "")) > 200
                    else digest.get("summary")
                ),
                "deleted_at": digest.get("deleted_at"),
                "archived": digest.get("archived"),
                "metadata": digest.get("metadata"),
                "feedback_score": digest.get("feedback_score"),  # Добавляем поле отзыва
                "feedback_count": digest.get("feedback_count"),  # Опционально для статистики
            }
            formatted_digests.append(formatted_digest)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "digests": formatted_digests,
                    "total": len(formatted_digests),
                    "limit": limit,
                    "offset": offset,
                },
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения истории дайджестов: {e}")
        return jsonify({"status": "error", "message": f"Ошибка получения истории: {str(e)}"}), 500


@api_bp.route("/digests/<digest_id>", methods=["GET"])
def get_digest_by_id(digest_id):
    """Get specific digest by ID."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import get_digest_by_id as db_get_digest_by_id, get_user_by_telegram

        # Convert telegram_id to UUID if needed
        if user_id.isdigit() and len(user_id) < 10:
            # user_id is telegram_id, convert to UUID
            user_data = get_user_by_telegram(int(user_id))
            if not user_data:
                return jsonify({"status": "error", "message": "User not found"}), 404
            user_uuid = user_data['id']
        else:
            # user_id is already UUID
            user_uuid = user_id

        # Get digest by ID
        digest = db_get_digest_by_id(digest_id=str(digest_id), user_id=str(user_uuid))

        if not digest:
            return jsonify({"status": "error", "message": "Digest not found"}), 404

        # Parse metadata from summary (temporary solution until migration)
        summary = digest.get("summary", "")
        if summary.startswith("[") and "]" in summary:
            metadata_part = summary.split("]", 1)[0] + "]"
            clean_summary = summary.split("]", 1)[1].strip()

            # Parse metadata
            try:
                metadata = metadata_part[1:-1].split("|")
                if len(metadata) >= 4:
                    category, style, period, limit_count = metadata[:4]
                else:
                    category, style, period, limit_count = "all", "analytical", "today", "10"
            except Exception:
                category, style, period, limit_count = "all", "analytical", "today", "10"
        else:
            clean_summary = summary
            category, style, period, limit_count = "all", "analytical", "today", "10"

        formatted_digest = {
            "id": digest.get("id"),
            "summary": clean_summary,
            "category": category,
            "style": style,
            "period": period,
            "limit": int(limit_count) if limit_count.isdigit() else 10,
            "created_at": digest.get("created_at"),
            "user_id": digest.get("user_id"),
        }

        return jsonify({"status": "success", "data": formatted_digest})

    except Exception as e:
        logger.error(f"Ошибка получения дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка получения дайджеста: {str(e)}"}), 500


@api_bp.route("/digests/<digest_id>", methods=["DELETE"])
def soft_delete_digest(digest_id):
    """Soft delete specific digest by ID."""
    user_id = request.args.get("user_id")
    permanent = request.args.get("permanent", "false").lower() == "true"

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import (
            soft_delete_digest as db_soft_delete_digest,
            permanent_delete_digest as db_permanent_delete_digest,
        )

        # Convert telegram_id to UUID if needed
        user_uuid = convert_user_id_to_uuid(user_id)
        if not user_uuid:
            return jsonify({"status": "error", "message": "User not found"}), 404

        if permanent:
            # Окончательное удаление
            success = db_permanent_delete_digest(digest_id=str(digest_id), user_id=str(user_uuid))
            message = "Digest permanently deleted"
        else:
            # Мягкое удаление
            success = db_soft_delete_digest(digest_id=str(digest_id), user_id=str(user_uuid))
            message = "Digest moved to trash"

        if success:
            return jsonify({"status": "success", "message": message, "deleted": True})
        else:
            return jsonify({"status": "error", "message": "Digest not found or access denied"}), 404

    except Exception as e:
        logger.error(f"Ошибка удаления дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка удаления дайджеста: {str(e)}"}), 500


@api_bp.route("/digests/<digest_id>/restore", methods=["POST"])
def restore_digest(digest_id):
    """Restore soft deleted digest."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import restore_digest as db_restore_digest

        # Convert telegram_id to UUID if needed
        user_uuid = convert_user_id_to_uuid(user_id)
        if not user_uuid:
            return jsonify({"status": "error", "message": "User not found"}), 404

        success = db_restore_digest(digest_id=str(digest_id), user_id=str(user_uuid))

        if success:
            return jsonify({"status": "success", "message": "Digest restored successfully", "restored": True})
        else:
            return jsonify({"status": "error", "message": "Digest not found, not deleted, or access denied"}), 404

    except Exception as e:
        logger.error(f"Ошибка восстановления дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка восстановления дайджеста: {str(e)}"}), 500


@api_bp.route("/digests/<digest_id>/archive", methods=["POST"])
def archive_digest(digest_id):
    """Archive digest."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import archive_digest as db_archive_digest

        # Convert telegram_id to UUID if needed
        user_uuid = convert_user_id_to_uuid(user_id)
        if not user_uuid:
            return jsonify({"status": "error", "message": "User not found"}), 404

        success = db_archive_digest(digest_id=str(digest_id), user_id=str(user_uuid))

        if success:
            return jsonify({"status": "success", "message": "Digest archived successfully", "archived": True})
        else:
            return jsonify({"status": "error", "message": "Digest not found, already archived, or access denied"}), 404

    except Exception as e:
        logger.error(f"Ошибка архивирования дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка архивирования дайджеста: {str(e)}"}), 500


@api_bp.route("/digests/<digest_id>/unarchive", methods=["POST"])
def unarchive_digest(digest_id):
    """Unarchive digest."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import unarchive_digest as db_unarchive_digest

        # Convert telegram_id to UUID if needed
        user_uuid = convert_user_id_to_uuid(user_id)
        if not user_uuid:
            return jsonify({"status": "error", "message": "User not found"}), 404

        success = db_unarchive_digest(digest_id=str(digest_id), user_id=str(user_uuid))

        if success:
            return jsonify({"status": "success", "message": "Digest unarchived successfully", "unarchived": True})
        else:
            return jsonify({"status": "error", "message": "Digest not found, not archived, or access denied"}), 404

    except Exception as e:
        logger.error(f"Ошибка разархивирования дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка разархивирования дайджеста: {str(e)}"}), 500


@api_bp.route("/users/by-telegram-id/<int:telegram_id>", methods=["GET"])
def get_user_by_telegram_id(telegram_id):
    """Get user_id by telegram_id for Telegram WebApp integration (public endpoint)."""
    try:
        logger.info(f"🔍 API request for telegram_id: {telegram_id}")

        # Импортируем модули
        from utils.text.name_normalizer import normalize_user_name
        from database.db_models import supabase

        logger.info(f"🔍 Supabase connection check: {supabase is not None}")
        if not supabase:
            logger.error("❌ Supabase not initialized!")
            return jsonify({"status": "error", "message": "Database not initialized"}), 500

        # Получаем данные пользователя из заголовков (опционально)
        tg_user_data = request.headers.get('X-Telegram-User-Data')
        tg_user = None
        if tg_user_data:
            import json
            try:
                tg_user = json.loads(tg_user_data)
                logger.info(f"⚠️ Using userData for user {telegram_id}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse userData: {e}")

        # Ищем пользователя по telegram_id с retry логикой
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"🔍 Database query attempt {attempt + 1} for telegram_id: {telegram_id}")
                result = supabase.table("users").select("id, username, locale, first_name").eq("telegram_id", telegram_id).execute()
                logger.info(f"✅ Database query successful on attempt {attempt + 1}")
                break
            except Exception as db_error:
                logger.error(f"❌ Database error attempt {attempt + 1}: {db_error}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ All {max_retries} attempts failed")
                    return jsonify({"status": "error", "message": f"Database connection error: {str(db_error)}"}), 500
                else:
                    import time
                    time.sleep(0.5)  # Небольшая пауза перед retry

        if result.data:
            user_data = result.data[0]
            logger.info(f"User found by telegram_id {telegram_id}: {user_data['id']}")
            logger.info(f"🔍 User data: first_name='{user_data.get('first_name')}', username='{user_data.get('username')}'")

            # Обновляем данные пользователя с нормализацией имён
            needs_update = False
            new_first_name = user_data.get('first_name')
            new_username = user_data.get('username')

            if tg_user and tg_user.get('first_name'):
                if not user_data.get('first_name'):
                    # Нормализуем имя пользователя
                    raw_first_name = tg_user.get('first_name')
                    new_first_name = normalize_user_name(
                        raw_name=raw_first_name,
                        username=tg_user.get('username'),
                        user_id=telegram_id
                    )
                    needs_update = True
                    logger.info(f"Will update first_name for user {user_data['id']}: {raw_first_name} -> {new_first_name}")

            if tg_user and tg_user.get('username'):
                if not user_data.get('username'):
                    new_username = tg_user.get('username')
                    needs_update = True
                    logger.info(f"Will update username for user {user_data['id']}: {tg_user.get('username')}")

            if needs_update:
                try:
                    from database.db_models import upsert_user_by_telegram
                    upsert_user_by_telegram(
                        telegram_id=telegram_id,
                        username=new_username,
                        locale=user_data.get('locale', 'ru'),
                        first_name=new_first_name
                    )
                    # Обновляем данные в ответе
                    user_data['first_name'] = new_first_name
                    user_data['username'] = new_username
                    logger.info(f"Updated user data for {user_data['id']}: first_name={new_first_name}, username={new_username}")
                except Exception as update_error:
                    logger.error(f"Failed to update user data for {user_data['id']}: {update_error}")

            # Детальное логирование ответа
            response_data = {
                "status": "success",
                "data": {
                    "user_id": user_data["id"],
                    "telegram_id": telegram_id,
                    "username": user_data.get("username"),
                    "locale": user_data.get("locale", "ru"),
                    "first_name": user_data.get("first_name"),
                },
            }

            logger.info(f"🔍 Response data: {response_data}")
            logger.info(f"🔍 Response data type: {type(response_data)}")

            # Проверяем JSON сериализацию
            try:
                import json
                json_str = json.dumps(response_data, ensure_ascii=False)
                logger.info(f"✅ JSON serialization successful, length: {len(json_str)}")
            except Exception as e:
                logger.error(f"❌ JSON serialization error: {e}")
                return jsonify({"status": "error", "message": f"JSON serialization error: {str(e)}"}), 500

            response = jsonify(response_data)
            # Отключаем кэширование для API пользователя
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            logger.info(f"User not found by telegram_id: {telegram_id}, creating new user")
            logger.info(f"🔍 Creating new user for telegram_id: {telegram_id}")

            # Создаем нового пользователя с нормализацией имён
            try:
                from database.db_models import create_user

                # Используем уже полученные данные пользователя из аутентификации
                if not tg_user:
                    logger.warning("⚠️ No user data available for new user creation")
                    # Создаем пользователя с минимальными данными
                    normalized_name = normalize_user_name(None, None, telegram_id)
                    new_user_id = create_user(
                        telegram_id=telegram_id,
                        username=None,
                        locale='ru',
                        first_name=normalized_name
                    )
                else:
                    # Нормализуем имя пользователя
                    raw_first_name = tg_user.get('first_name')
                    normalized_name = normalize_user_name(
                        raw_name=raw_first_name,
                        username=tg_user.get('username'),
                        user_id=telegram_id
                    )

                    logger.info(f"🔧 Creating user with normalized name: {repr(raw_first_name)} -> {repr(normalized_name)}")

                    new_user_id = create_user(
                        telegram_id=telegram_id,
                        username=tg_user.get('username'),
                        locale=tg_user.get('language_code', 'ru'),
                        first_name=normalized_name
                    )

                if new_user_id:
                    logger.info(f"New user created: {new_user_id} for telegram_id: {telegram_id}")

                    return jsonify(
                        {
                            "status": "success",
                            "data": {
                                "user_id": new_user_id,
                                "telegram_id": telegram_id,
                                "username": tg_user.get('username') if tg_user else None,
                                "locale": tg_user.get('language_code', 'ru') if tg_user else 'ru',
                                "first_name": normalized_name,
                            },
                        }
                    )
                else:
                    logger.error(f"Failed to create user for telegram_id: {telegram_id}")
                    return jsonify({"status": "error", "message": "Failed to create user"}), 500

            except Exception as create_error:
                logger.error(f"Error creating user for telegram_id {telegram_id}: {create_error}")
                return jsonify({"status": "error", "message": f"Failed to create user: {str(create_error)}"}), 500

    except Exception as e:
        logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500


@api_bp.route("/users/telegram-auth", methods=["POST"])
def telegram_auth():
    """Authenticate user via Telegram WebApp initData."""
    try:
        data = request.get_json()
        init_data = data.get("initData")

        if not init_data:
            return jsonify({"status": "error", "message": "initData is required"}), 400

        # Парсим initData для получения telegram_id
        # Формат: "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1234567890&hash=abc123"
        import urllib.parse

        parsed_data = urllib.parse.parse_qs(init_data)
        user_data_str = parsed_data.get("user", [None])[0]

        if not user_data_str:
            return jsonify({"status": "error", "message": "Invalid initData format"}), 400

        # Декодируем user данные
        user_data = urllib.parse.unquote(user_data_str)
        import json

        user_info = json.loads(user_data)
        telegram_id = user_info.get("id")

        if not telegram_id:
            return jsonify({"status": "error", "message": "Telegram ID not found in initData"}), 400

        # Ищем пользователя в базе данных
        from database.db_models import supabase

        if not supabase:
            return jsonify({"status": "error", "message": "Database not initialized"}), 500

        result = supabase.table("users").select("id, username, locale").eq("telegram_id", telegram_id).execute()

        if result.data:
            user_data = result.data[0]
            logger.info(f"Telegram auth successful for telegram_id {telegram_id}: {user_data['id']}")

            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "user_id": user_data["id"],
                        "telegram_id": telegram_id,
                        "username": user_data.get("username"),
                        "locale": user_data.get("locale", "ru"),
                        "telegram_user": user_info,
                    },
                }
            )
        else:
            logger.warning(f"Telegram auth failed - user not found: {telegram_id}")
            return jsonify({"status": "error", "message": "User not found", "code": "USER_NOT_FOUND"}), 404

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON in initData"}), 400
    except Exception as e:
        logger.error(f"Error in telegram auth: {e}")
        return jsonify({"status": "error", "message": f"Authentication error: {str(e)}"}), 500


# =============================================================================
# USER PREFERENCES API ENDPOINTS
# =============================================================================

@api_bp.route("/users/preferences", methods=["GET"])
def get_user_preferences():
    """Get user preferences."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import get_user_preferences

        preferences = get_user_preferences(user_id)

        return jsonify({
            "status": "success",
            "data": preferences
        })

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return jsonify({"status": "error", "message": f"Error getting preferences: {str(e)}"}), 500


@api_bp.route("/users/preferences", methods=["POST"])
def save_user_preferences():
    """Save user preferences."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    try:
        from database.db_models import save_user_preferences

        success = save_user_preferences(
            user_id=user_id,
            preferred_category=data.get("preferred_category", "all"),
            preferred_style=data.get("preferred_style", "analytical"),
            preferred_period=data.get("preferred_period", "today"),
            min_importance=data.get("min_importance", 0.3),
            enable_smart_filtering=data.get("enable_smart_filtering", True)
        )

        if success:
            return jsonify({
                "status": "success",
                "message": "Preferences saved successfully"
            })
        else:
            return jsonify({"status": "error", "message": "Failed to save preferences"}), 500

    except Exception as e:
        logger.error(f"Error saving user preferences: {e}")
        return jsonify({"status": "error", "message": f"Error saving preferences: {str(e)}"}), 500


# =============================================================================
# ANALYTICS API ENDPOINTS
# =============================================================================

@api_bp.route("/analytics/digest-stats", methods=["GET"])
def get_digest_analytics():
    """Get digest generation analytics."""
    user_id = request.args.get("user_id")  # Optional - если не указан, возвращает общую статистику
    days = int(request.args.get("days", 30))

    try:
        from database.db_models import get_digest_analytics

        analytics_data = get_digest_analytics(user_id=user_id, days=days)

        # Подсчитываем статистику
        total_generations = len(analytics_data)
        successful_generations = len([a for a in analytics_data if a.get("success", True)])
        avg_generation_time = sum([a.get("generation_time_ms", 0) for a in analytics_data]) / total_generations if total_generations > 0 else 0

        # Популярные комбинации
        category_stats = {}
        style_stats = {}

        for item in analytics_data:
            category = item.get("category", "unknown")
            style = item.get("style", "unknown")

            category_stats[category] = category_stats.get(category, 0) + 1
            style_stats[style] = style_stats.get(style, 0) + 1

        return jsonify({
            "status": "success",
            "data": {
                "total_generations": total_generations,
                "successful_generations": successful_generations,
                "success_rate": successful_generations / total_generations if total_generations > 0 else 0,
                "avg_generation_time_ms": avg_generation_time,
                "category_stats": category_stats,
                "style_stats": style_stats,
                "period_days": days,
                "user_id": user_id
            }
        })

    except Exception as e:
        logger.error(f"Error getting digest analytics: {e}")
        return jsonify({"status": "error", "message": f"Error getting analytics: {str(e)}"}), 500


# =============================================================================
# SMART FILTERING API ENDPOINTS
# =============================================================================

@api_bp.route("/smart-filters/current", methods=["GET"])
def get_current_smart_filter():
    """Get current smart filter based on time."""
    try:
        from database.db_models import get_smart_filter_for_time

        smart_filter = get_smart_filter_for_time()

        return jsonify({
            "status": "success",
            "data": smart_filter
        })

    except Exception as e:
        logger.error(f"Error getting smart filter: {e}")
        return jsonify({"status": "error", "message": f"Error getting smart filter: {str(e)}"}), 500


# =============================================================================
# FEEDBACK API ENDPOINTS
# =============================================================================

@api_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for digest.

    Request body:
        {
            "digest_id": "uuid",
            "score": 0.9  // 0.0-1.0
        }

    Returns:
        JSON with success/error status
    """
    try:
        data = request.get_json()
        digest_id = data.get('digest_id')
        score = data.get('score')  # 0.0 - 1.0

        if not digest_id or score is None:
            return jsonify({
                "status": "error",
                "message": "digest_id and score are required"
            }), 400

        if not 0.0 <= score <= 1.0:
            return jsonify({
                "status": "error",
                "message": "score must be between 0.0 and 1.0"
            }), 400

        # Update feedback
        from database.db_models import update_digest_feedback
        success = update_digest_feedback(digest_id, score)

        if success:
            # Update daily analytics
            # from database.db_models import update_daily_analytics
            # update_daily_analytics() - deprecated, using individual event logging

            return jsonify({
                "status": "success",
                "message": "Feedback saved"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Digest not found"
            }), 404

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def convert_user_id_to_uuid(user_id: str):
    """Convert telegram_id to UUID if needed."""
    if user_id.isdigit() and len(user_id) < 10:
        # user_id is telegram_id, convert to UUID
        from database.db_models import get_user_by_telegram
        user_data = get_user_by_telegram(int(user_id))
        if not user_data:
            return None
        return user_data['id']
    else:
        # user_id is already UUID
        return user_id


# ============================================================================
# Day 17: User Preferences & Notifications API
# ============================================================================

@api_bp.route("/user/preferences", methods=["GET"])
def get_user_notification_preferences():
    """
    Get user notification preferences.

    Returns user's notification settings including:
    - categories: List of interested categories
    - min_importance: Minimum importance threshold (0.0-1.0)
    - delivery_method: Notification delivery method (bot/webapp/all)
    - notification_frequency: Frequency (realtime/hourly/daily/weekly)
    - max_notifications_per_day: Maximum notifications per day
    """
    try:
        user_id = request.headers.get("X-Telegram-User-Id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 401

        from services.notification_service import get_notification_service
        service = get_notification_service()

        # Get preferences from database
        prefs = asyncio.run(service.get_user_preferences(int(user_id)))

        if not prefs:
            # Return defaults
            prefs = {
                "categories": [],
                "min_importance": 0.6,
                "delivery_method": "bot",
                "notification_frequency": "daily",
                "max_notifications_per_day": 3
            }

        return jsonify({"success": True, "data": prefs})

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/user/preferences", methods=["POST", "PUT"])
def update_user_preferences():
    """
    Update user notification preferences.

    Request body:
    {
        "categories": ["crypto", "markets"],
        "min_importance": 0.7,
        "delivery_method": "bot",
        "notification_frequency": "daily",
        "max_notifications_per_day": 3
    }
    """
    try:
        user_id = request.headers.get("X-Telegram-User-Id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 401

        data = request.json

        if not data:
            return jsonify({"success": False, "error": "Request body required"}), 400

        from services.notification_service import get_notification_service
        service = get_notification_service()

        # Update preferences
        success = asyncio.run(service.update_user_preferences(int(user_id), data))

        if success:
            # Get updated preferences
            prefs = asyncio.run(service.get_user_preferences(int(user_id)))
            return jsonify({"success": True, "data": prefs})
        else:
            return jsonify({"success": False, "error": "Failed to update preferences"}), 500

    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/user/notifications/test", methods=["POST"])
def test_notification():
    """
    Test notification delivery for user.

    Useful for testing notification system without waiting for real events.
    """
    try:
        user_id = request.headers.get("X-Telegram-User-Id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 401

        from services.notification_service import get_notification_service
        service = get_notification_service()

        # Prepare test digest
        digest = asyncio.run(service.prepare_daily_digest(int(user_id)))

        if digest.get('count', 0) > 0:
            # Send test notification
            events = digest.get('events', [])
            success = asyncio.run(service.send_telegram_notification(int(user_id), events))

            return jsonify({
                "success": True,
                "message": "Test notification sent" if success else "Notification rate limit reached",
                "events_count": len(events)
            })
        else:
            return jsonify({
                "success": True,
                "message": "No events matching your preferences",
                "events_count": 0
            })

    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


__all__ = ["api_bp"]
