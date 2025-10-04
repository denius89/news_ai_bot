#!/usr/bin/env python3
"""
Debug API issue by testing the exact same logic.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from database.db_models import get_user_notifications, get_user_by_telegram

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def debug_api_logic():
    """Debug the exact same logic used in API."""
    load_dotenv()

    print("🔍 Debugging API logic...")

    # Simulate the exact same logic from API
    user_id_input = "123"
    limit = 10
    offset = 0

    print(f"Input: user_id_input='{user_id_input}', limit={limit}, offset={offset}")

    try:
        # Convert user_id - try UUID format first, then fallback to int
        if len(user_id_input) == 36 and user_id_input.count('-') == 4:
            # It's a UUID
            user_id = user_id_input
            print(f"Using UUID directly: {user_id}")
        else:
            try:
                # Try to convert to int and then get UUID from users table
                telegram_id = int(user_id_input)
                print(f"Converting telegram_id to UUID: {telegram_id}")
                # Get UUID from users table
                user_data = get_user_by_telegram(telegram_id)
                if user_data:
                    user_id = user_data['id']
                    print(f"Found user data: {user_data}")
                else:
                    # Use first user as fallback
                    user_id = 'f7d38911-4e62-4012-a9bf-2aaa03483497'  # First user from our check
                    print(f"User not found, using fallback: {user_id}")
            except ValueError:
                # Use first user as fallback
                user_id = 'f7d38911-4e62-4012-a9bf-2aaa03483497'
                print(f"Invalid user_id format, using fallback: {user_id}")

        print(f"Final user_id for query: {user_id}")

        # Get notifications from database
        print(f"Calling get_user_notifications with user_id={user_id}, limit={limit}")
        notifications = get_user_notifications(user_id=user_id, limit=limit, offset=offset)
        print(f"get_user_notifications returned {len(notifications)} notifications")

        # Show notifications
        for i, notification in enumerate(notifications):
            print(f"  {i+1}. {notification['title']} (read: {notification['read']})")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Debugging API logic...")
    print("=" * 50)

    success = debug_api_logic()

    print("=" * 50)
    if success:
        print("✅ Debug completed!")
        sys.exit(0)
    else:
        print("❌ Debug failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
