"""
API Routes for PulseAI WebApp
Handles subscriptions and user data management

Categories are centralized in digests/configs.py and imported here
to maintain consistency across the application.
"""

import asyncio
import logging

from flask import Blueprint, request, jsonify

from database.db_models import (
    get_user_notifications,
    mark_notification_read,
    get_notification_settings,
    upsert_notification_setting,
    # create_notification  # unused for now
)
from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService
from digests.configs import CATEGORIES

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
subscription_service = SubscriptionService()
notification_service = NotificationService()


async def resolve_user_id(user_id_input: str) -> str:
    """
    Resolve user ID from different input formats:
    - 'demo-user-123' -> creates demo user and returns UUID
    - '123456789' (numeric string) -> creates/gets Telegram user and returns UUID
    - 'uuid-string' -> returns as-is (already a UUID)

    Returns: UUID string for database operations
    """
    if user_id_input == 'demo-user-123':
        # Demo user fallback for development
        return await subscription_service.get_or_create_user(123, 'demo_user')
    elif user_id_input.isdigit():
        # Real Telegram user ID (numeric string)
        telegram_id = int(user_id_input)
        return await subscription_service.get_or_create_user(telegram_id, None)
    else:
        # Assume it's already a UUID (for direct API calls)
        return user_id_input


# Import centralized categories (already imported above)


# Convert to API format with descriptions
def get_subscription_categories():
    """Convert centralized categories to API format"""
    category_descriptions = {
        'crypto': 'Latest cryptocurrency news and market updates',
        'economy': 'Economic analysis and financial market insights',
        'world': 'Global news and international developments',
        'technology': 'Technology innovations and industry updates',
        'politics': 'Political news and government developments',
    }

    return [
        {
            'id': category_id,
            'title': category_label.replace('📊 ', '')
            .replace('💰 ', '')
            .replace('🌍 ', '')
            .replace('⚙️ ', '')
            .replace('🏛️ ', ''),
            'description': category_descriptions.get(
                category_id, f'{category_label} news and updates'
            ),
        }
        for category_id, category_label in CATEGORIES.items()
    ]


SUBSCRIPTION_CATEGORIES = get_subscription_categories()


