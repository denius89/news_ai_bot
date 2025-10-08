"""
API Routes for PulseAI WebApp
Handles subscriptions and user data management

Categories are centralized in digests/configs.py and imported here
to maintain consistency across the application.
"""

import asyncio
import logging

from flask import Blueprint, request, jsonify

from database.db_models import list_notifications, get_user_notifications, mark_notification_read
from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService
from services.categories import get_category_structure, get_emoji_icon, validate_sources

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
                from database.db_models import get_user_by_telegram

                user_data = get_user_by_telegram(telegram_id)
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
                from database.db_models import get_user_by_telegram

                user_data = get_user_by_telegram(telegram_id)
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
    """GET /api/health - Health check endpoint"""
    return jsonify(
        {
            "status": "success",
            "message": "PulseAI API is healthy",
            "version": "1.0.0",
        }
    )


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


@api_bp.route("/events/upcoming", methods=["GET"])
def get_upcoming_events():
    """
    API endpoint для получения предстоящих событий для календаря.

    Query parameters:
        - days: количество дней вперед (по умолчанию 7)
        - category: фильтр по категории (опционально)
        - min_importance: минимальная важность (по умолчанию 0)

    Returns:
        JSON с событиями в формате для календаря
    """
    try:
        days = int(request.args.get("days", 7))
        category = request.args.get("category")
        min_importance = float(request.args.get("min_importance", 0))

        # Получаем события из базы данных
        from database.db_models import get_latest_events

        events = get_latest_events(limit=100)

        # Фильтруем по категории если указана
        if category:
            events = [e for e in events if e.get("category") == category]

        # Фильтруем по важности
        events = [e for e in events if (e.get("importance") or 0) >= min_importance]

        # Преобразуем в формат для календаря
        formatted_events = []
        for event in events:
            # Определяем категорию на основе источника или других данных
            # По умолчанию markets для экономических событий
            event_category = event.get("category", "markets")

            formatted_event = {
                "id": event.get("id", f"event_{hash(event.get('title', ''))}"),
                "title": event.get("title", "Без названия"),
                "starts_at": event.get("event_time", "2025-10-06T12:00:00Z"),
                "category": event_category,
                "importance": float(event.get("importance", 0)) / 3.0,  # Нормализуем 0-3 в 0-1
                "description": f"Источник: {event.get('source', 'Unknown')}",
                "country": event.get("country", ""),
                "currency": event.get("currency", ""),
                "fact": event.get("fact"),
                "forecast": event.get("forecast"),
                "previous": event.get("previous"),
                "link": None,  # Пока нет ссылок в базе
            }
            formatted_events.append(formatted_event)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "events": formatted_events,
                    "total_count": len(formatted_events),
                    "days": days,
                    "category": category,
                    "min_importance": min_importance,
                },
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения событий: {e}")
        return jsonify({"status": "error", "message": "Ошибка получения событий"}), 500


