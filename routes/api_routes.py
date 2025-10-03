"""
API Routes for PulseAI WebApp
Handles subscriptions and user data management

Categories are centralized in digests/configs.py and imported here
to maintain consistency across the application.
"""

import logging

from flask import Blueprint, request, jsonify

from digests.configs import CATEGORIES

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")


def convert_to_uuid(user_id_input):
    """Convert various user ID formats to UUID string."""
    if isinstance(user_id_input, str):
        # If it looks like a UUID, return as-is
        if len(user_id_input) == 36 and user_id_input.count("-") == 4:
            return user_id_input
        # Otherwise assume it's a Telegram ID (for demo users)
        return f"demo-user-{user_id_input}"
    else:
        # Assume it's already a UUID (for direct API calls)
        return user_id_input


# Convert to API format with descriptions
def get_subscription_categories():
    """Convert centralized categories to API format"""
    category_descriptions = {
        'crypto': 'Latest cryptocurrency news and market updates',
        'economy': 'Economic analysis and financial market insights',
        'world': 'Global news and international developments',
    }

    return [
        {
            'id': category_id,
            'name': category_label,
            'description': category_descriptions.get(
                category_id, f'News about {category_label.lower()}'
            ),
        }
        for category_id, category_label in CATEGORIES.items()
    ]


SUBSCRIPTION_CATEGORIES = get_subscription_categories()


@api_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """
    GET /api/subscriptions?user_id=<id>
    Returns user's subscription status for all categories.
    """
    user_id_input = request.args.get('user_id')
    if not user_id_input:
        return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

    try:
        # Convert to UUID if needed (for future use)
        _ = convert_to_uuid(user_id_input)

        # For demo purposes, return empty subscriptions
        # TODO: Implement actual database calls
        subscribed_categories = set()

        # Build response with all categories and their status
        categories_with_status = []
        for category in SUBSCRIPTION_CATEGORIES:
            categories_with_status.append(
                {
                    'id': category['id'],
                    'name': category['name'],
                    'description': category['description'],
                    'subscribed': category['id'] in subscribed_categories,
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
        logger.error('Error fetching subscriptions for user %s: %s', user_id_input, e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@api_bp.route('/subscriptions/update', methods=['POST'])
def update_subscription():
    """
    POST /api/subscriptions/update
    Updates user's subscription status for a category.
    Body: {"user_id": "uuid", "category": "crypto", "enabled": true}
    """
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

    data = request.get_json()
    user_id = data.get('user_id')
    category = data.get('category')
    enabled = data.get('enabled')

    if not user_id or not category or enabled is None:
        return (
            jsonify(
                {
                    'status': 'error',
                    'message': 'user_id, category, and enabled are required',
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
                    'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                }
            ),
            400,
        )

    try:
        # Convert to UUID if needed
        user_id = convert_to_uuid(user_id)

        # For demo purposes, just return success
        # TODO: Implement actual database calls
        if enabled:
            return jsonify(
                {
                    'status': 'success',
                    'message': f'Successfully subscribed to {category}',
                    'data': {'category': category, 'subscribed': True},
                }
            )
        else:
            return jsonify(
                {
                    'status': 'success',
                    'message': f'Successfully unsubscribed from {category}',
                    'data': {'category': category, 'subscribed': False},
                }
            )

    except Exception as e:
        logger.error('Error updating subscription: %s', e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    GET /api/notifications?user_id=<id>
    Returns list of notifications for user.
    """
    user_id_input = request.args.get('user_id')
    if not user_id_input:
        return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

    try:
        # Convert to UUID if needed (for future use)
        _ = convert_to_uuid(user_id_input)

        # For demo purposes, return empty notifications
        # TODO: Implement actual database calls
        notifications = []

        return jsonify(
            {
                'status': 'success',
                'data': {
                    'notifications': notifications,
                    'total_count': 0,
                    'unread_count': 0,
                },
            }
        )

    except Exception as e:
        logger.error('Error fetching notifications for user %s: %s', user_id_input, e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@api_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notification_read_endpoint():
    """
    POST /api/notifications/mark-read
    Marks a notification as read.
    TODO: Implement mark_notification_read function in db_models
    """
    return jsonify({'status': 'error', 'message': 'Not implemented yet'}), 501


@api_bp.route('/notification-settings', methods=['GET'])
def get_notification_settings():
    """
    GET /api/notification-settings?user_id=<id>
    Returns user's notification settings for all categories.
    TODO: Implement get_notification_settings function in db_models
    """
    return jsonify({'status': 'error', 'message': 'Not implemented yet'}), 501


@api_bp.route('/notification-settings/update', methods=['POST'])
def update_notification_settings():
    """
    POST /api/notification-settings/update
    Updates user's notification settings.
    TODO: Implement upsert_notification_setting function in db_models
    """
    return jsonify({'status': 'error', 'message': 'Not implemented yet'}), 501


@api_bp.route('/users', methods=['POST'])
def create_user():
    """
    POST /api/users
    Creates a new user or returns existing user.
    Body: {"telegram_id": 123456789, "username": "optional"}
    """
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'JSON body is required'}), 400

    data = request.get_json()
    telegram_id = data.get('telegram_id')
    username = data.get('username')

    if not telegram_id:
        return jsonify({'status': 'error', 'message': 'telegram_id is required'}), 400

    try:
        # For demo purposes, just return a mock user ID
        # TODO: Implement actual database calls
        user_id = f"user-{telegram_id}"

        return jsonify(
            {
                'status': 'success',
                'message': 'User created or retrieved successfully',
                'data': {
                    'user_id': user_id,
                    'telegram_id': telegram_id,
                    'username': username,
                },
            }
        )

    except Exception as e:
        logger.error('Error creating user: %s', e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """GET /api/health - Health check endpoint"""
    return jsonify(
        {
            'status': 'success',
            'message': 'PulseAI API is healthy',
            'version': '1.0.0',
        }
    )


__all__ = ['api_bp']