@api_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """
    Get user subscriptions
    Query params: user_id (required)
    Returns: JSON with categories and subscription status
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

        logger.info(f"📋 Getting subscriptions for user: {user_id}")

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Get user subscriptions from database
            user_subscriptions = asyncio.run(subscription_service.list(user_id))
            subscribed_categories = {sub['category'] for sub in user_subscriptions}
        except Exception as e:
            logger.error(f"❌ Error getting user subscriptions: {str(e)}")
            # Return empty subscriptions if user doesn't exist
            user_subscriptions = []
            subscribed_categories = set()

        # Build response with all categories and their status
        categories_with_status = []
        for category in SUBSCRIPTION_CATEGORIES:
            categories_with_status.append(
                {
                    'id': category['id'],
                    'title': category['title'],
                    'description': category['description'],
                    'enabled': category['id'] in subscribed_categories,
                }
            )

        return jsonify(
            {
                'status': 'success',
                'data': {
                    'categories': categories_with_status,
                    'total_subscriptions': len(subscribed_categories),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Error getting subscriptions: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get subscriptions'}), 500


@api_bp.route('/subscriptions/update', methods=['POST'])
def update_subscription():
    """
    Update user subscription
    Body: JSON { user_id, category, enabled }
    Returns: JSON with status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

        user_id = data.get('user_id')
        category = data.get('category')
        enabled = data.get('enabled')

        if not all([user_id, category, enabled is not None]):
            return (
                jsonify(
                    {
                        'status': 'error',
                        'message': 'user_id, category, and enabled fields are required',
                    }
                ),
                400,
            )

        # Validate category
        valid_categories = [cat['id'] for cat in SUBSCRIPTION_CATEGORIES]
        if category not in valid_categories:
            return (
                jsonify(
                    {
                        'status': 'error',
                        'message': f'Invalid category. Valid categories: {valid_categories}',
                    }
                ),
                400,
            )

        logger.info(
            f"🔄 Updating subscription: user={user_id}, category={category}, enabled={enabled}"
        )

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Update subscription in database
            if enabled:
                success = asyncio.run(subscription_service.add(user_id, category))
                action = 'subscribed to'
            else:
                removed_count = asyncio.run(subscription_service.remove(user_id, category))
                success = removed_count > 0
                action = 'unsubscribed from'
        except Exception as e:
            logger.error(f"❌ Error updating subscription: {str(e)}")
            success = False
            action = 'failed to update'

        if success:
            logger.info(f"✅ User {user_id} {action} {category}")
            return jsonify(
                {
                    'status': 'success',
                    'message': f'Successfully {action} {category}',
                    'data': {'user_id': user_id, 'category': category, 'enabled': enabled},
                }
            )
        else:
            logger.warning(f"⚠️ Failed to update subscription: user={user_id}, category={category}")
            return jsonify({'status': 'error', 'message': 'Failed to update subscription'}), 500

    except Exception as e:
        logger.error(f"❌ Error updating subscription: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to update subscription'}), 500


@api_bp.route('/user/create', methods=['POST'])
def create_user():
    """
    Create or get user by telegram_id
    Body: JSON { telegram_id, username? }
    Returns: JSON with user_id
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

        telegram_id = data.get('telegram_id')
        username = data.get('username')

        if not telegram_id:
            return jsonify({'status': 'error', 'message': 'telegram_id is required'}), 400

        logger.info(f"👤 Creating/getting user: telegram_id={telegram_id}, username={username}")

        # Create or get user
        import asyncio

        user_id = asyncio.run(subscription_service.get_or_create_user(telegram_id, username))

        return jsonify(
            {
                'status': 'success',
                'data': {'user_id': user_id, 'telegram_id': telegram_id, 'username': username},
            }
        )

    except Exception as e:
        logger.error(f"❌ Error creating user: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to create user'}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({'status': 'success', 'message': 'PulseAI API is healthy', 'version': '1.0.0'})


# --- NOTIFICATIONS ENDPOINTS ---


@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Get user notifications
    Query params: user_id (required), limit (optional, default 50)
    Returns: JSON with notifications list
    """
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))

        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

        logger.info(f"📬 Getting notifications for user: {user_id}")

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Get user notifications from database
            notifications = get_user_notifications(user_id, limit)

            # Count unread notifications
            unread_count = sum(1 for n in notifications if not n.get('read', True))

            return jsonify(
                {
                    'status': 'success',
                    'data': {
                        'notifications': notifications,
                        'total_count': len(notifications),
                        'unread_count': unread_count,
                    },
                }
            )

        except Exception as e:
            logger.error(f"❌ Error getting notifications: {str(e)}")
            return jsonify(
                {
                    'status': 'success',
                    'data': {'notifications': [], 'total_count': 0, 'unread_count': 0},
                }
            )

    except Exception as e:
        logger.error(f"❌ Error getting notifications: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get notifications'}), 500


@api_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notification_as_read():
    """
    Mark notification as read
    Body: JSON { user_id, notification_id }
    Returns: JSON with status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

        user_id = data.get('user_id')
        notification_id = data.get('notification_id')

        if not all([user_id, notification_id]):
            return (
                jsonify({'status': 'error', 'message': 'user_id and notification_id are required'}),
                400,
            )

        logger.info(
            f"📖 Marking notification as read: user={user_id}, notification={notification_id}"
        )

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Mark notification as read
            success = mark_notification_read(user_id, notification_id)

            if success:
                return jsonify(
                    {
                        'status': 'success',
                        'message': 'Notification marked as read',
                        'data': {'user_id': user_id, 'notification_id': notification_id},
                    }
                )
            else:
                return (
                    jsonify(
                        {'status': 'error', 'message': 'Notification not found or access denied'}
                    ),
                    404,
                )

        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {str(e)}")
            return (
                jsonify({'status': 'error', 'message': 'Failed to mark notification as read'}),
                500,
            )

    except Exception as e:
        logger.error(f"❌ Error marking notification as read: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to mark notification as read'}), 500


@api_bp.route('/notification-settings', methods=['GET'])
def get_notification_settings_api():
    """
    Get user notification settings
    Query params: user_id (required)
    Returns: JSON with categories and notification settings
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

        logger.info(f"⚙️ Getting notification settings for user: {user_id}")

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Get user notification settings from database
            user_settings = get_notification_settings(user_id)
            settings_dict = {setting['category']: setting for setting in user_settings}

            # Build response with all categories and their settings
            categories_with_settings = []
            for category in SUBSCRIPTION_CATEGORIES:
                category_id = category['id']
                setting = settings_dict.get(
                    category_id, {'enabled': False, 'via_telegram': True, 'via_webapp': True}
                )

                categories_with_settings.append(
                    {
                        'id': category_id,
                        'title': category['title'],
                        'description': category['description'],
                        'enabled': setting.get('enabled', False),
                        'via_telegram': setting.get('via_telegram', True),
                        'via_webapp': setting.get('via_webapp', True),
                    }
                )

            return jsonify({'status': 'success', 'data': {'categories': categories_with_settings}})

        except Exception as e:
            logger.error(f"❌ Error getting notification settings: {str(e)}")
            # Return default settings if error
            categories_with_settings = []
            for category in SUBSCRIPTION_CATEGORIES:
                categories_with_settings.append(
                    {
                        'id': category['id'],
                        'title': category['title'],
                        'description': category['description'],
                        'enabled': True,
                        'via_telegram': True,
                        'via_webapp': True,
                    }
                )

            return jsonify({'status': 'success', 'data': {'categories': categories_with_settings}})

    except Exception as e:
        logger.error(f"❌ Error getting notification settings: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get notification settings'}), 500


@api_bp.route('/notification-settings/update', methods=['POST'])
def update_notification_settings():
    """
    Update user notification settings
    Body: JSON { user_id, category, enabled, via_telegram, via_webapp }
    Returns: JSON with status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

        user_id = data.get('user_id')
        category = data.get('category')
        enabled = data.get('enabled')
        via_telegram = data.get('via_telegram')
        via_webapp = data.get('via_webapp')

        if not all(
            [
                user_id,
                category,
                enabled is not None,
                via_telegram is not None,
                via_webapp is not None,
            ]
        ):
            return (
                jsonify(
                    {
                        'status': 'error',
                        'message': 'user_id, category, enabled, via_telegram, and via_webapp fields are required',
                    }
                ),
                400,
            )

        # Validate category
        valid_categories = [cat['id'] for cat in SUBSCRIPTION_CATEGORIES]
        if category not in valid_categories:
            return (
                jsonify(
                    {
                        'status': 'error',
                        'message': f'Invalid category. Valid categories: {valid_categories}',
                    }
                ),
                400,
            )

        logger.info(
            f"⚙️ Updating notification settings: user={user_id}, category={category}, enabled={enabled}"
        )

        # Resolve user ID (handles demo users, Telegram IDs, and UUIDs)
        try:
            user_id = asyncio.run(resolve_user_id(user_id))

            # Update notification settings in database
            success = upsert_notification_setting(
                user_id, category, enabled, via_telegram, via_webapp
            )

            if success:
                logger.info(
                    f"✅ Notification settings updated: user={user_id}, category={category}"
                )
                return jsonify(
                    {
                        'status': 'success',
                        'message': f'Notification settings updated for {category}',
                        'data': {
                            'user_id': user_id,
                            'category': category,
                            'enabled': enabled,
                            'via_telegram': via_telegram,
                            'via_webapp': via_webapp,
                        },
                    }
                )
            else:
                logger.warning(
                    f"⚠️ Failed to update notification settings: user={user_id}, category={category}"
                )
                return (
                    jsonify(
                        {'status': 'error', 'message': 'Failed to update notification settings'}
                    ),
                    500,
                )

        except Exception as e:
            logger.error(f"❌ Error updating notification settings: {str(e)}")
            return (
                jsonify({'status': 'error', 'message': 'Failed to update notification settings'}),
                500,
            )

    except Exception as e:
        logger.error(f"❌ Error updating notification settings: {str(e)}")
        return (
            jsonify({'status': 'error', 'message': 'Failed to update notification settings'}),
            500,
        )