# --- Digest API Endpoints ---
@api_bp.route("/digests/styles", methods=["GET"])
def get_digest_styles():
    """Get available digest styles."""
    try:
        from digests.configs import STYLES

        return jsonify(
            {
                "status": "success",
                "data": {
                    "styles": STYLES,
                    "descriptions": {
                        "analytical": "Глубокий анализ с экспертной оценкой",
                        "business": "Деловой тон с фокусом на практические решения",
                        "meme": "Лёгкий стиль с юмором и мемами",
                    },
                },
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения стилей дайджеста: {e}")
        return jsonify({"status": "error", "message": "Ошибка получения стилей"}), 500


@api_bp.route("/digests/categories", methods=["GET"])
def get_digest_categories():
    """Get available digest categories."""
    try:
        from services.categories import get_categories

        # Get real categories from sources.yaml
        real_categories = get_categories()

        # Map to display names with icons
        category_display = {
            "crypto": "₿ Криптовалюты",
            "sports": "⚽ Спорт",
            "markets": "📈 Рынки",
            "tech": "🤖 Технологии",
            "world": "🌍 Мир",
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
                    "periods": {"today": "📅 Сегодня", "7d": "📅 Последние 7 дней", "30d": "📅 Последние 30 дней"},
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
    user_id = data.get("user_id")  # Новый параметр для привязки к пользователю
    save_digest = data.get("save", True)  # По умолчанию сохраняем

    try:
        from services.unified_digest_service import get_async_digest_service
        from digests.configs import STYLES
        from services.categories import get_categories
        from database.db_models import save_digest as db_save_digest

        # Get real categories
        real_categories = get_categories()

        # Validate parameters
        if style not in STYLES:
            return jsonify({"status": "error", "message": f"Invalid style: {style}"}), 400

        if category != "all" and category not in real_categories:
            return jsonify({"status": "error", "message": f"Invalid category: {category}"}), 400

        # Generate digest using async service
        categories_list = None if category == "all" else [category]
        digest_service = get_async_digest_service()

        # Use async method to generate AI digest
        digest_text = run_async(
            digest_service.async_build_ai_digest(limit=limit, categories=categories_list, style=style)
        )

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
                digest_id = db_save_digest(
                    user_id=str(user_id),
                    summary=digest_text,
                    category=category,
                    style=style,
                    period=period,
                    limit_count=limit,
                    metadata={
                        "api_generated": True,
                        "category_name": (
                            category_display.get(category, "Все категории") if category != "all" else "Все категории"
                        ),
                        "style_name": STYLES.get(style, style),
                    },
                )
                logger.info(f"Дайджест сохранен для пользователя {user_id}: {digest_id}")
            except Exception as save_error:
                logger.warning(f"Не удалось сохранить дайджест: {save_error}")
                # Продолжаем выполнение даже если сохранение не удалось

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
                        "style_name": STYLES.get(style, style),
                        "category_name": (
                            category_display.get(category, "Все категории") if category != "all" else "Все категории"
                        ),
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
    user_id = request.args.get("user_id")
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    include_archived = request.args.get("include_archived", "false").lower() == "true"

    if not user_id:
        return jsonify({"status": "error", "message": "user_id parameter is required"}), 400

    try:
        from database.db_models import get_user_digests

        # Get user's digest history with soft delete support
        digests = get_user_digests(
            user_id=str(user_id),
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            include_archived=include_archived,
        )

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
        from database.db_models import get_digest_by_id as db_get_digest_by_id

        # Get digest by ID
        digest = db_get_digest_by_id(digest_id=str(digest_id), user_id=str(user_id))

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
            except:
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

        if permanent:
            # Окончательное удаление
            success = db_permanent_delete_digest(digest_id=str(digest_id), user_id=str(user_id))
            message = "Digest permanently deleted"
        else:
            # Мягкое удаление
            success = db_soft_delete_digest(digest_id=str(digest_id), user_id=str(user_id))
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

        success = db_restore_digest(digest_id=str(digest_id), user_id=str(user_id))

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

        success = db_archive_digest(digest_id=str(digest_id), user_id=str(user_id))

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

        success = db_unarchive_digest(digest_id=str(digest_id), user_id=str(user_id))

        if success:
            return jsonify({"status": "success", "message": "Digest unarchived successfully", "unarchived": True})
        else:
            return jsonify({"status": "error", "message": "Digest not found, not archived, or access denied"}), 404

    except Exception as e:
        logger.error(f"Ошибка разархивирования дайджеста {digest_id}: {e}")
        return jsonify({"status": "error", "message": f"Ошибка разархивирования дайджеста: {str(e)}"}), 500


@api_bp.route("/users/by-telegram-id/<int:telegram_id>", methods=["GET"])
def get_user_by_telegram_id(telegram_id):
    """Get user_id by telegram_id for Telegram WebApp integration."""
    try:
        from database.db_models import supabase

        if not supabase:
            return jsonify({"status": "error", "message": "Database not initialized"}), 500

        # Ищем пользователя по telegram_id
        result = supabase.table("users").select("id, username, locale").eq("telegram_id", telegram_id).execute()

        if result.data:
            user_data = result.data[0]
            logger.info(f"User found by telegram_id {telegram_id}: {user_data['id']}")

            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "user_id": user_data["id"],
                        "telegram_id": telegram_id,
                        "username": user_data.get("username"),
                        "locale": user_data.get("locale", "ru"),
                    },
                }
            )
        else:
            logger.warning(f"User not found by telegram_id: {telegram_id}")
            return jsonify({"status": "error", "message": "User not found", "code": "USER_NOT_FOUND"}), 404

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


__all__ = ["api_bp"]
